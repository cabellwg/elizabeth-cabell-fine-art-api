import datetime
import re
from time import sleep

from flask import (
    Blueprint, request, jsonify
)
from flask_jwt_extended import (
    create_access_token, jwt_required
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

USERNAME_PATTERN = re.compile("[a-zA-Z0-9_$]+")


def build_bp(app):
    """Factory wrapper for auth blueprint"""
    bp = Blueprint("auth", __name__, url_prefix="/auth")

    # Begin route definitions

    @bp.route("/register", methods=["POST"])
    def register():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        username = request.json.get("username", None)
        password = request.json.get("password", None)
        code = request.json.get("registrationCode", None)

        if not username:
            return jsonify({"msg": "Username required"}), 400
        elif not password:
            return jsonify({"msg": "Password required"}), 400
        elif not USERNAME_PATTERN.match(username):
            return jsonify({"msg": "Username must only contain alphanumeric characters or _ or $"}), 400
        elif not code == app.config["USER_REGISTRATION_CODE"]:
            return jsonify({"msg": "Invalid registration code"}), 400

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

        if password_hash != "" and check_password_hash(password_hash, password):
            tokens = {
                "accessToken": create_access_token(identity=username)
            }
            return jsonify(tokens), 200
        else:
            sleep(0.5)

        return jsonify({"msg": "Incorrect username or password"}), 400

    @bp.route("/verify-token", methods=["POST"])
    @jwt_required
    def verify_token():
        return jsonify({}), 200

    # End route definitions

    return bp
