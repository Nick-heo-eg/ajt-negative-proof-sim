"""
Test that Negative Proof records are generated when candidates are blocked.
"""
from pathlib import Path
import tempfile
from sim.run import run_simulation
from sim.cases.aircanada_case import get_expected_outcome


def test_negative_proof_generated_for_blocked_candidates():
    """Blocked candidates must generate Negative Proof records."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        # Air Canada case should have negative proofs
        assert len(log.negative_proof) > 0, "Should have at least one Negative Proof"

        # Each negative proof must have required fields
        for proof in log.negative_proof:
            assert proof.candidate_id, "Must have candidate_id"
            assert proof.blocked_by_rule_id, "Must have blocking rule_id"
            assert proof.reason, "Must have reason"
            assert proof.blocked_candidate, "Must have blocked content"


def test_negative_proof_matches_expected_rules():
    """Negative Proof should reference expected policy rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)
        expected = get_expected_outcome()

        # Check that expected rules appear in negative proofs
        blocked_rule_ids = {proof.blocked_by_rule_id for proof in log.negative_proof}

        for required_rule in expected["required_negative_proof_rules"]:
            assert required_rule in blocked_rule_ids, \
                f"Expected rule {required_rule} to block at least one candidate"


def test_negative_proof_count_meets_minimum():
    """Should block at least the expected number of candidates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)
        expected = get_expected_outcome()

        assert len(log.negative_proof) >= expected["blocked_candidates_min"], \
            f"Should block at least {expected['blocked_candidates_min']} candidates"


def test_selected_candidate_not_in_negative_proof():
    """The selected candidate should NOT appear in Negative Proof."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        if log.decision_basis.selected_candidate_id:
            blocked_ids = {proof.candidate_id for proof in log.negative_proof}
            assert log.decision_basis.selected_candidate_id not in blocked_ids, \
                "Selected candidate should not be in negative proof"


def test_negative_proof_is_serializable():
    """Negative Proof must be JSON serializable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        # Should be able to serialize to JSON
        import json
        json_str = json.dumps(log.model_dump(), indent=2)
        assert json_str, "Log with negative proof must be serializable"

        # Should be able to deserialize
        data = json.loads(json_str)
        assert "negative_proof" in data
        assert isinstance(data["negative_proof"], list)
