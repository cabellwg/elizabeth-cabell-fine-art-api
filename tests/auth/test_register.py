import datetime
import unittest
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

    @patch("flask_app.db.MongoClient")
    def test_registration_successful(self, mock_MongoClient):
        """Tests the registration endpoint with good login info"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        test_data = {
            "username": "johndoe",
            "password": "hunter2",
            "registrationCode": "test-registration-code"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(200, r.status_code)
        self.assertIsNotNone(self.mock_db.test.apiAuth.find_one({"username": "johndoe"}))

    @patch("flask_app.db.MongoClient")
    def test_registration_with_wrong_rcode(self, mock_MongoClient):
        """Tests the registration endpoint with the wrong registration code"""
        mock_MongoClient.return_value = self.mock_db
        mock_MongoClient().test.apiAuth.insert_many(self.test_user_docs)

        test_data = {
            "username": "johndoe",
            "password": "hunter2",
            "registrationCode": "wrong-registration-code"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Invalid registration code"}, r.json)

    def test_registration_without_password(self):
        """Tests the registration endpoint with failed login info"""

        test_data = {
            "username": "facebookmygrandsonnathan",
            "registrationCode": "test-registration-code"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Password required"}, r.json)

    def test_registration_without_username(self):
        """Tests the registration endpoint without a username"""

        test_data = {
            "password": "Password1",
            "registrationCode": "test-registration-code"
        }

        r = self.client.post("/auth/register", json=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Username required"}, r.json)

    def test_registration_dirty(self):
        """Tests the registration endpoint with an invalid username"""

        test_data = {
            "username": "*\"}); db.apiAuth.delete_many({})",
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
