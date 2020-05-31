import os

from PIL import Image
from flask import (
    Blueprint, request, jsonify
)
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError, RAISE

from .db import get_db
from .schemas import PsalmsSchema
from .image_utils import decorate_image_filename, resize_image


def build_bp(app):
    """Factory wrapper for psalms blueprint"""
    bp = Blueprint("psalms", __name__, url_prefix="/psalms")

    # Begin route definitions

    @bp.route("/", methods=["GET"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["GET"])
    def get_psalms():
        db = get_db()

        query_res = db.primary.psalms.find()
        metadata = []
        for psalm in query_res:
            psalm.pop("_id", None)
            metadata.append(psalm)

        return jsonify(metadata), 200

    @bp.route("/", methods=["PUT"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["PUT"])
    @jwt_required
    def add_psalms():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            psalm = PsalmsSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        db = get_db()
        psalms = db.primary.psalms

        if psalms.find_one({"number": psalm["number"]}):
            return jsonify({"msg": "Psalm {} already exists".format(psalm["number"])}), 400

        psalms.insert_one(psalm)
        return jsonify({}), 201

    @bp.route("/upload", methods=["POST"])
    @cross_origin(origins=[app.config["ALLOWED_ORIGINS"]],
                  allow_headers=["Content-Type", "Authorization"],
                  methods=["POST"])
    @jwt_required
    def upload_image_to_metadata_image_store():
        """Uploads a psalm image to the image store. Function is idempotent."""
        file = request.files.get("file")
        number = request.data.get("number")
        image_type = request.data.get("imageType")

        if not file:
            return jsonify({"msg": "Request must include a file to upload"}), 400
        if len(file.filename) == 0:
            return jsonify({"msg": "Please choose a file"}), 400

        db = get_db()
        psalm = db.primary.psalms.find_one({"number": number})
        if not psalm:
            return jsonify({"msg": "Psalm {} not found".format(number)}), 404

        try:
            with Image.open(file) as im:
                if image_type == "thumbnail":
                    base = os.path.join(app.config["IMAGE_STORE_DIR"], psalm["thumbnailPath"])
                    im.save(base)
                elif image_type == "demo":
                    base = os.path.join(app.config["IMAGE_STORE_DIR"], psalm["demoPath"])
                    full_img = im
                    large_img = resize_image(im, 800)
                    thumbnail_img = resize_image(im, 64)
                    full_img.save(decorate_image_filename(base, "full"))
                    large_img.save(decorate_image_filename(base, "large"))
                    thumbnail_img.save(decorate_image_filename(base, "thumbnail"))
                else:
                    return jsonify({"msg": "Please enter a valid image type"}), 400

        except IOError:
            jsonify({"msg": "Please upload a valid image file."}), 400

        return jsonify({}), 201

    # End route definitions

    return bp
