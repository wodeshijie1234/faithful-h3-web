from dataclasses import dataclass


@dataclass(frozen=True)
class AccelerationPlan:
    tier: str
    recommended_model: str
    install_triton: bool
    requires_self_test: bool
    reason: str


def recommend_model_from_vram(raw: str, threshold_mib: int = 16000) -> str:
    values = []
    for line in str(raw or "").splitlines():
        try:
            values.append(int(line.strip()))
        except ValueError:
            continue
    return "9b" if values and max(values) >= threshold_mib else "4b"


def acceleration_plan(*, platform: str, python: tuple[int, int], capability: tuple[int, int], vram_gib: float) -> AccelerationPlan:
    modern_gpu = capability >= (8, 0)
    recommended = "9b" if vram_gib >= 16 else "4b"
    if platform.casefold() == "windows" and python >= (3, 11) and modern_gpu:
        return AccelerationPlan("accelerated", recommended, True, True, "Acceleration requires an import and inference self-test.")
    if modern_gpu:
        return AccelerationPlan("stable", recommended, False, False, "Use the stable CUDA backend for this environment.")
    return AccelerationPlan("compatible", "4b", False, False, "Use the compatible backend on pre-Ampere GPUs.")
