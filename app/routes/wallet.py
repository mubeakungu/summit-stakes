from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.wallet import Transaction
from app.services.mpesa import stk_push, normalize_phone

wallet_bp = Blueprint("wallet", __name__)

MIN_DEPOSIT = 10
MAX_DEPOSIT = 150000  # keep in line with your BCLB-approved limits / daily caps


@wallet_bp.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            flash("Enter a valid amount.", "error")
            return redirect(url_for("wallet.deposit"))

        if amount < MIN_DEPOSIT or amount > MAX_DEPOSIT:
            flash(f"Deposit amount must be between {MIN_DEPOSIT} and {MAX_DEPOSIT} KES.", "error")
            return redirect(url_for("wallet.deposit"))

        phone = normalize_phone(request.form.get("phone", current_user.phone))

        tx = Transaction(
            wallet_id=current_user.wallet.id,
            tx_type="deposit",
            amount=amount,
            status="pending",
            phone_used=phone,
        )
        db.session.add(tx)
        db.session.commit()

        try:
            result = stk_push(phone, amount, account_reference=f"DEP{tx.id}")
            tx.mpesa_checkout_request_id = result.get("CheckoutRequestID")
            tx.reference = result.get("MerchantRequestID")
            db.session.commit()
            flash("Check your phone to complete the M-Pesa payment.", "success")
        except Exception:
            tx.status = "failed"
            db.session.commit()
            flash("Could not reach M-Pesa right now. Try again shortly.", "error")

        return redirect(url_for("wallet.deposit"))

    return render_template("wallet/deposit.html")


@wallet_bp.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    """
    Safaricom Daraja calls this with the result of the STK push.
    Auto-approves the deposit and credits the wallet on success.
    """
    payload = request.get_json(force=True, silent=True) or {}
    stk_callback = payload.get("Body", {}).get("stkCallback", {})

    checkout_id = stk_callback.get("CheckoutRequestID")
    result_code = stk_callback.get("ResultCode")

    tx = Transaction.query.filter_by(mpesa_checkout_request_id=checkout_id).first()
    if not tx:
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200

    if result_code == 0:
        items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        meta = {i["Name"]: i.get("Value") for i in items}

        tx.status = "completed"
        tx.mpesa_receipt = meta.get("MpesaReceiptNumber")

        wallet = tx.wallet
        wallet.balance = (wallet.balance or 0) + tx.amount
        db.session.commit()
    else:
        tx.status = "failed"
        db.session.commit()

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200
