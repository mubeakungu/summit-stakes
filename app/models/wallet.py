from datetime import datetime
from app import db


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0)
    bonus_balance = db.Column(db.Numeric(12, 2), default=0)
    currency = db.Column(db.String(3), default="KES")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="wallet", lazy="dynamic")


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False)

    # deposit, withdrawal, bet_stake, bet_payout, cashback, bonus
    tx_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, completed, failed, reversed

    mpesa_receipt = db.Column(db.String(40), nullable=True, index=True)
    mpesa_checkout_request_id = db.Column(db.String(60), nullable=True, index=True)
    phone_used = db.Column(db.String(15), nullable=True)

    reference = db.Column(db.String(60), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
