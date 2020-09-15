import logging

from flask import current_app, g
from pymongo import MongoClient
from sentry_sdk import capture_exception


def get_db():
    """Gets the connection to the art database"""
    if "db" not in g:
        try:
            g.db = MongoClient(current_app.config["MONGO_URI"])
            g.db.database = g.db[current_app.config["DB_NAME"]]
        except Exception as e:
            logging.exception("There was a problem accessing the database: %s", e)
            if current_app.config["ENV"] == "prod":
                capture_exception(e)
    return g.db


def close_db(_):
    """Closes the connection to the art database"""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    """Adds the close_db method as a teardown step"""
    app.teardown_appcontext(close_db)
