from flask import current_app, g
from pymongo import MongoClient


def get_db():
    """Gets the connection to the art database"""
    if "db" not in g:
        g.db = MongoClient(current_app.config["MONGO_URI"])
        g.db.database = g.db[current_app.config["DB_NAME"]]
    return g.db


def close_db(_):
    """Closes the connection to the art database"""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    """Adds the close_db method as a teardown step"""
    app.teardown_appcontext(close_db)
