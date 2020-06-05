import os

from PIL import Image
from flask import (
    Blueprint, request, jsonify
)
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError, RAISE

from .db import get_db
from .image_utils import decorate_image_filename, resize_image
from .schemas import PieceSchema


def build_bp(app):
    """Factory wrapper for art blueprint"""
    bp = Blueprint("art", __name__, url_prefix="/art")

    # Begin route definitions

    @bp.route("/", methods=["GET"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["GET"])
    def get_pieces():
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
            piece["price"] = round(float(piece["price"]) / 100, ndigits=2)
            metadata.append(piece)

        return jsonify(metadata), 200

    @bp.route("/", methods=["PUT"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["PUT"])
    @jwt_required
    def add_piece():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            piece = PieceSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        art = get_db().primary.art

        if art.find_one({"title": piece["title"]}):
            return jsonify({"msg": "Piece with title {} already exists".format(piece["title"])}), 400

        art.insert_one(piece)
        return jsonify({}), 201

    @bp.route("/update", methods=["POST"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["POST"])
    @jwt_required
    def update_piece():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            new_piece = PieceSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        art = get_db().primary.art

        result = art.replace_one({"title": new_piece["title"]}, new_piece)
        if result.matched_count != 1:
            return jsonify({"msg": "Piece with title {} does not exist".format(new_piece["title"])}), 400

        return jsonify({}), 200

    @bp.route("/upload", methods=["POST"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["POST"])
    @jwt_required
    def upload_piece_to_image_store():
        """Uploads an image to the image store. Function is idempotent."""
        if not request.content_type.startswith("multipart/form-data"):
            return jsonify({"msg": "Please use multipart/form-data"}), 400

        file = request.files.get("file")
        title = request.form.get("title")

        if not file:
            return jsonify({"msg": "Request must include a file to upload"}), 400
        if len(file.filename) == 0:
            return jsonify({"msg": "Please choose a file"}), 400
        if title is None or len(title) == 0:
            return jsonify({"msg": "Please specify a piece"}), 400

        art = get_db().primary.art
        piece = art.find_one({"title": title})
        if not piece:
            return jsonify({"msg": "Piece with title \"{}\" not found".format(title)}), 404

        try:
            with Image.open(file.stream) as im:
                base_dir = app.config["IMAGE_STORE_DIR"]

                if not os.path.isdir(base_dir):
                    os.mkdir(base_dir)

                base_name = os.path.join(base_dir, piece["path"])

                full_img = im
                large_img = resize_image(im, 1000)
                thumbnail_img = resize_image(im, 64)

                full_img.save(decorate_image_filename(base_name, "full"))
                large_img.save(decorate_image_filename(base_name, "large"))
                thumbnail_img.save(decorate_image_filename(base_name, "thumbnail"))
        except IOError:
            return jsonify({"msg": "Please upload a valid image file."}), 400

        return jsonify({}), 201

    # End route definitions

    return bp
