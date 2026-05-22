"""Decision Engine Agent — Approve/block/flag based on fraud score."""
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.database import FraudDecision, RiskLevel

THRESHOLDS = {"block": 0.75, "flag_review": 0.50, "step_up_auth": 0.35, "approve": 0.0}


class DecisionEngine:
    def __init__(self):
        self.name = "DecisionEngine"
        self.status = "healthy"
        self.last_run: Optional[datetime] = None
        self.records_processed = 0

    def decide(self, fraud_score: float, amount: float, risk_factors: list) -> Dict[str, Any]:
        if fraud_score >= THRESHOLDS["block"]:
            decision = FraudDecision.BLOCK
            risk = RiskLevel.CRITICAL
        elif fraud_score >= THRESHOLDS["flag_review"]:
            decision = FraudDecision.FLAG_REVIEW
            risk = RiskLevel.HIGH
        elif fraud_score >= THRESHOLDS["step_up_auth"]:
            decision = FraudDecision.STEP_UP_AUTH
            risk = RiskLevel.MEDIUM
        else:
            decision = FraudDecision.APPROVE
            risk = RiskLevel.LOW

        # Override: high-amount + any risk = escalate
        if amount > 2000 and fraud_score >= 0.25:
            if decision == FraudDecision.APPROVE:
                decision = FraudDecision.STEP_UP_AUTH
                risk = RiskLevel.MEDIUM

        self.records_processed += 1
        self.last_run = datetime.utcnow()

        return {
            "decision": decision.value,
            "risk_level": risk.value,
            "fraud_score": fraud_score,
            "reason": self._reason(decision, risk_factors),
        }

    def _reason(self, decision: FraudDecision, factors: list) -> str:
        if decision == FraudDecision.APPROVE:
            return "Transaction within normal parameters"
        if decision == FraudDecision.BLOCK:
            return f"Blocked: {', '.join(f['factor'] for f in factors[:3])}"
        if decision == FraudDecision.FLAG_REVIEW:
            return f"Flagged for review: {', '.join(f['factor'] for f in factors[:2])}"
        return "Step-up authentication required"
