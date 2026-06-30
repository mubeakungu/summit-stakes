import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/summit_stakes"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MPESA_CONSUMER_KEY"] = os.environ.get("MPESA_CONSUMER_KEY", "")
    app.config["MPESA_CONSUMER_SECRET"] = os.environ.get("MPESA_CONSUMER_SECRET", "")
    app.config["MPESA_SHORTCODE"] = os.environ.get("MPESA_SHORTCODE", "")
    app.config["MPESA_PASSKEY"] = os.environ.get("MPESA_PASSKEY", "")
    app.config["MPESA_CALLBACK_URL"] = os.environ.get("MPESA_CALLBACK_URL", "")
    app.config["MPESA_ENV"] = os.environ.get("MPESA_ENV", "sandbox")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.wallet import wallet_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(wallet_bp, url_prefix="/wallet")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
