from flask import Flask
from .extensions import db, migrate, limiter, redis_client
from .routes import task_routes, user_routes
from sqlalchemy.exc import OperationalError
import time

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Connection Pooling settings (should be BEFORE db.init_app)
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800  # 30 minutes
    }

    #  Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    #  Retry mechanism for DB connection
    with app.app_context():
        retries = 5
        while retries:
            try:
                db.engine.connect()
                print(" Connected to DB successfully")
                break
            except OperationalError as e:
                retries -= 1
                print(f" DB connection failed: {e}")
                print(f" Retrying in 2s... ({5 - retries}/5)")
                time.sleep(2)
        else:
            raise Exception(" DB connection failed after 5 retries.")

    #  Register Blueprints
    app.register_blueprint(task_routes.bp)
    app.register_blueprint(user_routes.user_bp)

    return app
