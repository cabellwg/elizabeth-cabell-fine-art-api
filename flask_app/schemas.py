import re

from werkzeug.utils import secure_filename
from marshmallow import Schema, fields, post_load, validates, ValidationError, validates_schema

HEX_COLOR_PATTERN = re.compile("^#(?:[0-9a-fA-F]{3}){1,2}$")


class PieceSchema(Schema):
    """Schema for a piece of artwork"""
    key = fields.Integer(required=True)
    title = fields.String(required=True)
    medium = fields.String(required=True)
    size = fields.String(required=True)
    price = fields.Float(required=True)
    collection = fields.String(required=True)
    series = fields.String(default="None")

    @validates("key")
    def validate_key(self, value):
        if value < 0:
            raise ValidationError("Key must be nonnegative")

    @validates_schema
    def check_series(self, data, **kwargs):
        if data["collection"] == "Psalms" and data["series"] == "None":
            raise ValidationError("Series required for pieces in Psalms collection")

    @post_load
    def build_path(self, in_data, **kwargs):
        in_data["path"] = secure_filename(in_data["title"].lower())
        in_data["price"] = round(in_data["price"] * 100)
        return in_data


class PsalmsParagraphSchema(Schema):
    key = fields.Integer(required=True)
    text = fields.String(required=True)

    @validates("key")
    def validate_key(self, value):
        if value < 0:
            raise ValidationError("Key must be nonnegative")


class PsalmsStatementSchema(Schema):
    title = fields.Str(required=True)
    text = fields.List(fields.Nested(PsalmsParagraphSchema))


class PsalmsSchema(Schema):
    number = fields.Int(required=True)
    demoThumbnailColor = fields.Str(required=True)
    statement = fields.Nested(PsalmsStatementSchema)

    @validates("number")
    def validate_number(self, value):
        if value <= 0:
            raise ValidationError("Number must be positive")

    @validates("demoThumbnailColor")
    def validate_demo_thumbnail_color(self, value):
        if not re.match(HEX_COLOR_PATTERN, value):
            raise ValidationError("Demo thumbnail color is not a valid hex color code")

    @post_load
    def build_paths(self, in_data, **kwargs):
        in_data["demoPath"] = secure_filename("{}-demo".format(in_data["number"]))
        in_data["thumbnailPath"] = secure_filename("{}-thumbnail".format(in_data["number"]))
        return in_data
