"""Transaction Analyzer Agent — Extracts features from transaction + payer history."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import Transaction, PayerProfile


class TransactionAnalyzer:
    def __init__(self):
        self.name = "TransactionAnalyzer"
        self.status = "healthy"
        self.last_run: Optional[datetime] = None
        self.records_processed = 0

    def analyze(self, db: Session, payer_id: str, amount: float, channel: str,
                ip_address: str, device_fp: str) -> Dict[str, Any]:
        profile = db.query(PayerProfile).filter(PayerProfile.payer_id == payer_id).first()

        features = {
            "amount": amount,
            "channel": channel,
            "ip_address": ip_address,
            "device_fingerprint": device_fp,
        }

        if profile:
            # Amount deviation
            avg = profile.avg_transaction_amount or amount
            features["amount_deviation"] = abs(amount - avg) / max(avg, 1)
            features["amount_vs_max"] = amount / max(profile.max_transaction_amount, 1)
            features["is_new_payer"] = False
            features["transaction_history_count"] = profile.transaction_count
            features["prior_fraud_rate"] = profile.fraud_count / max(profile.transaction_count, 1)
            features["channel_mismatch"] = 1 if channel != profile.typical_channel else 0
            features["ip_mismatch"] = 1 if ip_address[:7] != (profile.typical_ip_prefix or "")[:7] else 0

            # Velocity: transactions in last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent = db.query(Transaction).filter(
                Transaction.payer_id == payer_id,
                Transaction.created_at >= one_hour_ago
            ).count()
            features["hourly_velocity"] = recent

            # Time since last transaction
            if profile.last_transaction_at:
                features["hours_since_last"] = (datetime.utcnow() - profile.last_transaction_at).total_seconds() / 3600
            else:
                features["hours_since_last"] = 999
        else:
            features["amount_deviation"] = 0.5
            features["amount_vs_max"] = 1.0
            features["is_new_payer"] = True
            features["transaction_history_count"] = 0
            features["prior_fraud_rate"] = 0
            features["channel_mismatch"] = 0
            features["ip_mismatch"] = 0
            features["hourly_velocity"] = 0
            features["hours_since_last"] = 999

        self.records_processed += 1
        self.last_run = datetime.utcnow()
        return features
