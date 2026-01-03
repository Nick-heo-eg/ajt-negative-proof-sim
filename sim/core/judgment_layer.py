"""
Judgment Layer: External decision-making system with explicit rules.
The LLM generates candidates; the Judgment Layer makes the final decision.
Every rejected candidate generates a Negative Proof record.
"""
import yaml
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from sim.core.log_schema import Candidate, NegativeProof, DecisionBasis
from sim.core.hash_utils import compute_policy_hash


class JudgmentLayer:
    """
    External decision system that applies explicit rules to candidates.

    Key principles:
    - LLM is a generator, not a decider
    - Every decision must have explicit rule basis
    - Every rejection must emit Negative Proof
    """

    def __init__(self, policy_path: Path):
        """Load policy from YAML file."""
        self.policy_path = policy_path
        with open(policy_path, 'r', encoding='utf-8') as f:
            self.policy = yaml.safe_load(f)

        self.policy_version = self.policy.get("version", "unknown")
        self.policy_hash = compute_policy_hash(self.policy)
        self.rules = self.policy.get("rules", [])

    def evaluate(
        self,
        candidates: List[Candidate],
        input_payload: Dict[str, Any]
    ) -> Tuple[str, DecisionBasis, List[NegativeProof]]:
        """
        Evaluate candidates and make final decision.

        Returns:
            - final_decision: The selected response or override
            - decision_basis: Explanation with rule IDs
            - negative_proofs: Records of blocked candidates
        """
        negative_proofs: List[NegativeProof] = []
        applied_rules: List[str] = []
        selected_candidate: Optional[Candidate] = None

        # Apply rules in order
        for rule in self.rules:
            rule_id = rule["id"]
            rule_type = rule["type"]

            if rule_type == "block_pattern":
                # Block candidates matching a pattern
                pattern = rule["pattern"]
                for candidate in candidates:
                    if pattern.lower() in candidate.proposal.lower():
                        negative_proofs.append(NegativeProof(
                            candidate_id=candidate.candidate_id,
                            blocked_candidate=candidate.proposal[:100],
                            blocked_by_rule_id=rule_id,
                            reason=rule.get("reason", "Pattern matched block rule")
                        ))
                        applied_rules.append(rule_id)

            elif rule_type == "source_of_truth_enforcement":
                # Validate against source of truth
                truth_data = rule.get("source_of_truth", {})
                for candidate in candidates:
                    # Check if candidate contradicts source of truth
                    if self._contradicts_truth(candidate, truth_data):
                        negative_proofs.append(NegativeProof(
                            candidate_id=candidate.candidate_id,
                            blocked_candidate=candidate.proposal[:100],
                            blocked_by_rule_id=rule_id,
                            reason=f"Contradicts source of truth: {rule.get('reason', '')}"
                        ))
                        applied_rules.append(rule_id)

            elif rule_type == "require_citation":
                # Require candidates to cite sources
                for candidate in candidates:
                    has_citation = candidate.metadata.get("has_citation", False)
                    if not has_citation:
                        negative_proofs.append(NegativeProof(
                            candidate_id=candidate.candidate_id,
                            blocked_candidate=candidate.proposal[:100],
                            blocked_by_rule_id=rule_id,
                            reason="Missing required citation"
                        ))
                        applied_rules.append(rule_id)

            elif rule_type == "confidence_threshold":
                # Block low-confidence candidates
                threshold = rule.get("min_confidence", 0.7)
                for candidate in candidates:
                    if candidate.confidence < threshold:
                        negative_proofs.append(NegativeProof(
                            candidate_id=candidate.candidate_id,
                            blocked_candidate=candidate.proposal[:100],
                            blocked_by_rule_id=rule_id,
                            reason=f"Confidence {candidate.confidence} below threshold {threshold}"
                        ))
                        applied_rules.append(rule_id)

            elif rule_type == "override_with_template":
                # Use override template instead of LLM output
                template = rule.get("template", "")
                applied_rules.append(rule_id)
                # This will be used as final decision
                final_action = "override"
                decision_basis = DecisionBasis(
                    selected_candidate_id=None,
                    applied_rule_ids=applied_rules,
                    reasoning=rule.get("reason", "Policy override"),
                    final_action=final_action
                )
                return template, decision_basis, negative_proofs

        # Find best candidate that wasn't blocked
        blocked_ids = {proof.candidate_id for proof in negative_proofs}
        viable_candidates = [c for c in candidates if c.candidate_id not in blocked_ids]

        if not viable_candidates:
            # All blocked - use fallback
            fallback = self.policy.get("fallback", "No suitable response available.")
            applied_rules.append("fallback")
            decision_basis = DecisionBasis(
                selected_candidate_id=None,
                applied_rule_ids=applied_rules,
                reasoning="All candidates blocked by policy rules",
                final_action="fallback"
            )
            return fallback, decision_basis, negative_proofs

        # Select highest confidence viable candidate
        selected_candidate = max(viable_candidates, key=lambda c: c.confidence)
        applied_rules.append("confidence_selection")

        decision_basis = DecisionBasis(
            selected_candidate_id=selected_candidate.candidate_id,
            applied_rule_ids=applied_rules,
            reasoning=f"Selected candidate with highest confidence among viable options",
            final_action="allow"
        )

        return selected_candidate.proposal, decision_basis, negative_proofs

    def _contradicts_truth(self, candidate: Candidate, truth_data: Dict[str, Any]) -> bool:
        """Check if candidate contradicts source of truth."""
        # Simple pattern matching for simulation
        forbidden_claims = truth_data.get("forbidden_claims", [])
        for claim in forbidden_claims:
            if claim.lower() in candidate.proposal.lower():
                return True
        return False
