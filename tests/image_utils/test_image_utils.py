import unittest

from PIL import Image

from flask_app.image_utils import *


class TestImageUtils(unittest.TestCase):
    """Tests the image utility functions"""

    def test_resize_image_landscape(self):
        """Resizes a landscape image"""
        test_image = Image.new(mode="RGB", size=(30, 20))

        new_image = resize_image(test_image, 15)

        self.assertEqual(15, new_image.width)
        self.assertEqual(10, new_image.height)

    def test_resize_image_portrait(self):
        """Resizes a portrait image"""
        test_image = Image.new(mode="RGB", size=(20, 30))

        new_image = resize_image(test_image, 15)

        self.assertEqual(10, new_image.width)
        self.assertEqual(15, new_image.height)

    def test_resize_image_square(self):
        """Resizes a square image"""
        test_image = Image.new(mode="RGB", size=(20, 20))

        new_image = resize_image(test_image, 15)

        self.assertEqual(15, new_image.width)
        self.assertEqual(15, new_image.height)

    def test_decorate_image_filename(self):
        """Tests filename decoration"""
        self.assertEqual("test-big.jpg", decorate_image_filename("test", "big"))
