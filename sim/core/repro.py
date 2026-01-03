"""
Reproducibility utilities for simulation runs.
"""
from sim.core.log_schema import ReproInfo
from sim.core.hash_utils import compute_run_hash


def create_repro_info(
    seed: int,
    policy_hash: str,
    prompt_id: str,
    canonical_output: str
) -> ReproInfo:
    """
    Create reproducibility information for a run.

    Args:
        seed: Random seed used
        policy_hash: Hash of the policy
        prompt_id: Identifier for the prompt/input
        canonical_output: Canonical JSON of the output

    Returns:
        ReproInfo object with run hash
    """
    run_hash = compute_run_hash(
        prompt_id=prompt_id,
        policy_hash=policy_hash,
        seed=seed,
        canonical_output=canonical_output
    )

    return ReproInfo(
        seed=seed,
        deterministic=True,
        run_hash=run_hash,
        policy_hash=policy_hash
    )
