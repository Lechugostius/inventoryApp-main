from config import Config
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from flask import Flask
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Registrar los Blueprints
    app.secret_key = os.environ.get("SECRET_KEY")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp, url_prefix="/")
    return app
