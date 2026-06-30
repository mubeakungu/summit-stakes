from datetime import date
from flask import Blueprint, render_template
from sqlalchemy import func
from app import db
from app.models.wallet import Transaction

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/promotions")
def promotions():
    today = date.today()

    paid_today = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.tx_type.in_(["bet_payout", "cashback"]),
            Transaction.status == "completed",
            func.date(Transaction.created_at) == today,
        )
        .scalar()
    )

    active_today = (
        db.session.query(func.count(func.distinct(Transaction.wallet_id)))
        .filter(func.date(Transaction.created_at) == today)
        .scalar()
    )

    return render_template(
        "promotions.html",
        paid_today=float(paid_today or 0),
        active_today=active_today or 0,
    )
