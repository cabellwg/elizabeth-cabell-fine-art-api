from decimal import Decimal
from bson.decimal128 import Decimal128
from bson.codec_options import TypeCodec

from flask import current_app, g
from flask_pymongo import PyMongo


def get_db():
    """Gets the connection to the art database"""
    if "db" not in g:
        g.db = PyMongo(current_app)
    return g.db


def close_db(_):
    """Closes the connection to the art database"""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    """Adds the close_db method as a teardown step"""
    app.teardown_appcontext(close_db)
