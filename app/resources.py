from __future__ import annotations

import copy
import ctypes
import os
import subprocess
import threading
import time
from ctypes import wintypes


def _filetime_value(value: wintypes.FILETIME) -> int:
    return (value.dwHighDateTime << 32) | value.dwLowDateTime


def _memory_metric(used_mib: float, total_mib: float) -> dict[str, float]:
    percent = (used_mib / total_mib * 100) if total_mib else 0.0
    return {
        "used_gib": round(used_mib / 1024, 1),
        "total_gib": round(total_mib / 1024, 1),
        "percent": round(percent, 1),
    }


if os.name == "nt":
    class _MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]


    class _PdhValueUnion(ctypes.Union):
        _fields_ = [
            ("long_value", wintypes.LONG),
            ("double_value", ctypes.c_double),
            ("large_value", ctypes.c_longlong),
        ]


    class _PdhFormattedValue(ctypes.Structure):
        _fields_ = [("status", wintypes.DWORD), ("value", _PdhValueUnion)]


class _WindowsDiskCounters:
    _FORMAT_DOUBLE = 0x00000200

    def __init__(self) -> None:
        if os.name != "nt":
            raise RuntimeError("Windows performance counters are unavailable")
        self._pdh = ctypes.WinDLL("pdh", use_last_error=True)
        self._pdh.PdhOpenQueryW.argtypes = [wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(wintypes.HANDLE)]
        self._pdh.PdhOpenQueryW.restype = wintypes.LONG
        self._pdh.PdhAddEnglishCounterW.argtypes = [wintypes.HANDLE, wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(wintypes.HANDLE)]
        self._pdh.PdhAddEnglishCounterW.restype = wintypes.LONG
        self._pdh.PdhCollectQueryData.argtypes = [wintypes.HANDLE]
        self._pdh.PdhCollectQueryData.restype = wintypes.LONG
        self._pdh.PdhGetFormattedCounterValue.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(_PdhFormattedValue)]
        self._pdh.PdhGetFormattedCounterValue.restype = wintypes.LONG
        self._pdh.PdhCloseQuery.argtypes = [wintypes.HANDLE]
        self._pdh.PdhCloseQuery.restype = wintypes.LONG

        self._query = wintypes.HANDLE()
        self._read = wintypes.HANDLE()
        self._write = wintypes.HANDLE()
        self._warmed = False
        self._check(self._pdh.PdhOpenQueryW(None, 0, ctypes.byref(self._query)))
        try:
            self._check(self._pdh.PdhAddEnglishCounterW(
                self._query, r"\PhysicalDisk(_Total)\Disk Read Bytes/sec", 0, ctypes.byref(self._read)
            ))
            self._check(self._pdh.PdhAddEnglishCounterW(
                self._query, r"\PhysicalDisk(_Total)\Disk Write Bytes/sec", 0, ctypes.byref(self._write)
            ))
        except Exception:
            self.close()
            raise

    @staticmethod
    def _check(status: int) -> None:
        if status != 0:
            raise OSError(f"Windows performance counter error 0x{status & 0xFFFFFFFF:08X}")

    def sample(self) -> tuple[float, float]:
        self._check(self._pdh.PdhCollectQueryData(self._query))
        if not self._warmed:
            self._warmed = True
            return 0.0, 0.0
        return self._value(self._read), self._value(self._write)

    def _value(self, counter: wintypes.HANDLE) -> float:
        value = _PdhFormattedValue()
        self._check(self._pdh.PdhGetFormattedCounterValue(
            counter, self._FORMAT_DOUBLE, None, ctypes.byref(value)
        ))
        return max(0.0, float(value.value.double_value))

    def close(self) -> None:
        if getattr(self, "_query", None):
            self._pdh.PdhCloseQuery(self._query)
            self._query = None


class ResourceMonitor:
    def __init__(self, interval_seconds: float = 2.0) -> None:
        self._interval = max(0.5, interval_seconds)
        self._lock = threading.Lock()
        self._started = False
        self._snapshot = self._empty_snapshot()
        self._previous_cpu = self._cpu_times()
        self._disk_counters = None

    @staticmethod
    def _empty_snapshot() -> dict:
        return {
            "available": False,
            "cpu_percent": None,
            "ram": None,
            "disk": None,
            "gpu_percent": None,
            "vram": None,
        }

    def snapshot(self) -> dict:
        self._ensure_started()
        with self._lock:
            return copy.deepcopy(self._snapshot)

    def _ensure_started(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
        self._update()
        threading.Thread(target=self._run, name="resource-monitor", daemon=True).start()

    def _run(self) -> None:
        while True:
            time.sleep(self._interval)
            self._update()

    def _update(self) -> None:
        sample = self._collect()
        with self._lock:
            self._snapshot = sample

    def _collect(self) -> dict:
        cpu_percent, ram = self._cpu_and_ram()
        disk = self._disk()
        gpu_percent, vram = self._gpu_and_vram()
        return {
            "available": any(value is not None for value in (cpu_percent, ram, disk, gpu_percent, vram)),
            "cpu_percent": cpu_percent,
            "ram": ram,
            "disk": disk,
            "gpu_percent": gpu_percent,
            "vram": vram,
        }

    @staticmethod
    def _cpu_times() -> tuple[int, int, int] | None:
        if os.name != "nt":
            return None
        idle = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        try:
            if not ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
            ):
                return None
        except (AttributeError, OSError):
            return None
        return _filetime_value(idle), _filetime_value(kernel), _filetime_value(user)

    def _cpu_and_ram(self) -> tuple[float | None, dict | None]:
        current_cpu = self._cpu_times()
        cpu_percent = None
        if current_cpu and self._previous_cpu:
            idle_delta = current_cpu[0] - self._previous_cpu[0]
            total_delta = (current_cpu[1] - self._previous_cpu[1]) + (current_cpu[2] - self._previous_cpu[2])
            if total_delta > 0:
                cpu_percent = round(max(0.0, min(100.0, (total_delta - idle_delta) / total_delta * 100)), 1)
        self._previous_cpu = current_cpu

        if os.name != "nt":
            return cpu_percent, None
        status = _MemoryStatusEx()
        status.length = ctypes.sizeof(status)
        try:
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return cpu_percent, None
        except (AttributeError, OSError):
            return cpu_percent, None
        mib = 1024 * 1024
        used_mib = (status.total_physical - status.available_physical) / mib
        return cpu_percent, _memory_metric(used_mib, status.total_physical / mib)

    def _disk(self) -> dict[str, float] | None:
        if os.name != "nt":
            return None
        try:
            if self._disk_counters is None:
                self._disk_counters = _WindowsDiskCounters()
            read_bytes, write_bytes = self._disk_counters.sample()
            scale = 1024 * 1024
            return {
                "read_mb_s": round(read_bytes / scale, 1),
                "write_mb_s": round(write_bytes / scale, 1),
            }
        except (OSError, RuntimeError):
            return None

    @staticmethod
    def _gpu_and_vram() -> tuple[float | None, dict | None]:
        try:
            output = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                text=True,
                errors="replace",
                timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            utilization_text, used_text, total_text = output.splitlines()[0].split(",", 2)
            used_mib = float(used_text.strip())
            total_mib = float(total_text.strip())
            return round(float(utilization_text.strip()), 1), _memory_metric(used_mib, total_mib)
        except (OSError, subprocess.SubprocessError, ValueError, IndexError):
            return None, None
