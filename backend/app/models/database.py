"""Database models for Real-Time Fraud Detection."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
DATABASE_URL = "sqlite:///./fraud_detection.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PaymentChannel(str, PyEnum):
    ACH = "ach"
    CARD = "card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class FraudDecision(str, PyEnum):
    APPROVE = "approve"
    BLOCK = "block"
    FLAG_REVIEW = "flag_review"
    STEP_UP_AUTH = "step_up_auth"


class RiskLevel(str, PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(50), unique=True)
    payer_id = Column(String(50))
    biller_name = Column(String(200))
    amount = Column(Float)
    channel = Column(Enum(PaymentChannel))
    ip_address = Column(String(50))
    device_fingerprint = Column(String(100))
    fraud_score = Column(Float, default=0.0)
    velocity_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    risk_level = Column(Enum(RiskLevel))
    decision = Column(Enum(FraudDecision))
    risk_factors = Column(JSON)
    is_fraud = Column(Boolean, default=False)
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PayerProfile(Base):
    __tablename__ = "payer_profiles"
    id = Column(Integer, primary_key=True)
    payer_id = Column(String(50), unique=True)
    name = Column(String(200))
    avg_transaction_amount = Column(Float, default=0.0)
    max_transaction_amount = Column(Float, default=0.0)
    typical_channel = Column(String(50))
    typical_ip_prefix = Column(String(20))
    transaction_count = Column(Integer, default=0)
    fraud_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    last_transaction_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(50))
    alert_type = Column(String(50))
    severity = Column(String(20))
    description = Column(String(500))
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
