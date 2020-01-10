from flask import request, make_response
from flask_cors import cross_origin

from flask_app.contact import send_contact_email


def apply_routes(app):
    """Applies URL routes to the Flask app.

    :param app: The Flask app to which to apply the routes.
    """

    @app.route("/healthcheck", methods=["GET"])
    def healthcheck():
        """Route for the healthcheck."""
        return b"", 200


def jsonify_no_content(app, status):
    """Creates a response with no content with MIME type application/json.

    :param app: The Flask app
    :param status: The status code to give the response
    :return: An empty JSON response
    """
    response = make_response("", status)
    response.mimetype = app.config["JSONIFY_MIMETYPE"]

    return response
