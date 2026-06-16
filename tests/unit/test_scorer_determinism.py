"""Determinism tests for the scoring layer (Saba, Step 4).

The compliance score has to be reproducible: the same media must always yield
the same score, breakdown, and status. These tests pin that down for the pure
scoring math (no model weights, no I/O) so a regression that introduces
non-determinism — e.g. iterating a set, an unseeded RNG, dict ordering — fails
loudly here.

The end-to-end determinism of score_image() over real bytes depends on the
deepfake model and is exercised in the integration suite; here we isolate the
deterministic arithmetic core.
"""

from scoring.models import SignalBreakdown
from scoring.scorer import (
    build_result,
    compute_authenticity_score,
    map_compliance_status,
)

REPEATS = 50


def test_score_is_stable_across_repeated_calls():
    breakdown = SignalBreakdown(m=0.81, a=0.42, v=0.66, p=0.19)
    scores = {compute_authenticity_score(breakdown) for _ in range(REPEATS)}
    assert len(scores) == 1


def test_status_is_stable_across_repeated_calls():
    breakdown = SignalBreakdown(m=0.5, a=0.5, v=0.5, p=0.5)
    score = compute_authenticity_score(breakdown)
    statuses = {map_compliance_status(score) for _ in range(REPEATS)}
    assert len(statuses) == 1


def test_build_result_is_fully_deterministic(mock_deepfake_model):
    breakdown = SignalBreakdown(m=0.8, a=0.9, v=0.7, p=0.6)
    first = build_result("hash-abc", breakdown)
    for _ in range(REPEATS):
        again = build_result("hash-abc", breakdown)
        # Pydantic models compare field-by-field; identical inputs -> identical model.
        assert again == first


def test_equal_inputs_produce_equal_results_independently(mock_deepfake_model):
    # Two breakdowns constructed separately but with equal values must score equal.
    a = SignalBreakdown(m=0.33, a=0.77, v=0.5, p=0.1)
    b = SignalBreakdown(m=0.33, a=0.77, v=0.5, p=0.1)
    assert build_result("same-hash", a) == build_result("same-hash", b)


def test_distinct_hashes_only_differ_in_hash_field(mock_deepfake_model):
    breakdown = SignalBreakdown(m=0.6, a=0.6, v=0.6, p=0.6)
    one = build_result("hash-1", breakdown)
    two = build_result("hash-2", breakdown)
    assert one.media_hash != two.media_hash
    # Everything derived from the signals must be identical.
    assert one.authenticity_score == two.authenticity_score
    assert one.compliance_status == two.compliance_status
    assert one.score_breakdown == two.score_breakdown
