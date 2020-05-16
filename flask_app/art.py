from flask import (
    Blueprint, request, jsonify
)
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required

from .db import get_db


def build_bp(app):
    """Factory wrapper for art blueprint"""
    bp = Blueprint("art", __name__, url_prefix="/art")

    # Begin route definitions

    @bp.route("/", methods=["GET"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["GET"])
    def get():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        db = get_db()

        collection = request.json.get("collection")
        series = request.json.get("series")

        if collection is None:
            return jsonify({
                "msg": "No artwork matching the parameters was found"
            }), 404

        if series is not None:
            query_filter = {
                "collection": collection,
                "series": series
            }
        else:
            query_filter = {
                "collection": collection
            }

        num_results = db.primary.art.count_documents(query_filter)

        if num_results == 0:
            return jsonify({
                "msg": "No artwork matching the parameters was found"
            }), 404

        query_res = db.primary.art.find(query_filter)

        metadata = []
        for piece in query_res:
            piece.pop("_id", None)
            piece.pop("collection", None)
            piece.pop("series", None)
            metadata.append(piece)

        return jsonify(metadata), 200

    @bp.route("/psalms-metadata", methods=["GET"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["GET"])
    def get_psalms_metadata():
        db = get_db()

        query_res = db.primary["psalmsMetadata"].find()
        metadata = []
        for psalm in query_res:
            psalm.pop("_id", None)
            metadata.append(psalm)

        return jsonify(metadata), 200

    # End route definitions

    return bp
