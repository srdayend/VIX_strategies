import pytest

from vix_strategies.thesis.curve import (
    CurvePoint,
    LocalCurve,
    build_local_curve,
    curve_price_at_dte,
)


def test_curve_price_is_exact_at_vix_and_futures_anchors():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=21.0)],
    )

    assert curve_price_at_dte(curve, 0.0) == 15.0
    assert curve_price_at_dte(curve, 10.0) == 17.0
    assert curve_price_at_dte(curve, 40.0) == 21.0


def test_curve_interpolates_linearly_between_vix_m1_and_m1_m2():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=21.0)],
    )

    assert curve_price_at_dte(curve, 5.0) == 16.0
    assert curve_price_at_dte(curve, 25.0) == 19.0


def test_direct_local_curve_requires_vix_anchor_at_zero_dte():
    with pytest.raises(ValueError, match="VIX anchor at dte 0"):
        LocalCurve(points=(CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=21.0)))


def test_direct_local_curve_requires_strictly_increasing_dte():
    with pytest.raises(ValueError, match="strictly increasing"):
        LocalCurve(
            points=(
                CurvePoint(dte=0.0, price=15.0),
                CurvePoint(dte=40.0, price=21.0),
                CurvePoint(dte=10.0, price=17.0),
            )
        )


def test_curve_rejects_unsorted_futures_dtes():
    with pytest.raises(ValueError, match="strictly increasing"):
        build_local_curve(
            vix_level=15.0,
            futures_points=[
                CurvePoint(dte=40.0, price=21.0),
                CurvePoint(dte=10.0, price=17.0),
            ],
        )


def test_curve_rejects_duplicate_futures_dtes():
    with pytest.raises(ValueError, match="strictly increasing"):
        build_local_curve(
            vix_level=15.0,
            futures_points=[
                CurvePoint(dte=10.0, price=17.0),
                CurvePoint(dte=10.0, price=18.0),
            ],
        )


def test_curve_rejects_target_dte_outside_local_curve_bounds():
    curve = build_local_curve(
        vix_level=15.0,
        futures_points=[CurvePoint(dte=10.0, price=17.0), CurvePoint(dte=40.0, price=21.0)],
    )

    with pytest.raises(ValueError, match="outside local curve bounds"):
        curve_price_at_dte(curve, -1.0)
    with pytest.raises(ValueError, match="outside local curve bounds"):
        curve_price_at_dte(curve, 41.0)


def test_curve_rejects_nonpositive_futures_dte():
    with pytest.raises(ValueError, match="futures DTE must be positive"):
        build_local_curve(
            vix_level=15.0,
            futures_points=[CurvePoint(dte=0.0, price=17.0)],
        )
