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
    """Tests uploading an image to the art endpoint"""

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

        self.test_psalm_docs = [
            {
                "number": 2,
                "demoPath": "test_demo_path",
                "demoThumbnailColor": "#1482cd",
                "thumbnailPath": "test_thumbnail_path",
                "statement": {
                    "title": "Psalm Piece 2",
                    "text": [
                        {
                            "key": 0,
                            "text": "Test paragraph"
                        }
                    ]
                }
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

    @patch("flask_app.db.MongoClient")
    def test_upload_thumbnail(self, mock_MongoClient):
        """Tries to upload a thumbnail image"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "number": 2,
                "imageType": "thumbnail"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(201, r.status_code)

            base_dir = self.client.application.config["IMAGE_STORE_DIR"]
            self.assertTrue(os.path.exists(os.path.join(base_dir, "test_thumbnail_path.jpg")))

    @patch("flask_app.db.MongoClient")
    def test_upload_with_missing_psalm(self, mock_MongoClient):
        """Tries to upload a thumbnail image"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "number": 1,
                "imageType": "thumbnail"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(404, r.status_code)
            self.assertEqual({"msg": "Psalm 1 not found"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_upload_demo(self, mock_MongoClient):
        """Tries to upload a demo image"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "number": 2,
                "imageType": "demo"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(201, r.status_code)

            base_dir = self.client.application.config["IMAGE_STORE_DIR"]
            self.assertTrue(os.path.exists(os.path.join(base_dir, "test_demo_path-large.jpg")))
            self.assertTrue(os.path.exists(os.path.join(base_dir, "test_demo_path-thumbnail.jpg")))

    @patch("flask_app.db.MongoClient")
    def test_upload_image_with_invalid_number(self, mock_MongoClient):
        """Tries to upload an image with an invalid Psalm number"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "number": -2,
                "imageType": "demo"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(400, r.status_code)
            self.assertEqual({"msg": "Please use a valid Psalm number"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_upload_image_with_invalid_number_type(self, mock_MongoClient):
        """Tries to upload an image with an invalid Psalm number type"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "number": "NaN",
                "imageType": "demo"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(400, r.status_code)
            self.assertEqual({"msg": "Please use a valid Psalm number"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_upload_piece_with_invalid_type(self, mock_MongoClient):
        """Tries to upload an image with an invalid type"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_data = {
                "number": 2,
                "imageType": "WRONG!"
            }

            test_headers = {
                "Content-Type": "multipart/form-data",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload", data=test_data,
                                     method="POST", headers=test_headers)
            builder.files.add_file("file", im, "test.jpg", "image/jpeg")

            r = self.client.open(builder)
            self.assertEqual(400, r.status_code)
            self.assertEqual({"msg": "Please enter a valid image type"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_upload_with_invalid_content_type(self, mock_MongoClient):
        """Tries to upload an image with the wrong content type"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        with open("test.jpg", mode="rb") as im:
            test_headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + login_response.json.get("accessToken")
            }

            builder = EnvironBuilder(app=self.client.application, path="/psalms/upload",
                                     method="POST", headers=test_headers)

            r = self.client.open(builder)
            self.assertEqual(400, r.status_code)
            self.assertEqual({"msg": "Please use multipart/form-data"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_upload_without_file(self, mock_MongoClient):
        """Tries to upload a piece without an image file"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.psalms.insert_many(self.test_psalm_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "number": 2,
            "imageType": "demo"
        }

        test_headers = {
            "Content-Type": "multipart/form-data",
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.post("/psalms/upload", data=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request must include a file to upload"}, r.json)
