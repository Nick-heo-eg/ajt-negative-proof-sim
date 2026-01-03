"""
Deterministic candidate generator stub.
Simulates LLM output without actual API calls.
"""
import random
from typing import List, Dict, Any
from sim.core.log_schema import Candidate


class CandidateGenerator:
    """
    Generates candidate responses deterministically based on seed.
    Does NOT make real LLM calls - this is a simulation.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_candidates(
        self,
        case_id: str,
        input_payload: Dict[str, Any],
        case_spec: Dict[str, Any]
    ) -> List[Candidate]:
        """
        Generate candidates based on case specification.

        Args:
            case_id: Identifier for the case (e.g., "aircanada")
            input_payload: User input data
            case_spec: Case-specific configuration for candidate generation

        Returns:
            List of Candidate objects
        """
        candidates_spec = case_spec.get("candidates", [])
        candidates = []

        for i, spec in enumerate(candidates_spec):
            # Add deterministic variation based on seed
            confidence_base = spec.get("confidence", 0.8)
            # Add small random variation that's deterministic
            confidence = round(
                confidence_base + self.rng.uniform(-0.05, 0.05),
                4
            )
            confidence = max(0.0, min(1.0, confidence))

            candidate = Candidate(
                candidate_id=f"{case_id}_candidate_{i}",
                proposal=spec["proposal"],
                reason=spec["reason"],
                confidence=confidence,
                metadata=spec.get("metadata", {})
            )
            candidates.append(candidate)

        return candidates

    def reset_seed(self, seed: int):
        """Reset the random seed for reproducibility."""
        self.seed = seed
        self.rng = random.Random(seed)
