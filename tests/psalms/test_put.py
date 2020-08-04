import unittest
import datetime
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestPut(unittest.TestCase):
    """Tests the PUT method of the psalms endpoint"""

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

    @patch("flask_app.db.MongoClient")
    def test_put_psalm(self, mock_MongoClient):
        """Tries to insert a piece"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "number": 2,
            "demoThumbnailColor": "#1482cd",
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

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.put("/psalms/add", json=test_data, headers=test_headers)
        self.assertEqual(201, r.status_code)

    def test_put_psalm_without_token(self):
        """Tries to insert a piece without a bearer token"""

        test_data = {}

        r = self.client.put("/psalms/add", json=test_data)
        self.assertEqual(401, r.status_code)

    @patch("flask_app.db.MongoClient")
    def test_put_psalm_with_bad_credentials(self, mock_MongoClient):
        """Tries to insert a piece with an incorrect token"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        self.client.post("/auth/login", json=login_data)

        test_data = {}

        test_headers = {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODk4ODkzNzMsIm5iZiI6MTU4OTg4OTM3M"
                             "ywianRpIjoiNzliNWIyM2ItNmRlNi00YjNhLWFiZmYtNWJkZjE0YWNlOGQ0IiwiZXhwIjoxNTg5ODkwMjczLCJpZG"
                             "VudGl0eSI6ImpvaG5kb2UiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.RC_f-okxnBUpI4wJpxDECTpr"
                             "-3noOi9LO0XRHh7ZBY0"
        }

        r = self.client.put("/psalms/add", json=test_data, headers=test_headers)
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

        test_data = {}

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.put("/psalms/add", data=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request body must be application/json"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_psalm_without_field(self, mock_MongoClient):
        """Tries to insert a psalm without specifying a mandatory field"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "number": 2,
            "statement": {
                "title": "Psalm Piece 2",
                "text": [
                    {
                        "key": 0
                    }
                ]
            }
        }

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.put("/psalms/add", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"demoThumbnailColor": ["Missing data for required field."],
                          "statement": {
                              "text": {
                                  "0": {
                                      "text": ["Missing data for required field."]
                                  }
                              }
                          }}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_psalm_twice(self, mock_MongoClient):
        """Tries to insert a psalm with the same number twice"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "number": 2,
            "demoThumbnailColor": "#1482cd",
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

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        self.client.put("/psalms/add", json=test_data, headers=test_headers)
        r = self.client.put("/psalms/add", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Psalm 2 already exists"}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_put_invalid_color(self, mock_MongoClient):
        """Tries to insert a psalm with an invalid thumbnail color"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "number": 2,
            "demoThumbnailColor": "#1482nd",
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

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.put("/psalms/add", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"demoThumbnailColor": ["Demo thumbnail color is not a valid hex color code"]}, r.json)

    @patch("flask_app.db.MongoClient")
    def test_put_invalid_number(self, mock_MongoClient):
        """Tries to insert a psalm with an invalid key"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        login_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        login_response = self.client.post("/auth/login", json=login_data)

        test_data = {
            "number": -2,
            "demoThumbnailColor": "#1482ad",
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

        test_headers = {
            "Authorization": "Bearer " + login_response.json.get("accessToken")
        }

        r = self.client.put("/psalms/add", json=test_data, headers=test_headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"number": ["Number must be positive"]}, r.json)


if __name__ == "__main__":
    unittest.main()
