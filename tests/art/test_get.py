import unittest
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestGet(unittest.TestCase):
    """Tests the GET method of the art endpoint"""

    def setUp(self):
        """Runs before each test method"""
        self.client = flask_app.create_app(test_env="test").test_client()
        self.mock_db = MongoClient()

        self.test_art_docs = [
            {
                "key": 0,
                "path": "psalms/1/p1.1.jpg",
                "title": "Psalm One – P1.1",
                "medium": "Acrylic on canvas",
                "size": "20\" x 20\"",
                "price": 200000,
                "collection": "Psalms",
                "series": "1"
            },
            {
                "key": 8,
                "path": "psalms/1/beatus-vir.jpg",
                "title": "Beatus Vir – P1.4",
                "medium": "Oil on canvas",
                "size": "20\" x 20\"",
                "price": -100,
                "collection": "Psalms",
                "series": "1"
            },
            {
                "key": 1,
                "path": "florals/orangerie.jpg",
                "title": "Orangerie",
                "medium": "Oil, framed, gold impressionist",
                "size": "18\" x 24\"",
                "price": 216000,
                "collection": "Florals"
            }
        ]

    @patch("flask_app.db.PyMongo")
    def test_get_psalms(self, mock_pymongo):
        """Tries to get the Psalms in an existing series"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        test_data = {
            "collection": "Psalms",
            "series": "1"
        }

        expected_response = [
            {
                "key": 0,
                "path": "psalms/1/p1.1.jpg",
                "title": "Psalm One – P1.1",
                "medium": "Acrylic on canvas",
                "size": "20\" x 20\"",
                "price": 2000
            },
            {
                "key": 8,
                "path": "psalms/1/beatus-vir.jpg",
                "title": "Beatus Vir – P1.4",
                "medium": "Oil on canvas",
                "size": "20\" x 20\"",
                "price": -1
            }
        ]

        r = self.client.get("/art/", json=test_data)
        self.assertEqual(expected_response, r.json)

    @patch("flask_app.db.PyMongo")
    def test_get_psalms_with_invalid_series(self, mock_pymongo):
        """Tries to get the Psalms in a nonexistent series"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        test_data = {
            "collection": "Psalms",
            "series": "999"
        }

        expected_response = {
            "msg": "No artwork matching the parameters was found"
        }

        r = self.client.get("/art/", json=test_data)
        self.assertEqual(404, r.status_code)
        self.assertEqual(expected_response, r.json)

    @patch("flask_app.db.PyMongo")
    def test_get_florals(self, mock_pymongo):
        """Tries to get the artwork from the Florals collection"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        test_data = {
            "collection": "Florals"
        }

        expected_response = [
            {
                "key": 1,
                "path": "florals/orangerie.jpg",
                "title": "Orangerie",
                "medium": "Oil, framed, gold impressionist",
                "size": "18\" x 24\"",
                "price": 2160
            }
        ]

        r = self.client.get("/art/", json=test_data)
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected_response, r.json)

    @patch("flask_app.db.PyMongo")
    def test_get_nonexistent_collection(self, mock_pymongo):
        """Tries to get the artwork from the Florals collection"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.art.insert_many(self.test_art_docs)

        test_data = {
            "collection": "There's no collection with this name"
        }

        expected_response = {
            "msg": "No artwork matching the parameters was found"
        }

        r = self.client.get("/art/", json=test_data)
        self.assertEqual(404, r.status_code)
        self.assertEqual(expected_response, r.json)

    def test_content_type(self):
        """Tries to use form data"""

        test_data = {
            "collection": "There's no collection with this name"
        }

        r = self.client.get("/art/", data=test_data)
        self.assertEqual(400, r.status_code)
        self.assertEqual({"msg": "Request body must be application/json"}, r.json)


if __name__ == '__main__':
    unittest.main()
