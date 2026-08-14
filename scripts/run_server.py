from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import threading
from ctypes import wintypes


_CREATE_SUSPENDED = 0x00000004


if os.name == "nt":
    class _IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]


    class _BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]


    class _ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BasicLimitInformation),
            ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]


class WindowsKillOnCloseJob:
    _EXTENDED_LIMIT_INFORMATION = 9
    _KILL_ON_JOB_CLOSE = 0x00002000

    def __init__(self) -> None:
        if os.name != "nt":
            raise RuntimeError("Windows Job Objects are only available on Windows")

        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self._kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        self._kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self._kernel32.SetInformationJobObject.restype = wintypes.BOOL
        self._kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self._kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self._kernel32.CloseHandle.restype = wintypes.BOOL

        self._lock = threading.Lock()
        self._handle = self._kernel32.CreateJobObjectW(None, None)
        if not self._handle:
            raise ctypes.WinError(ctypes.get_last_error())

        limits = _ExtendedLimitInformation()
        limits.BasicLimitInformation.LimitFlags = self._KILL_ON_JOB_CLOSE
        if not self._kernel32.SetInformationJobObject(
            self._handle,
            self._EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, process) -> None:
        with self._lock:
            if not self._handle:
                raise RuntimeError("The process job is already closed")
            if not self._kernel32.AssignProcessToJobObject(self._handle, process._handle):
                raise ctypes.WinError(ctypes.get_last_error())

    def close(self) -> None:
        with self._lock:
            if self._handle:
                self._kernel32.CloseHandle(self._handle)
                self._handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def _resume_process(process: subprocess.Popen) -> None:
    ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
    ntdll.NtResumeProcess.argtypes = [wintypes.HANDLE]
    ntdll.NtResumeProcess.restype = ctypes.c_long
    status = ntdll.NtResumeProcess(process._handle)
    if status != 0:
        raise OSError(f"Unable to resume the server process (NTSTATUS 0x{status & 0xFFFFFFFF:08X})")


def _install_console_close_handler(job: WindowsKillOnCloseJob):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handler_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

    @handler_type
    def handler(control_type):
        if control_type in {0, 1, 2, 5, 6}:
            job.close()
            return True
        return False

    kernel32.SetConsoleCtrlHandler.argtypes = [handler_type, wintypes.BOOL]
    kernel32.SetConsoleCtrlHandler.restype = wintypes.BOOL
    if not kernel32.SetConsoleCtrlHandler(handler, True):
        raise ctypes.WinError(ctypes.get_last_error())
    return kernel32, handler


def run_server(host: str, port: int) -> int:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    creation_flags = _CREATE_SUSPENDED | subprocess.CREATE_NEW_PROCESS_GROUP
    process = subprocess.Popen(command, creationflags=creation_flags)
    kernel32 = None
    handler = None

    with WindowsKillOnCloseJob() as job:
        try:
            job.assign(process)
            _resume_process(process)
            kernel32, handler = _install_console_close_handler(job)
            return process.wait()
        finally:
            if kernel32 is not None and handler is not None:
                kernel32.SetConsoleCtrlHandler(handler, False)
            if process.poll() is None:
                job.close()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Faithful H3 with Windows process cleanup")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=7868, type=int)
    args = parser.parse_args()
    return run_server(args.host, args.port)


if __name__ == "__main__":
    raise SystemExit(main())
