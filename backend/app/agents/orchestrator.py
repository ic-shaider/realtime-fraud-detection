"""Fraud Detection Orchestrator."""
import uuid, time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.agents.transaction_analyzer import TransactionAnalyzer
from app.agents.fraud_scorer import FraudScorer
from app.agents.decision_engine import DecisionEngine
from app.models.database import Transaction, PayerProfile, FraudAlert, FraudDecision


class FraudOrchestrator:
    def __init__(self):
        self.analyzer = TransactionAnalyzer()
        self.scorer = FraudScorer()
        self.engine = DecisionEngine()
        self.transactions_processed = 0
        self.last_run: Optional[datetime] = None

    def evaluate(self, db: Session, payer_id: str, amount: float, channel: str,
                 biller: str, ip_address: str = "192.168.1.1", device_fp: str = "fp_default") -> Dict[str, Any]:
        start = time.time()
        txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        features = self.analyzer.analyze(db, payer_id, amount, channel, ip_address, device_fp)
        scores = self.scorer.score(features)
        decision = self.engine.decide(scores["fraud_score"], amount, scores["risk_factors"])
        processing_ms = int((time.time() - start) * 1000)

        # Store transaction
        txn = Transaction(
            transaction_id=txn_id, payer_id=payer_id, biller_name=biller,
            amount=amount, channel=channel, ip_address=ip_address,
            device_fingerprint=device_fp, fraud_score=scores["fraud_score"],
            velocity_score=scores["velocity_score"], anomaly_score=scores["anomaly_score"],
            behavioral_score=scores["behavioral_score"],
            risk_level=decision["risk_level"], decision=decision["decision"],
            risk_factors=scores["risk_factors"], processing_time_ms=processing_ms,
        )
        db.add(txn)

        # Create alert if blocked/flagged
        if decision["decision"] in ("block", "flag_review"):
            db.add(FraudAlert(
                transaction_id=txn_id, alert_type=decision["decision"],
                severity=decision["risk_level"], description=decision["reason"],
            ))

        # Update payer profile
        profile = db.query(PayerProfile).filter(PayerProfile.payer_id == payer_id).first()
        if profile:
            profile.transaction_count += 1
            profile.last_transaction_at = datetime.utcnow()
            if amount > profile.max_transaction_amount:
                profile.max_transaction_amount = amount
            profile.avg_transaction_amount = (profile.avg_transaction_amount * (profile.transaction_count - 1) + amount) / profile.transaction_count

        db.commit()
        self.transactions_processed += 1
        self.last_run = datetime.utcnow()

        return {"transaction_id": txn_id, "processing_ms": processing_ms, **scores, **decision}

    def get_status(self) -> Dict[str, Any]:
        return {
            "orchestrator": {"transactions_processed": self.transactions_processed, "last_run": self.last_run.isoformat() if self.last_run else None},
            "agents": [
                {"name": self.analyzer.name, "status": self.analyzer.status, "records_processed": self.analyzer.records_processed},
                {"name": self.scorer.name, "status": self.scorer.status, "records_processed": self.scorer.records_processed},
                {"name": self.engine.name, "status": self.engine.status, "records_processed": self.engine.records_processed},
            ]
        }
