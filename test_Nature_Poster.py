"""
Author: Logan Maupin
Date: 11/20/2022

The following is a test script for nature poster script.
Certain functions are left out of testing for now while I work on a way to figure out how to test them.
"""

import unittest
from unittest.mock import patch
from Nature_Poster import *


class TestNatureBot(unittest.TestCase):

    def test_no_badwords(self):

        # some of my more SFW bad words
        with open("bad_words.txt") as bad_words:

            for word in bad_words:
                self.assertFalse([word.replace("\n", "")])
                self.assertFalse([word.replace("\n", "").upper()])
                self.assertFalse([word.replace("\n", "").title()])

            self.assertTrue(["This", "sentence", "contains", "no", "bad", "words"])

    # I want to somehow mock patch this in unittest but I'm not sure how I could make this work.
    # This test will fail if you run it offline.
    # TODO: figure out how to unittest this without pinging a specific web server, for now this will do
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
        self.assertEqual(get_file_size("https://raw.githubusercontent.com/Voltaic314/Nature-Poster/main/test_photo_for_hashing.jpg"), 146.168)

    def test_acceptable_extension(self):
        self.assertTrue(acceptable_extension("jpg"))
        self.assertTrue(acceptable_extension("jpeg"))
        self.assertTrue(acceptable_extension("png"))
        self.assertTrue(acceptable_extension("webp"))
        self.assertFalse(acceptable_extension("gif"))
        self.assertFalse("bmp")
        self.assertFalse("mp4")

    # I don't have a test for this yet so for now it passes.
    def test_post_to_fb(self):
        pass

    # Not sure how to test this yet either so for now we'll pass it for the time being.
    # Since it requires an example response text. I have a json response I could use but that's not
    # what you pass into the function, that's what it outputs. So I'm not sure how I would handle this.
    # probably some kind of mock patch thing again but not sure yet.
    def test_get_post_id_from_json(self):
        pass

    # again, this requires sending post requests to FB API so I'm not really sure how I would test this yet.
    def test_edit_fb_post_caption(self):
        pass

