import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
