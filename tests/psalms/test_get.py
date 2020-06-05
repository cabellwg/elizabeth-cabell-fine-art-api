import unittest
from unittest.mock import patch

from mongomock import MongoClient

import flask_app


class TestGet(unittest.TestCase):
    """Tests the GET method of the psalms endpoint"""

    def setUp(self):
        """Runs before each test method"""
        self.client = flask_app.create_app(test_env="test").test_client()
        self.mock_db = MongoClient()

        self.test_metadata_docs = [
            {
                "series": "1",
                "demoImg": "psalms/1/demo-img.jpg",
                "demoThumbnailColor": "#1482cd",
                "thumbnail": "psalms/1/thumbnail.jpg"
            }
        ]

    @patch("flask_app.db.PyMongo")
    def test_get_psalms(self, mock_pymongo):
        """Tries to get the Psalms"""
        mock_pymongo.return_value = self.mock_db
        mock_pymongo().primary.psalms.insert_many(self.test_metadata_docs)

        expected_response = [
            {
                "series": "1",
                "demoImg": "psalms/1/demo-img.jpg",
                "demoThumbnailColor": "#1482cd",
                "thumbnail": "psalms/1/thumbnail.jpg"
            }
        ]

        r = self.client.get("/psalms/")
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected_response, r.json)


if __name__ == '__main__':
    unittest.main()
