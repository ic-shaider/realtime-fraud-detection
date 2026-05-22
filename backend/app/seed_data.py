"""Seed data for Fraud Detection."""
import random
from datetime import datetime, timedelta
from app.models.database import (init_db, SessionLocal, Transaction, PayerProfile, FraudAlert,
                                  PaymentChannel, FraudDecision, RiskLevel)

BILLERS = ["CDE Lightband", "Soquel Creek Water", "City of Wylie TX", "Texas Farm Bureau",
           "Safety Insurance", "FCCI Insurance", "Comcast Business"]
CHANNELS = list(PaymentChannel)


def seed():
    init_db()
    db = SessionLocal()
    db.query(FraudAlert).delete()
    db.query(Transaction).delete()
    db.query(PayerProfile).delete()
    db.commit()

    # Create payer profiles
    for i in range(60):
        fraud_rate = random.choice([0]*50 + [0.05]*5 + [0.1]*3 + [0.2]*2)
        db.add(PayerProfile(
            payer_id=f"PAY-{10000+i}", name=f"Payer {i}",
            avg_transaction_amount=round(random.uniform(50, 400), 2),
            max_transaction_amount=round(random.uniform(200, 1500), 2),
            typical_channel=random.choice(CHANNELS).value,
            typical_ip_prefix=f"192.168.{random.randint(1,10)}",
            transaction_count=random.randint(5, 100),
            fraud_count=int(random.randint(5, 100) * fraud_rate),
            risk_score=round(fraud_rate * 2, 3),
            last_transaction_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720)),
        ))

    # Generate transactions
    for i in range(300):
        payer = f"PAY-{random.randint(10000, 10059)}"
        amount = round(random.uniform(10, 2000), 2)
        channel = random.choice(CHANNELS)
        is_fraud = random.random() < 0.08
        score = round(random.uniform(0.6, 0.95) if is_fraud else random.uniform(0.01, 0.45), 4)

        if score >= 0.75:
            decision = FraudDecision.BLOCK
            risk = RiskLevel.CRITICAL
        elif score >= 0.50:
            decision = FraudDecision.FLAG_REVIEW
            risk = RiskLevel.HIGH
        elif score >= 0.35:
            decision = FraudDecision.STEP_UP_AUTH
            risk = RiskLevel.MEDIUM
        else:
            decision = FraudDecision.APPROVE
            risk = RiskLevel.LOW

        txn = Transaction(
            transaction_id=f"TXN-{i:06d}", payer_id=payer, biller_name=random.choice(BILLERS),
            amount=amount, channel=channel, ip_address=f"192.168.{random.randint(1,20)}.{random.randint(1,254)}",
            device_fingerprint=f"fp_{random.randint(1000,9999)}",
            fraud_score=score, velocity_score=round(random.uniform(0, 0.5), 3),
            anomaly_score=round(random.uniform(0, 0.6), 3), behavioral_score=round(random.uniform(0, 0.4), 3),
            risk_level=risk, decision=decision, is_fraud=is_fraud,
            risk_factors=[{"factor": "test", "score": score}],
            processing_time_ms=random.randint(5, 80),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
        )
        db.add(txn)

        if decision in (FraudDecision.BLOCK, FraudDecision.FLAG_REVIEW):
            db.add(FraudAlert(
                transaction_id=txn.transaction_id, alert_type=decision.value,
                severity=risk.value, description=f"Score {score:.3f} - {decision.value}",
                resolved=random.random() < 0.6,
                created_at=txn.created_at,
            ))

    db.commit()
    db.close()
    print("✓ Seeded 60 payers, 300 transactions, fraud alerts")


if __name__ == "__main__":
    seed()
