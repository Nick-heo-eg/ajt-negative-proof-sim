"""
Hash utilities for reproducibility and policy versioning.
"""
import hashlib
import json
from typing import Any, Dict


def compute_sha256(content: str) -> str:
    """Compute SHA256 hash of a string."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def compute_policy_hash(policy_dict: Dict[str, Any]) -> str:
    """
    Compute stable hash of a policy YAML loaded as dict.
    Uses canonical JSON serialization with sorted keys.
    """
    canonical = json.dumps(policy_dict, sort_keys=True, ensure_ascii=False)
    return compute_sha256(canonical)


def compute_run_hash(
    prompt_id: str,
    policy_hash: str,
    seed: int,
    canonical_output: str
) -> str:
    """
    Compute hash representing this specific run.
    Same inputs + same policy + same seed => same run_hash.
    """
    combined = f"{prompt_id}|{policy_hash}|{seed}|{canonical_output}"
    return compute_sha256(combined)
