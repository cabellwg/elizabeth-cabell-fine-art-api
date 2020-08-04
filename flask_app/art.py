import os

from PIL import Image
from flask import (
    Blueprint, request, jsonify
)
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError, RAISE

from .db import get_db
from .image_utils import decorate_image_filename, resize_image
from .schemas import PiecesSchema, PieceSchema


def build_bp(app):
    """Factory wrapper for art blueprint"""
    bp = Blueprint("art", __name__, url_prefix="/art")

    # Begin route definitions

    @bp.route("/", methods=["POST"])
    def get_pieces():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        db = get_db().database

        query_filter = request.json
        num_results = db.art.count_documents(query_filter)

        if num_results == 0:
            return jsonify({
                "msg": "No artwork matching the parameters was found"
            }), 404

        query_res = db.art.find(query_filter)

        metadata = []
        for piece in query_res:
            piece.pop("_id", None)
            piece.pop("collection", None)
            piece.pop("series", None)
            piece["price"] = round(float(piece["price"]) / 100, ndigits=2)
            metadata.append(piece)

        return jsonify(metadata), 200

    @bp.route("/add", methods=["PUT"])
    @jwt_required
    def add_piece():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            piece = PieceSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        art = get_db().database.art

        if art.find_one({"title": piece["title"]}):
            return jsonify({"msg": "Piece with title {} already exists".format(piece["title"])}), 400

        art.insert_one(piece)
        return jsonify({}), 201

    @bp.route("/update", methods=["POST"])
    @jwt_required
    def update_piece():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            new_pieces = PiecesSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        art = get_db().database.art

        for new_piece in new_pieces["pieces"]:
            art.replace_one({"title": new_piece["title"]}, new_piece)

        return jsonify({}), 200

    @bp.route("/delete", methods=["DELETE"])
    @jwt_required
    def delete_piece():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        title = request.json.get("title")
        art = get_db().database.art
        art.delete_one({"title": title})
        return jsonify({}), 200

    @bp.route("/upload", methods=["POST"])
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

        art = get_db().database.art
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
