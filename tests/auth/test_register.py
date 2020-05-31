import unittest
import datetime
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestRegister(unittest.TestCase):
    """Tests the registration endpoint"""

    def setUp(self):
        """Runs before each test method"""
        self.client = flask_app.create_app(test_env="test").test_client()
        self.mock_db = MongoClient()

        self.test_user_docs = [
            {
                "username": "janedoe",
                "password": "some-hashy-shit",
                "created": datetime.datetime.utcnow(),
                "passwordLastUpdated": datetime.datetime.utcnow()
            },
            {
                "username": "joshdoe",
                "password": "some-hashy-shit-or-something",
                "created": datetime.datetime.utcnow(),
                "passwordLastUpdated": datetime.datetime.utcnow()
            }
        ]

    @patch("flask_app.db.PyMongo")
    def test_registration_successful(self, mock_pymongo):
        """Tests the registration endpoint with good login info"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.auth.insert_many(self.test_user_docs)

        test_data = {
            "username": "johndoe",
            "password": "hunter2",
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(200, r.status_code)
        self.assertIsNotNone(self.mock_db.primary.auth.find_one({"username": "johndoe"}))

    def test_registration_without_password(self):
        """Tests the registration endpoint with failed login info"""

        test_data = {
            "username": "facebookmygrandsonnathan"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Password required"}, r.json)

    def test_registration_without_username(self):
        """Tests the registration endpoint without a username"""

        test_data = {
            "password": "Password1"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Username required"}, r.json)

    def test_registration_dirty(self):
        """Tests the registration endpoint with an invalid username"""

        test_data = {
            "username": "*\"}); db.auth.delete_many({})",
            "password": "hunter2"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Username must only contain alphanumeric characters or _ or $"}, r.json)

    def test_registration_with_non_json(self):
        """Tests the authentication endpoint with the wrong data type"""
        test_data = {
            "username": "johndoe",
            "password": "hunter2"
        }

        r = self.client.post("/auth/register", data=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request body must be application/json"}, r.json)


if __name__ == '__main__':
    unittest.main()
