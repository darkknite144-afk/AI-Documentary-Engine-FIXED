from app.agents.quality_controller import quality_controller


def test_gate_check_passes_when_both_checks_pass():
    assert quality_controller.gate_check({"status": "PASS"}, {"status": "PASS"}) == "PASS"


def test_gate_check_needs_review_when_red_team_fails():
    result = quality_controller.gate_check({"status": "NEEDS_REWRITE"}, {"status": "PASS"})
    assert result == "NEEDS_REVIEW"


def test_gate_check_needs_review_when_fact_check_fails():
    result = quality_controller.gate_check({"status": "PASS"}, {"status": "FLAGGED"})
    assert result == "NEEDS_REVIEW"


def test_gate_check_defaults_to_needs_review_on_missing_status():
    assert quality_controller.gate_check({}, {}) == "NEEDS_REVIEW"
