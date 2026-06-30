from flask import Blueprint, jsonify
from app.models.game import Bet
from app.models.user import User

api_bp = Blueprint("api", __name__)


@api_bp.route("/winners")
def winners():
    """
    Latest settled bets with a positive net result, newest first.
    Polled by the promotions page winners ticker every few seconds.
    Phone numbers are masked server-side - never expose the full number here.
    """
    recent = (
        Bet.query.filter(Bet.status == "settled", Bet.payout > Bet.stake)
        .order_by(Bet.settled_at.desc())
        .limit(8)
        .all()
    )

    out = []
    for bet in recent:
        user = User.query.get(bet.user_id)
        if not user:
            continue
        out.append(
            {
                "masked_id": user.masked_phone(),
                "amount": float(bet.net()),
                "game": bet.game.name if bet.game else "Unknown",
                "settled_at": bet.settled_at.isoformat() if bet.settled_at else None,
            }
        )

    return jsonify(out)
