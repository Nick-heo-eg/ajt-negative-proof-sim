"""
CLI runner for Interpretation Gap simulations.

Usage:
    python -m sim.run --case aircanada --seed 42 --out logs/aircanada_run.json
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from sim.core.candidate_generator import CandidateGenerator
from sim.core.judgment_layer import JudgmentLayer
from sim.core.log_schema import SimulationLog
from sim.core.repro import create_repro_info
from sim.core.ajt_record import create_ajt_record


def load_case_spec(case_id: str) -> Dict[str, Any]:
    """Load case specification."""
    if case_id == "aircanada":
        from sim.cases.aircanada_case import get_case_spec
        return get_case_spec()
    else:
        raise ValueError(f"Unknown case: {case_id}")


def load_input_fixture(case_id: str) -> Dict[str, Any]:
    """Load input fixture for a case."""
    fixture_path = Path(__file__).parent / "fixtures" / f"{case_id}_inputs.json"
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_simulation(case_id: str, seed: int, output_path: Path) -> SimulationLog:
    """
    Run a single simulation case.

    Args:
        case_id: Case identifier (e.g., "aircanada")
        seed: Random seed for deterministic generation
        output_path: Path to write output JSON

    Returns:
        SimulationLog object
    """
    # Load case components
    case_spec = load_case_spec(case_id)
    input_fixture = load_input_fixture(case_id)
    policy_path = Path(__file__).parent / "policies" / f"policy_{case_id}.yaml"

    # Initialize components
    generator = CandidateGenerator(seed=seed)
    judgment_layer = JudgmentLayer(policy_path=policy_path)

    # Generate candidates
    candidates = generator.generate_candidates(
        case_id=case_id,
        input_payload=input_fixture,
        case_spec=case_spec
    )

    # Apply Judgment Layer
    final_decision, decision_basis, negative_proofs = judgment_layer.evaluate(
        candidates=candidates,
        input_payload=input_fixture
    )

    # Derive risk level from candidates metadata
    risk_level = "medium"  # default
    if any(c.metadata.get("risk_level") == "high" for c in candidates):
        risk_level = "high"
    elif all(c.metadata.get("risk_level") == "low" for c in candidates):
        risk_level = "low"

    # Create AJT record (spec-compliant)
    ajt = create_ajt_record(
        model="deterministic-stub",
        decision=decision_basis.final_action,
        risk_level=risk_level,
        policy_version=judgment_layer.policy_version,
        session_id=input_fixture.get("scenario", "unknown"),
        app_version="sim-v0.1.0",
        human_in_loop=False,
        # Extensions
        negative_proof_count=len(negative_proofs),
        applied_rule_ids=decision_basis.applied_rule_ids,
        policy_hash=judgment_layer.policy_hash,
        candidates_count=len(candidates)
    )

    # Create simulation log
    log = SimulationLog(
        case_id=case_id,
        prompt_id=input_fixture.get("scenario", "unknown"),
        input_payload=input_fixture,
        policy_version=judgment_layer.policy_version,
        policy_hash=judgment_layer.policy_hash,
        candidates=candidates,
        decision=final_decision,
        decision_basis=decision_basis,
        negative_proof=negative_proofs,
        repro=create_repro_info(
            seed=seed,
            policy_hash=judgment_layer.policy_hash,
            prompt_id=input_fixture.get("scenario", "unknown"),
            canonical_output=""  # Will be filled after serialization
        ),
        ajt=ajt
    )

    # Update run hash with actual output
    canonical_json = log.to_canonical_json()
    log.repro.run_hash = create_repro_info(
        seed=seed,
        policy_hash=judgment_layer.policy_hash,
        prompt_id=input_fixture.get("scenario", "unknown"),
        canonical_output=canonical_json
    ).run_hash

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(log.model_dump(), f, indent=2, ensure_ascii=False, sort_keys=True)

    return log


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run Interpretation Gap simulation cases"
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=["aircanada"],  # Will add gdpr22, injection later
        help="Case to run"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output path for JSON log"
    )

    args = parser.parse_args()

    try:
        log = run_simulation(
            case_id=args.case,
            seed=args.seed,
            output_path=args.out
        )

        print(f" Simulation complete: {args.case}")
        print(f"  Policy: {log.policy_version} ({log.policy_hash[:8]}...)")
        print(f"  Candidates: {len(log.candidates)}")
        print(f"  Negative Proofs: {len(log.negative_proof)}")
        print(f"  Final Decision: {log.decision_basis.final_action}")
        print(f"  Run Hash: {log.repro.run_hash[:16]}...")
        print(f"  Output: {args.out}")

        # Print negative proof summary
        if log.negative_proof:
            print("\n  Blocked candidates:")
            for proof in log.negative_proof:
                print(f"    - {proof.candidate_id}: {proof.blocked_by_rule_id}")

        return 0

    except Exception as e:
        print(f" Simulation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
