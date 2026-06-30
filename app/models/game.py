from datetime import datetime
from app import db


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(40), nullable=False)  # crash, slots, live, sportsbook, instant_win
    provider = db.Column(db.String(80), nullable=True)
    rtp_percent = db.Column(db.Numeric(5, 2), nullable=True)  # published return-to-player rate
    is_active = db.Column(db.Boolean, default=True)

    bets = db.relationship("Bet", backref="game", lazy="dynamic")


class Bet(db.Model):
    __tablename__ = "bets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)

    stake = db.Column(db.Numeric(12, 2), nullable=False)
    payout = db.Column(db.Numeric(12, 2), default=0)
    status = db.Column(db.String(20), default="settled")  # open, settled, void

    # server-side seed/hash for provably-fair verification, not exposed until round closes
    server_seed_hash = db.Column(db.String(128), nullable=True)
    server_seed_revealed = db.Column(db.String(128), nullable=True)
    client_seed = db.Column(db.String(128), nullable=True)

    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime, nullable=True)

    def net(self):
        return self.payout - self.stake
