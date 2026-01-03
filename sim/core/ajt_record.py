"""
AI Judgment Trail (AJT) record schema.

Conforms to: https://github.com/Nick-heo-eg/spec

This simulation demonstrates that Negative Proof can be derived
without modifying the decision process, by extending a minimal,
standard-aligned Judgment Trace (AJT).
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class AJTRecord(BaseModel):
    """
    AI Judgment Trail record (spec-compliant).

    9 required fields per spec + optional Echo/Simulation extensions.
    """

    # ========================================
    # Spec-required fields (9)
    # https://github.com/Nick-heo-eg/spec
    # ========================================

    timestamp: str = Field(
        description="ISO-8601 UTC timestamp when the decision was made",
        examples=["2025-01-15T14:32:11Z"]
    )

    run_id: str = Field(
        description="Unique identifier for this specific AI execution (UUID v4)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    model: str = Field(
        description="AI model identifier used for this decision",
        examples=["gpt-4", "claude-3-opus", "deterministic-stub"]
    )

    decision: str = Field(
        description="Decision made by the system",
        examples=["allow", "block", "escalate", "fallback"]
    )

    risk_level: str = Field(
        description="Assessed risk level for this decision",
        examples=["low", "medium", "high", "critical"]
    )

    human_in_loop: bool = Field(
        description="Whether a human reviewed or approved this decision"
    )

    policy_version: str = Field(
        description="Version identifier of the decision policy applied",
        examples=["v2.3.1", "policy-20250115"]
    )

    app_version: str = Field(
        description="Version of the application making the AI call",
        examples=["1.0.5", "sim-v0.1.0"]
    )

    session_id: str = Field(
        description="User or request session identifier",
        examples=["user-session-abc123", "req-550e8400"]
    )

    # ========================================
    # Echo/Simulation Extensions (optional)
    # ========================================

    negative_proof_count: Optional[int] = Field(
        default=None,
        description="Number of candidates blocked (Echo-specific)"
    )

    applied_rule_ids: Optional[List[str]] = Field(
        default=None,
        description="List of policy rule IDs applied in this decision (Echo-specific)"
    )

    policy_hash: Optional[str] = Field(
        default=None,
        description="SHA256 hash of policy for integrity verification (Echo-specific)"
    )

    candidates_count: Optional[int] = Field(
        default=None,
        description="Total number of candidates generated (Simulation-specific)"
    )

    class Config:
        json_schema_extra = {
            "spec_url": "https://github.com/Nick-heo-eg/spec",
            "compliance": "AJT v0.1 + Echo extensions",
            "note": "Extensions do not alter decision process, only auditability"
        }


def create_ajt_record(
    *,
    run_id: Optional[str] = None,
    model: str = "deterministic-stub",
    decision: str,
    risk_level: str,
    policy_version: str,
    session_id: str,
    app_version: str = "sim-v0.1.0",
    human_in_loop: bool = False,
    # Extensions
    negative_proof_count: Optional[int] = None,
    applied_rule_ids: Optional[List[str]] = None,
    policy_hash: Optional[str] = None,
    candidates_count: Optional[int] = None
) -> AJTRecord:
    """
    Create AJT record with automatic timestamp and run_id generation.

    Args:
        run_id: Optional UUID; auto-generated if not provided
        model: AI model identifier (default: "deterministic-stub" for simulation)
        decision: Final decision ("allow", "block", "fallback", etc.)
        risk_level: Risk assessment ("low", "medium", "high", "critical")
        policy_version: Policy version string
        session_id: Session/request identifier
        app_version: Application version (default: "sim-v0.1.0")
        human_in_loop: Whether human reviewed (default: False)
        negative_proof_count: Optional count of blocked candidates
        applied_rule_ids: Optional list of applied rule IDs
        policy_hash: Optional policy hash for integrity
        candidates_count: Optional total candidate count

    Returns:
        AJTRecord instance
    """
    return AJTRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        run_id=run_id or str(uuid.uuid4()),
        model=model,
        decision=decision,
        risk_level=risk_level,
        human_in_loop=human_in_loop,
        policy_version=policy_version,
        app_version=app_version,
        session_id=session_id,
        # Extensions
        negative_proof_count=negative_proof_count,
        applied_rule_ids=applied_rule_ids,
        policy_hash=policy_hash,
        candidates_count=candidates_count
    )
