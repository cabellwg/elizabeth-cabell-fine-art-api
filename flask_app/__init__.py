import logging
import os

import sentry_sdk
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sentry_sdk import capture_exception
from sentry_sdk.integrations.flask import FlaskIntegration


def create_app(test_env=None):
    """Builds the Flask app.

    :return: The application.
    """
    app = Flask(__name__)

    env = test_env if test_env is not None else os.environ["ENV"]
    app.config["ENV"] = env

    if env == "prod":
        app.config.from_object("config.ProdConfig")
    elif env == "test":
        app.config.from_object("config.TestConfig")
    else:
        app.config.from_object("config.DevConfig")

    if app.secret_key is None or app.config["JWT_SECRET_KEY"] is None:
        raise ValueError("Could not get application secret keys")

    if env == "prod":
        sentry_sdk.init(
                dsn=app.config["SENTRY_DSN"],
                integrations=[FlaskIntegration()]
        )

    CORS(app, origins=app.config["ALLOWED_ORIGINS"],
         allow_headers=["Content-Type", "Authorization"])
    JWTManager(app)

    @app.route("/healthcheck", methods=["GET"])
    def healthcheck():
        """Route for the healthcheck."""
        return b"", 200

    @app.errorhandler(500)
    def server_error(e):
        logging.exception("An error occurred during a request: %s", e)
        if env == "prod":
            capture_exception(e)
        return "An internal error occurred", 500

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.build_bp(app))

    from . import art
    app.register_blueprint(art.build_bp(app))

    from . import psalms
    app.register_blueprint(psalms.build_bp(app))

    return app


if __name__ == "__main__":
    application = create_app(test_env="dev")
    application.run()
