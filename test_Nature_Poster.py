"""
Author: Logan Maupin
Date: 11/20/2022

The following is a test script for nature poster script.
Certain functions are left out of testing for now while I work on a way to figure out how to test them.
"""

import unittest
from Nature_Poster import *


class TestPalindrome(unittest.TestCase):

    def test_no_badwords(self):

        # some of my more SFW bad words
        with open("bad_words.txt") as bad_words:

            for word in bad_words:
                self.assertFalse([word.replace("\n", "")])
                self.assertFalse([word.replace("\n", "").upper()])
                self.assertFalse([word.replace("\n", "").title()])

            self.assertTrue(["This", "sentence", "contains", "no", "bad", "words"])

    def test_write_image(self):
        ideal_hash = "949e9e70cc53ccc6"
        test_photo_file_name = "test_photo_for_hashing.jpg"
        image_link = "https://raw.githubusercontent.com/Voltaic314/Nature-Poster/main/test_photo_for_hashing.jpg"
        self.assertEqual(write_image(image_link, test_photo_file_name), ideal_hash)
        self.assertIsNotNone(write_image(image_link, test_photo_file_name))
        self.assertIsInstance(write_image(image_link, test_photo_file_name), str)

    def test_ocr_text(self):

        ideal_response = ["this", "image", "contains", "text", "and", "numbers" "and", "symbols"]
        self.assertEqual(ocr_text("test_image.jpg"), ideal_response)
        self.assertEqual(ocr_text("test_blank_image.jpg"), [])

    def test_get_file_size(self):
        pass