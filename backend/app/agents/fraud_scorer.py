"""Fraud Scorer Agent — Ensemble scoring (velocity + anomaly + behavioral)."""
from datetime import datetime
from typing import Dict, Any, List, Optional


class FraudScorer:
    def __init__(self):
        self.name = "FraudScorer"
        self.status = "healthy"
        self.last_run: Optional[datetime] = None
        self.records_processed = 0

    def score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        velocity = self._velocity_score(features)
        anomaly = self._anomaly_score(features)
        behavioral = self._behavioral_score(features)

        # Weighted ensemble
        fraud_score = round(velocity * 0.35 + anomaly * 0.40 + behavioral * 0.25, 4)
        risk_factors = self._get_risk_factors(features, velocity, anomaly, behavioral)

        self.records_processed += 1
        self.last_run = datetime.utcnow()

        return {
            "fraud_score": fraud_score,
            "velocity_score": velocity,
            "anomaly_score": anomaly,
            "behavioral_score": behavioral,
            "risk_factors": risk_factors,
        }

    def _velocity_score(self, features: Dict[str, Any]) -> float:
        score = 0.0
        velocity = features.get("hourly_velocity", 0)
        if velocity >= 5:
            score += 0.5
        elif velocity >= 3:
            score += 0.3
        elif velocity >= 2:
            score += 0.15

        hours_since = features.get("hours_since_last", 999)
        if hours_since < 0.05:  # <3 min
            score += 0.3
        elif hours_since < 0.5:
            score += 0.1

        return min(round(score, 4), 0.99)

    def _anomaly_score(self, features: Dict[str, Any]) -> float:
        score = 0.0
        deviation = features.get("amount_deviation", 0)
        if deviation > 3.0:
            score += 0.5
        elif deviation > 1.5:
            score += 0.3
        elif deviation > 0.8:
            score += 0.15

        if features.get("amount_vs_max", 0) > 1.5:
            score += 0.2

        if features.get("is_new_payer"):
            score += 0.1

        if features.get("amount", 0) > 1000:
            score += 0.1

        return min(round(score, 4), 0.99)

    def _behavioral_score(self, features: Dict[str, Any]) -> float:
        score = 0.0
        if features.get("channel_mismatch"):
            score += 0.25
        if features.get("ip_mismatch"):
            score += 0.3
        if features.get("prior_fraud_rate", 0) > 0:
            score += features["prior_fraud_rate"] * 0.5
        return min(round(score, 4), 0.99)

    def _get_risk_factors(self, features: Dict, vel: float, anom: float, beh: float) -> List[Dict]:
        factors = []
        if vel > 0.3:
            factors.append({"factor": "high_velocity", "score": vel, "desc": f"{features.get('hourly_velocity', 0)} txns in last hour"})
        if anom > 0.3:
            factors.append({"factor": "amount_anomaly", "score": anom, "desc": f"Amount deviation: {features.get('amount_deviation', 0):.1f}x"})
        if beh > 0.2:
            factors.append({"factor": "behavioral_mismatch", "score": beh, "desc": "Channel or IP mismatch"})
        if features.get("is_new_payer"):
            factors.append({"factor": "new_payer", "score": 0.1, "desc": "First-time payer"})
        return factors
