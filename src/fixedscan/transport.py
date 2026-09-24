"""Small executable checks for rounding transport and carry composition."""
from __future__ import annotations
from .checker_arithmetic import round_div


def residual(n: int, scale: int, mode: str) -> int:
    return scale * round_div(n, scale, mode) - n


def translation_modulus(scale: int, mode: str) -> int:
    return scale if mode == "floor" else 2 * scale


def verify_translation(scale: int, mode: str, radius: int = 256) -> bool:
    modulus = translation_modulus(scale, mode)
    return all(residual(n + modulus, scale, mode) == residual(n, scale, mode)
               for n in range(-radius, radius + 1))


def nearest_even_scale_counterexample(scale: int) -> tuple[int, int]:
    """Return n and n+scale whose RNE residuals differ (scale must be even)."""
    if scale % 2:
        raise ValueError("binary fixed-point scale is even except q=1")
    n = scale // 2
    assert residual(n, scale, "rne") != residual(n + scale, scale, "rne")
    return n, n + scale
