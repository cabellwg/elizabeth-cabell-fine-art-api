from flask import Flask

from flask_app.routes import apply_routes


def create_app(test_config=None):
    """Builds the Flask app.

    :param test_config: An optional test configuration for testing.
    :return: The application.
    """
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    apply_routes(app)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run()
