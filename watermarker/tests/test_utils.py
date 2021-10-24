# -*- coding: utf-8 -*-

import os

from django.test import TestCase
from PIL import Image

from ..utils import watermark


class UtilsTestCase(TestCase):
    def setUp(self):
        self.im = Image.open(os.path.join(os.path.dirname(__file__), "test.png"))
        self.mark = Image.open(os.path.join(os.path.dirname(__file__), "overlay.png"))

    def test_tile(self):
        watermark(self.im, self.mark, tile=True, opacity=0.5, rotation=30).save(
            os.path.join(os.path.dirname(__file__), "test1.png")
        )

    def test_scale(self):
        watermark(self.im, self.mark, scale="F").save(os.path.join(os.path.dirname(__file__), "test2.png"))

    def test_grayscale(self):
        watermark(self.im, self.mark, position=(100, 100), opacity=0.5, greyscale=True, rotation=-45).save(
            os.path.join(os.path.dirname(__file__), "test3.png")
        )

    def test_position(self):
        watermark(self.im, self.mark, position="C", tile=False, opacity=0.2, scale=2, rotation=30).save(
            os.path.join(os.path.dirname(__file__), "test4.png")
        )
