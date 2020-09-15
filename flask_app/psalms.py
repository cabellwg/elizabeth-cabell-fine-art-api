import os
import logging

from PIL import Image
from flask import (
    Blueprint, request, jsonify
)
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError, RAISE
from sentry_sdk import capture_exception

from .db import get_db
from .image_utils import decorate_image_filename, resize_image
from .schemas import PsalmsSchema, PsalmsListSchema


def build_bp(app):
    """Factory wrapper for psalms blueprint"""
    bp = Blueprint("psalms", __name__, url_prefix="/psalms")

    # Begin route definitions

    @bp.route("/", methods=["GET"])
    def get_psalms():
        db = get_db()

        query_res = db.database.psalms.find()
        metadata = []
        for psalm in query_res:
            psalm.pop("_id", None)
            metadata.append(psalm)

        return jsonify(metadata), 200

    @bp.route("/add", methods=["PUT"])
    @jwt_required
    def add_psalms():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            psalm = PsalmsSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        db = get_db()
        psalms = db.database.psalms

        if psalms.find_one({"number": psalm["number"]}):
            return jsonify({"msg": "Psalm {} already exists".format(psalm["number"])}), 400

        psalms.insert_one(psalm)
        return jsonify({}), 201

    @bp.route("/upload", methods=["POST"])
    @jwt_required
    def upload_image_to_metadata_image_store():
        """Uploads a psalm image to the image store. Function is idempotent."""
        if not request.content_type.startswith("multipart/form-data"):
            return jsonify({"msg": "Please use multipart/form-data"}), 400

        file = request.files.get("file")
        number = request.form.get("number")
        image_type = request.form.get("imageType")

        if not file:
            return jsonify({"msg": "Request must include a file to upload"}), 400
        if len(file.filename) == 0:
            return jsonify({"msg": "Please choose a file"}), 400
        try:
            number = int(number)
        except (TypeError, ValueError):
            return jsonify({"msg": "Please use a valid Psalm number"}), 400
        if number <= 0:
            return jsonify({"msg": "Please use a valid Psalm number"}), 400

        db = get_db()
        psalm = db.database.psalms.find_one({"number": number})
        if not psalm:
            return jsonify({"msg": "Psalm {} not found".format(number)}), 404

        try:
            with Image.open(file.stream) as im:
                base_dir = app.config["IMAGE_STORE_DIR"]

                if not os.path.isdir(base_dir):
                    os.mkdir(base_dir)

                if image_type == "thumbnail":
                    base_name = os.path.join(base_dir, psalm["thumbnailPath"] + ".jpg")
                    try:
                        im.save(base_name)
                    except IOError as e:
                        logging.exception("Error saving thumbnail image: %s", e)
                        if app.config["ENV"] == "prod":
                            capture_exception(e)
                        return jsonify({"msg": "Error saving thumbnail image"}), 500
                elif image_type == "demo":
                    base_name = os.path.join(base_dir, psalm["demoPath"])
                    try:
                        large_img = resize_image(im, 800)
                        thumbnail_img = resize_image(im, 64)
                        large_img.save(decorate_image_filename(base_name, "large"))
                        thumbnail_img.save(decorate_image_filename(base_name, "thumbnail"))
                    except IOError as e:
                        logging.exception("Error processing or saving demo image: %s", e)
                        if app.config["ENV"] == "prod":
                            capture_exception(e)
                        return jsonify({"msg": "Error saving demo image"}), 500
                else:
                    return jsonify({"msg": "Please enter a valid image type"}), 400

        except IOError:
            jsonify({"msg": "Please upload a valid image file."}), 400

        return jsonify({}), 201

    @bp.route("/update", methods=["POST"])
    @jwt_required
    def update_psalm():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        try:
            new_psalms = PsalmsListSchema().load(request.json, unknown=RAISE)
        except ValidationError as e:
            return jsonify(e.messages), 400

        psalms = get_db().database.psalms

        for new_psalm in new_psalms["psalms"]:
            psalms.replace_one({"number": new_psalm["number"]}, new_psalm)

        return jsonify({}), 200

    @bp.route("/delete", methods=["DELETE"])
    @jwt_required
    def delete_psalm():
        if not request.is_json:
            return jsonify({"msg": "Request body must be application/json"}), 400

        number = request.json.get("number")
        psalms = get_db().database.psalms
        psalms.delete_one({"number": number})
        return jsonify({}), 200

    # End route definitions

    return bp
