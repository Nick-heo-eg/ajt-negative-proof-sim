"""
Test AJT (AI Judgment Trail) spec compliance.

Validates conformance to: https://github.com/Nick-heo-eg/spec
"""
from pathlib import Path
import tempfile
from sim.run import run_simulation


def test_ajt_record_present():
    """AJT record should be present in simulation log."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt is not None, "AJT record should be present"


def test_ajt_required_fields():
    """AJT record must have all 9 spec-required fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)
        ajt = log.ajt

        # 9 required fields per spec
        required_fields = [
            "timestamp",
            "run_id",
            "model",
            "decision",
            "risk_level",
            "human_in_loop",
            "policy_version",
            "app_version",
            "session_id"
        ]

        for field in required_fields:
            assert hasattr(ajt, field), f"AJT must have '{field}' field"
            assert getattr(ajt, field) is not None, f"AJT.{field} must not be None"


def test_ajt_policy_version_matches():
    """AJT policy_version should match simulation policy_version."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt.policy_version == log.policy_version, \
            "AJT policy_version should match log policy_version"


def test_ajt_extensions_present():
    """AJT should include Echo/Simulation extensions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)
        ajt = log.ajt

        # Echo extensions
        assert ajt.negative_proof_count is not None, \
            "AJT should include negative_proof_count extension"
        assert ajt.applied_rule_ids is not None, \
            "AJT should include applied_rule_ids extension"
        assert ajt.policy_hash is not None, \
            "AJT should include policy_hash extension"
        assert ajt.candidates_count is not None, \
            "AJT should include candidates_count extension"


def test_ajt_policy_hash_matches():
    """AJT policy_hash extension should match simulation policy_hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt.policy_hash == log.policy_hash, \
            "AJT policy_hash extension should match log policy_hash"


def test_ajt_negative_proof_count_accurate():
    """AJT negative_proof_count should match actual negative_proof list length."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt.negative_proof_count == len(log.negative_proof), \
            "AJT negative_proof_count should match actual count"


def test_ajt_candidates_count_accurate():
    """AJT candidates_count should match actual candidates list length."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt.candidates_count == len(log.candidates), \
            "AJT candidates_count should match actual count"


def test_ajt_human_in_loop_false_for_simulation():
    """Simulation should have human_in_loop = False."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt.human_in_loop is False, \
            "Simulation should have human_in_loop = False"


def test_ajt_decision_matches_final_action():
    """AJT decision should match decision_basis.final_action."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        assert log.ajt.decision == log.decision_basis.final_action, \
            "AJT decision should match decision_basis.final_action"


def test_ajt_is_serializable():
    """AJT record must be JSON serializable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        out = tmpdir / "run.json"

        log = run_simulation("aircanada", seed=42, output_path=out)

        import json
        # Should be able to serialize full log including AJT
        json_str = json.dumps(log.model_dump(), indent=2)
        assert json_str, "Log with AJT must be serializable"

        # Should be able to deserialize
        data = json.loads(json_str)
        assert "ajt" in data, "Serialized log should contain 'ajt' field"
        assert data["ajt"] is not None, "Serialized AJT should not be null"
