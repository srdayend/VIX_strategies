from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence, Tuple


@dataclass(frozen=True)
class CurvePoint:
    dte: float
    price: float

    def __post_init__(self) -> None:
        if not isfinite(self.dte):
            raise ValueError("DTE must be finite")
        if not isfinite(self.price) or self.price <= 0:
            raise ValueError("price must be positive and finite")


@dataclass(frozen=True)
class LocalCurve:
    points: Tuple[CurvePoint, ...]

    def __post_init__(self) -> None:
        if not self.points:
            raise ValueError("LocalCurve requires at least a VIX anchor and one futures point")
        if self.points[0].dte != 0:
            raise ValueError("LocalCurve requires a VIX anchor at dte 0")
        if len(self.points) < 2:
            raise ValueError("LocalCurve requires at least one futures point")

        last_dte = self.points[0].dte
        for point in self.points[1:]:
            if point.dte <= last_dte:
                raise ValueError("LocalCurve DTEs must be strictly increasing")
            last_dte = point.dte


def build_local_curve(vix_level: float, futures_points: Sequence[CurvePoint]) -> LocalCurve:
    if not isfinite(vix_level) or vix_level <= 0:
        raise ValueError("vix_level must be positive and finite")
    if not futures_points:
        raise ValueError("at least one futures point is required")

    last_dte = 0.0
    checked_points = []
    for point in futures_points:
        if point.dte <= 0:
            raise ValueError("futures DTE must be positive")
        if point.dte <= last_dte:
            raise ValueError("futures DTEs must be strictly increasing")
        checked_points.append(point)
        last_dte = point.dte

    return LocalCurve(points=(CurvePoint(dte=0.0, price=float(vix_level)), *checked_points))


def curve_price_at_dte(curve: LocalCurve, target_dte: float) -> float:
    if not isfinite(target_dte):
        raise ValueError("target_dte must be finite")

    points = curve.points
    lower_bound = points[0].dte
    upper_bound = points[-1].dte
    if target_dte < lower_bound or target_dte > upper_bound:
        raise ValueError("target_dte outside local curve bounds")

    for point in points:
        if target_dte == point.dte:
            return point.price

    for left, right in zip(points, points[1:]):
        if left.dte <= target_dte <= right.dte:
            weight = (target_dte - left.dte) / (right.dte - left.dte)
            return left.price + weight * (right.price - left.price)

    raise RuntimeError("target_dte passed bounds validation but no segment was found")
