import unittest
import datetime
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestUpdate(unittest.TestCase):
    """Tests the POST method of the art/update endpoint"""

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
                "path": "psalms/1/p1.1.jpg",
                "title": "Test Piece",
                "medium": "Acrylic on canvas",
                "size": "20\" x 20\"",
                "price": 200000,
                "collection": "Florals"
            },
            {
                "key": 0,
                "path": "psalms/1/p1.1.jpg",
                "title": "Test Psalm",
                "medium": "Acrylic on canvas",
                "size": "20\" x 20\"",
                "price": 200000,
                "collection": "Psalms",
                "series": "1"
            }
        ]

    @patch("flask_app.db.MongoClient")
    def test_update_piece(self, mock_MongoClient):
        """Tries to update a piece"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.art.insert_many(self.test_art_docs)

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
            "price": 1000.00,
            "collection": "Florals"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.post("/art/update", json=test_data, headers=test_headers)
        self.assertEqual(200, r.status_code)

        new_piece = mock_MongoClient().test.art.find_one({"title": "Test Piece"})
        self.assertEqual(100000, new_piece["price"])

    @patch("flask_app.db.MongoClient")
    def test_update_psalm(self, mock_MongoClient):
        """Tries to replace a piece"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)
        mock_MongoClient().test.art.insert_many(self.test_art_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "title": "Test Psalm",
            "medium": "Acrylic on canvas",
            "size": "test",
            "price": 1000.00,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.post("/art/update", json=test_data, headers=test_headers)
        self.assertEqual(200, r.status_code)

        new_piece = mock_MongoClient().test.art.find_one({"title": "Test Psalm"})
        self.assertEqual(100000, new_piece["price"])
        self.assertEqual("test", new_piece["size"])

    def test_update_piece_without_token(self):
        """Tries to replace a piece without a bearer token"""

        test_data = {
            "key": 0,
            "title": "Test Piece",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000.00,
            "collection": "Psalms",
            "series": "1"
        }

        r = self.client.post("/art/update", json=test_data)
        self.assertEqual(401, r.status_code)

    @patch("flask_app.db.MongoClient")
    def test_update_piece_with_bad_credentials(self, mock_MongoClient):
        """Tries to replace a piece with an incorrect token"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

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
            "price": 2000.00,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODk4ODkzNzMsIm5iZiI6MTU4OTg4OTM3M"
                             "ywianRpIjoiNzliNWIyM2ItNmRlNi00YjNhLWFiZmYtNWJkZjE0YWNlOGQ0IiwiZXhwIjoxNTg5ODkwMjczLCJpZG"
                             "VudGl0eSI6ImpvaG5kb2UiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.RC_f-okxnBUpI4wJpxDECTpr"
                             "-3noOi9LO0XRHh7ZBY0"
        }

        r = self.client.post("/art/update", json=test_data, headers=test_headers)
        self.assertEqual(422, r.status_code)

    @patch("flask_app.db.MongoClient")
    def test_content_type(self, mock_MongoClient):
        """Tries to use form data"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "collection": "There's no collection with this name"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.post("/art/update", data=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request body must be application/json"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_nonexistent_piece(self, mock_MongoClient):
        """Tries to replace a piece that doesn't exist"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "key": 0,
            "title": "Test Piece 2",
            "medium": "Acrylic on canvas",
            "size": "20\" x 20\"",
            "price": 2000.00,
            "collection": "Psalms",
            "series": "1"
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        self.client.post("/art/update", json=test_data, headers=test_headers)
        r = self.client.post("/art/update", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Piece with title Test Piece 2 does not exist"}, r.json)


if __name__ == "__main__":
    unittest.main()
