"""Property-based tests for the scoring math (Saba, Step 4).

These complement the example-based assertions in test_scorer.py: instead of a
handful of fixed inputs, Hypothesis generates thousands of signal breakdowns and
checks that the *invariants* of the scorer hold across the whole input space.

Invariants under test:
  * authenticity score is always clamped to [0, 1]
  * the score is a convex combination of the four signals (weights sum to 1),
    so it can never exceed the largest signal nor fall below the smallest
  * status mapping is monotonic and consistent with the published thresholds
  * the score is monotonic non-decreasing in every individual signal
"""

import math

from hypothesis import given
from hypothesis import strategies as st

from scoring.constants import (
    THRESHOLD_COMPLIANT,
    THRESHOLD_NON_COMPLIANT,
    WA,
    WM,
    WP,
    WV,
)
from scoring.models import ComplianceStatus, SignalBreakdown
from scoring.scorer import compute_authenticity_score, map_compliance_status

# A signal value is any float in [0, 1]; reject NaN/inf so we test real inputs.
signal = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


def _breakdown(m: float, a: float, v: float, p: float) -> SignalBreakdown:
    return SignalBreakdown(m=m, a=a, v=v, p=p)


def test_weights_sum_to_one():
    # The convexity arguments below only hold if the weights are a partition.
    assert math.isclose(WM + WA + WV + WP, 1.0)


@given(m=signal, a=signal, v=signal, p=signal)
def test_score_always_in_unit_interval(m, a, v, p):
    score = compute_authenticity_score(_breakdown(m, a, v, p))
    assert 0.0 <= score <= 1.0


@given(m=signal, a=signal, v=signal, p=signal)
def test_score_bounded_by_min_and_max_signal(m, a, v, p):
    # A weighted average with non-negative weights summing to 1 lies between the
    # smallest and largest of its inputs.
    score = compute_authenticity_score(_breakdown(m, a, v, p))
    lo, hi = min(m, a, v, p), max(m, a, v, p)
    assert lo - 1e-9 <= score <= hi + 1e-9


@given(x=signal)
def test_uniform_signals_pass_through(x):
    # If every signal is x, the weighted average is exactly x.
    assert math.isclose(
        compute_authenticity_score(_breakdown(x, x, x, x)), x, abs_tol=1e-9
    )


@given(
    m=signal,
    a=signal,
    v=signal,
    p=signal,
    delta=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
)
def test_score_monotonic_in_metadata_signal(m, a, v, p, delta):
    # Raising any one signal must not lower the score (monotonicity).
    higher_m = min(1.0, m + delta)
    base = compute_authenticity_score(_breakdown(m, a, v, p))
    bumped = compute_authenticity_score(_breakdown(higher_m, a, v, p))
    assert bumped >= base - 1e-9


@given(
    score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_status_mapping_is_total_and_consistent(score):
    status = map_compliance_status(score)
    if score < THRESHOLD_NON_COMPLIANT:
        assert status == ComplianceStatus.NON_COMPLIANT
    elif score < THRESHOLD_COMPLIANT:
        assert status == ComplianceStatus.REVIEW
    else:
        assert status == ComplianceStatus.COMPLIANT


@given(
    lower=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
    higher=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
)
def test_status_is_monotonic_in_score(lower, higher):
    # A higher score is never *less* compliant than a lower one.
    if lower > higher:
        lower, higher = higher, lower
    rank = {
        ComplianceStatus.NON_COMPLIANT: 0,
        ComplianceStatus.REVIEW: 1,
        ComplianceStatus.COMPLIANT: 2,
    }
    assert rank[map_compliance_status(higher)] >= rank[map_compliance_status(lower)]
