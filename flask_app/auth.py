import datetime
import re

from flask import (
    Blueprint, request, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import cross_origin
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_refresh_token_required,
    get_jwt_identity
)

from .db import get_db

USERNAME_PATTERN = re.compile("[a-zA-Z0-9_$@?!]+")


def build_bp(app):
    """Factory wrapper for auth blueprint"""
    bp = Blueprint("auth", __name__, url_prefix="/auth")

    # Begin route definitions

    @bp.route("/register", methods=["POST"])
    @cross_origin(origins=app.config["ALLOWED_ORIGINS"],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["POST"])
    def register():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if not username:
            return jsonify({"msg": "Username required"}), 400
        elif not password:
            return jsonify({"msg": "Password required"}), 400
        elif not USERNAME_PATTERN.match(username):
            return jsonify({"msg": "Username must only contain alphanumeric characters or _ or $"}), 400

        auth = get_db().database.apiAuth
        if auth.find_one({"username": username}):
            return jsonify({"msg": "User {} is already registered".format(username)}), 400

        auth.insert_one({
            "username": username,
            "password": generate_password_hash(password),
            "created": datetime.datetime.utcnow(),
            "passwordLastUpdated": datetime.datetime.utcnow()
        })

        return jsonify({"msg": "User created, you may now log in"}), 200

    @bp.route("/login", methods=["POST"])
    @cross_origin(origins=app.config["ALLOWED_ORIGINS"],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["POST"])
    def login():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if not username:
            return jsonify({"msg": "Username required for login"}), 400

        # Check user credentials
        auth = get_db().database.apiAuth
        try:
            user = auth.find_one({"username": username})
        except Exception as e:
            print(e)
        password_hash = ""
        if user is not None and user.get("password") is not None:
            password_hash = user["password"]

        if check_password_hash(password_hash, password):
            tokens = {
                "access_token": create_access_token(identity=username),
                "refresh_token": create_refresh_token(identity=username)
            }
            return jsonify(tokens), 200

        return jsonify({"msg": "Incorrect username or password"}), 400

    @bp.route("/refresh", methods=["POST"])
    @cross_origin(origins=app.config["ALLOWED_ORIGINS"],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["POST"])
    @jwt_refresh_token_required
    def refresh():
        current_user = get_jwt_identity()
        ret = {
            "access_token": create_access_token(identity=current_user)
        }
        return jsonify(ret), 200

    # End route definitions

    return bp
