"""
Test that policy changes are detected via hash changes.
"""
import yaml
import tempfile
from pathlib import Path
from sim.core.hash_utils import compute_policy_hash
from sim.core.judgment_layer import JudgmentLayer


def test_policy_hash_changes_when_policy_modified():
    """Modifying policy content should change the policy hash."""
    # Load original policy
    original_path = Path(__file__).parent.parent / "policies" / "policy_aircanada.yaml"
    with open(original_path, 'r') as f:
        original_policy = yaml.safe_load(f)

    original_hash = compute_policy_hash(original_policy)

    # Create modified policy
    modified_policy = original_policy.copy()
    modified_policy["version"] = "2.0.0"  # Change version

    modified_hash = compute_policy_hash(modified_policy)

    assert original_hash != modified_hash, "Hash should change when policy is modified"


def test_policy_hash_stable_for_same_content():
    """Same policy content should always produce same hash."""
    policy_path = Path(__file__).parent.parent / "policies" / "policy_aircanada.yaml"

    # Load twice
    layer1 = JudgmentLayer(policy_path)
    layer2 = JudgmentLayer(policy_path)

    assert layer1.policy_hash == layer2.policy_hash, \
        "Same policy should produce same hash"


def test_adding_rule_changes_hash():
    """Adding a new rule should change the policy hash."""
    original_path = Path(__file__).parent.parent / "policies" / "policy_aircanada.yaml"
    with open(original_path, 'r') as f:
        original_policy = yaml.safe_load(f)

    original_hash = compute_policy_hash(original_policy)

    # Add a new rule
    modified_policy = original_policy.copy()
    modified_policy["rules"] = original_policy["rules"].copy()
    modified_policy["rules"].append({
        "id": "R999_new_rule",
        "type": "test_rule",
        "description": "New test rule"
    })

    modified_hash = compute_policy_hash(modified_policy)

    assert original_hash != modified_hash, \
        "Adding a rule should change policy hash"


def test_rule_order_affects_hash():
    """Changing rule order should change the hash (rules are ordered)."""
    original_path = Path(__file__).parent.parent / "policies" / "policy_aircanada.yaml"
    with open(original_path, 'r') as f:
        original_policy = yaml.safe_load(f)

    original_hash = compute_policy_hash(original_policy)

    # Reverse rule order
    modified_policy = original_policy.copy()
    modified_policy["rules"] = list(reversed(original_policy["rules"]))

    modified_hash = compute_policy_hash(modified_policy)

    # Only fail if there are at least 2 rules to reorder
    if len(original_policy["rules"]) >= 2:
        assert original_hash != modified_hash, \
            "Changing rule order should change policy hash"
