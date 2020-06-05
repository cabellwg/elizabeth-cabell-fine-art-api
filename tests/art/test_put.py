import unittest
import datetime
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestPut(unittest.TestCase):
    """Tests the PUT method of the art endpoint"""

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

    @patch("flask_app.db.PyMongo")
    def test_put_piece(self, mock_pymongo):
        """Tries to insert a piece"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000,
            "collection": "Florals"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(201, r.status_code)

    @patch("flask_app.db.PyMongo")
    def test_put_psalm(self, mock_pymongo):
        """Tries to insert a piece"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(201, r.status_code)

    def test_put_piece_without_token(self):
        """Tries to insert a piece without a bearer token"""

        test_data = {
            "key": 0,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000,
            "collection": "Psalms",
            "series": "1"
        }

        r = self.client.put("/art/", json=test_data)
        self.assertEqual(401, r.status_code)

    @patch("flask_app.db.PyMongo")
    def test_put_piece_with_bad_credentials(self, mock_pymongo):
        """Tries to insert a piece with an incorrect token"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODk4ODkzNzMsIm5iZiI6MTU4OTg4OTM3M"
                             "ywianRpIjoiNzliNWIyM2ItNmRlNi00YjNhLWFiZmYtNWJkZjE0YWNlOGQ0IiwiZXhwIjoxNTg5ODkwMjczLCJpZG"
                             "VudGl0eSI6ImpvaG5kb2UiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.RC_f-okxnBUpI4wJpxDECTpr"
                             "-3noOi9LO0XRHh7ZBY0"
        }

        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(422, r.status_code)

    @patch("flask_app.db.PyMongo")
    def test_content_type(self, mock_pymongo):
        """Tries to use form data"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "collection": "There's no collection with this name"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.put("/art/", data=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request body must be application/json"}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_piece_without_field(self, mock_pymongo):
        """Tries to insert a piece without specifying a mandatory field"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"title": ["Missing data for required field."]}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_piece_twice(self, mock_pymongo):
        """Tries to insert a piece with the same title twice"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        self.client.put("/art/", json=test_data, headers=test_headers)
        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Piece with title Test Piece already exists"}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_piece_wrong_key_and_price_type(self, mock_pymongo):
        """Tries to insert a piece with a string key"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": "WRONG!",
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": "$2,000.00",
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"key": ["Not a valid integer."], "price": ["Not a valid number."]}, r.json)

    @patch("flask_app.db.PyMongo")
    def test_piece_wrong_key_value(self, mock_pymongo):
        """Tries to insert a piece with a negative key value"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": -2,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 200000,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("access_token")
        }

        r = self.client.put("/art/", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"key": ["Key must be nonnegative"]}, r.json)


if __name__ == "__main__":
    unittest.main()
