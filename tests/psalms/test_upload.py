import datetime
import os
import shutil
import unittest
from unittest.mock import patch

from PIL import Image
from flask.testing import EnvironBuilder
from mongomock import MongoClient

import flask_app


class TestPut(unittest.TestCase):
    """Tests uploading an image to the psalms endpoint"""

    def setUp(self):
        """Runs before each test method"""
        self.client = flask_app.create_app(test_env="test").test_client()
        self.mock_db = MongoClient()

        self.test_user_docs = [
            {
                "username": "johndoe",
                "password": "pbkdf2:sha256:150000$WvnI6aK2$d9fe24da37a15003ef18"
                            "2f9c2d48da67615b5d92c7a143d3e73c963b38799839",
                "created": datetime.datetime.utcnow(),
                "passwordLastUpdated": datetime.datetime.utcnow()
            }
        ]

        self.test_art_docs = [
            {
                "key": 0,
                "title": "Test Piece",
                "path": "test_piece",
                "medium": "Acrylic on canvas",
                "size": "20\" x 20\"",
                "price": 200000,
                "collection": "Florals"
            }
        ]

        test_image = Image.new(mode="RGB", size=(1600, 1200))
        test_image.save("test.jpg")

    def tearDown(self):
        """Runs after each test method"""
        os.remove("test.jpg")
        base_dir = self.client.application.config["IMAGE_STORE_DIR"]
        if os.path.isdir(base_dir):
            shutil.rmtree(base_dir)

    @patch("flask_app.db.PyMongo")
    def test_upload_piece(self, mock_pymongo):
        """Tries to upload a piece"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "title": "Test Piece"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("access_token")
            }

            builder = EnvironBuilder(app=self.client.application, path="/art/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(201, r.status_code)

    @patch("flask_app.db.PyMongo")
    def test_upload_piece_without_title(self, mock_pymongo):
        """Tries to upload a piece without giving a title"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("access_token")
            }

            builder = EnvironBuilder(app=self.client.application, path="/art/upload",
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(400, r.status_code)
            self.assertEqual({"msg": "Please specify a piece"}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_upload_piece_with_empty_title(self, mock_pymongo):
        """Tries to upload a piece with an empty string as the title"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("access_token")
            }

            test_data = {
                "title": ""
            }

            builder = EnvironBuilder(app=self.client.application, path="/art/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(400, r.status_code)
            self.assertEqual({"msg": "Please specify a piece"}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_upload_piece_with_invalid_title(self, mock_pymongo):
        """Tries to upload a piece with a title that doesn't exist"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("access_token")
            }

            test_data = {
                "title": "N'existe pas"
            }

            builder = EnvironBuilder(app=self.client.application, path="/art/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(404, r.status_code)
            self.assertEqual({"msg": "Piece with title \"N'existe pas\" not found"}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_upload_with_invalid_content_type(self, mock_pymongo):
        """Tries to upload a piece with the wrong content type"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        builder = EnvironBuilder(app=self.client.application, path="/art/upload",
                                 method="POST", headers=test_headers)

        r = self.client.open(builder)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Please use multipart/form-data"}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_upload_without_file(self, mock_pymongo):
        """Tries to upload a piece without an image file"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "title": "test title"
        }

        test_headers = {
            "Content-Type": "multipart/form-data",
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.post("/art/upload", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request must include a file to upload"}, r.json)

