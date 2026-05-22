"""API routes for Fraud Detection."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import get_db, Transaction, FraudAlert, PayerProfile, FraudDecision, RiskLevel
from app.agents.orchestrator import FraudOrchestrator

router = APIRouter(prefix="/api/v1")
orchestrator = FraudOrchestrator()


class EvaluateRequest(BaseModel):
    payer_id: str
    amount: float
    channel: str = "card"
    biller: str = "Default Biller"
    ip_address: str = "192.168.1.1"
    device_fingerprint: str = "fp_default"


@router.post("/transactions/evaluate")
def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    return orchestrator.evaluate(db, req.payer_id, req.amount, req.channel, req.biller, req.ip_address, req.device_fingerprint)


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.query(Transaction).count()
    blocked = db.query(Transaction).filter(Transaction.decision == FraudDecision.BLOCK).count()
    flagged = db.query(Transaction).filter(Transaction.decision == FraudDecision.FLAG_REVIEW).count()
    approved = db.query(Transaction).filter(Transaction.decision == FraudDecision.APPROVE).count()
    avg_score = db.query(func.avg(Transaction.fraud_score)).scalar() or 0
    avg_ms = db.query(func.avg(Transaction.processing_time_ms)).scalar() or 0
    alerts = db.query(FraudAlert).filter(FraudAlert.resolved == False).count()
    return {
        "total_transactions": total, "blocked": blocked, "flagged": flagged,
        "approved": approved, "block_rate": round(blocked/max(total,1)*100, 1),
        "avg_fraud_score": round(avg_score, 4), "avg_processing_ms": round(avg_ms, 1),
        "open_alerts": alerts,
    }


@router.get("/transactions")
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    txns = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(limit).all()
    return {"transactions": [{"id": t.transaction_id, "payer": t.payer_id, "biller": t.biller_name,
            "amount": t.amount, "channel": t.channel.value if t.channel else None,
            "fraud_score": t.fraud_score, "decision": t.decision.value if t.decision else None,
            "risk": t.risk_level.value if t.risk_level else None, "ms": t.processing_time_ms,
            "time": t.created_at.isoformat() if t.created_at else None} for t in txns]}


@router.get("/alerts")
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(FraudAlert).filter(FraudAlert.resolved == False).order_by(FraudAlert.created_at.desc()).all()
    return {"alerts": [{"txn": a.transaction_id, "type": a.alert_type, "severity": a.severity,
            "desc": a.description, "time": a.created_at.isoformat()} for a in alerts]}


@router.get("/agents/status")
def agent_status():
    return orchestrator.get_status()
