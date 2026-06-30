from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    is_verified = db.Column(db.Boolean, default=False)
    is_self_excluded = db.Column(db.Boolean, default=False)
    self_excluded_until = db.Column(db.DateTime, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    daily_deposit_limit = db.Column(db.Numeric(12, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship("Wallet", backref="user", uselist=False)
    bets = db.relationship("Bet", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def masked_phone(self):
        return self.phone[:6] + "***" if len(self.phone) >= 6 else self.phone

    def is_of_legal_age(self):
        if not self.date_of_birth:
            return False
        from datetime import date
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        return age >= 18
