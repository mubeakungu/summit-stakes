from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models.user import User
from app.models.wallet import Wallet

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        dob_raw = request.form.get("date_of_birth", "")

        if not all([phone, full_name, password, dob_raw]):
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))

        try:
            dob = datetime.strptime(dob_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Enter a valid date of birth.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(phone=phone).first():
            flash("That phone number is already registered.", "error")
            return redirect(url_for("auth.register"))

        user = User(phone=phone, full_name=full_name, date_of_birth=dob)
        user.set_password(password)

        # Hard stop on the server side - never trust client-side age checks alone
        if not user.is_of_legal_age():
            flash("You must be 18 or older to register.", "error")
            return redirect(url_for("auth.register"))

        db.session.add(user)
        db.session.flush()

        wallet = Wallet(user_id=user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()

        flash("Account created. Log in to continue.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(phone=phone).first()
        if not user or not user.check_password(password):
            flash("Invalid phone number or password.", "error")
            return redirect(url_for("auth.login"))

        if user.is_self_excluded:
            flash("This account is currently self-excluded and cannot log in.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("main.promotions"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
