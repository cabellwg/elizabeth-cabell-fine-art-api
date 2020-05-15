import unittest
import datetime
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestLogin(unittest.TestCase):
    """Tests the login endpoint"""

    def setUp(self):
        """Runs before each test method"""
        self.client = flask_app.create_app(test_env="test").test_client()
        self.mock_db = MongoClient()

        self.test_user_docs = [
            {
                "username": "janedoe",
                "password": "her-password-will-be-wrong",
                "created": datetime.datetime.utcnow(),
                "passwordLastUpdated": datetime.datetime.utcnow()
            },
            {
                "username": "johndoe",
                "password": "pbkdf2:sha256:150000$WvnI6aK2$d9fe24da37a15003ef18"
                            "2f9c2d48da67615b5d92c7a143d3e73c963b38799839",
                "created": datetime.datetime.utcnow(),
                "passwordLastUpdated": datetime.datetime.utcnow()
            }
        ]

    @patch("flask_app.db.PyMongo")
    def test_login_successful(self, mock_pymongo):
        """Tests the login endpoint with good user credentials"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        test_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        r = self.client.post("/auth/login", json=test_data)
        self.assertEqual(200, r.status_code)
        self.assertIsNotNone(r.json["access_token"])
        self.assertIsNotNone(r.json["refresh_token"])

    @patch("flask_app.db.PyMongo")
    def test_login_wrong_password(self, mock_pymongo):
        """Tests the login endpoint with incorrect password"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        test_data = {
            "username": "johndoe",
            "password": "hunter"
        }

        r = self.client.post("/auth/login", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertIsNone(r.json.get("access_token"))
        self.assertIsNone(r.json.get("refresh_token"))
        self.assertEqual("Incorrect username or password", r.json["msg"])

    @patch("flask_app.db.PyMongo")
    def test_login_wrong_username(self, mock_pymongo):
        """Tests the login endpoint with incorrect username"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        test_data = {
            "username": "1337",
            "password": "hunter2"
        }

        r = self.client.post("/auth/login", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertIsNone(r.json.get("access_token"))
        self.assertIsNone(r.json.get("refresh_token"))
        self.assertEqual("Incorrect username or password", r.json["msg"])

    @patch("flask_app.db.PyMongo")
    def test_login_without_username(self, mock_pymongo):
        """Tests the login endpoint without a username"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        test_data = {
            "password": "hunter2"
        }

        r = self.client.post("/auth/login", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertIsNone(r.json.get("access_token"))
        self.assertIsNone(r.json.get("refresh_token"))
        self.assertEqual("Username required for login", r.json["msg"])

    @patch("flask_app.db.PyMongo")
    def test_login_with_non_json(self, mock_pymongo):
        """Tests the login endpoint with incorrect data type"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        test_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        r = self.client.post("/auth/login", data=test_data)
        self.assertEqual(400, r.status_code)
        self.assertIsNone(r.json.get("access_token"))
        self.assertIsNone(r.json.get("refresh_token"))
        self.assertEqual("Request body must be application/json", r.json["msg"])


if __name__ == '__main__':
    unittest.main()
