# Real-Time Payment Fraud Detection

> **Non-Hackathon Bucket — PoC Idea #3**
>
> ML-powered fraud scoring engine that evaluates every payment transaction in real-time,
> replacing IC's current rule-based Chase Screening API approach.

## What This Is

A **3-agent fraud detection pipeline** that scores transactions in <100ms:

1. **Transaction Analyzer Agent** — Extracts features from transaction + payer history
2. **Fraud Scorer Agent** — Ensemble model combining velocity, anomaly, and behavioral scores
3. **Decision Engine Agent** — Apply/block/flag based on score thresholds + biller config

## Why This Matters

- IC's current fraud = Chase Screening API + 9 processor-specific reject repos (all rule-based)
- No ML scoring, no payer risk profiles, no cross-channel correlation
- PaymentForesight MLOps infra (Azure ML, Snowflake, MLflow) can host fraud models with zero new infra
- Fraud losses in payments industry: 1-3% of transaction volume

## Quick Start

```bash
cd backend && pip install -r requirements.txt && python -m app.seed_data && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

## IC Context

- **Chase Screening API**: Current fraud gate — rule-based only
- **9 Processor Reject repos**: Chase, EFT, PayPal, Wells Fargo, etc.
- **PaymentForesight MLOps**: Azure ML + Snowflake — can host fraud models
- **Cross-channel**: ACH, card, PayPal, Apple Pay — need unified scoring

## License

Internal InvoiceCloud use only.
