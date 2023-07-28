"""
Author: Logan Maupin

The purpose of this module is to make a collection of image processing methods for the nature photo project. However,
we can use this class and methods in other modules as well.
"""
from PIL import Image
import imagehash
import pytesseract
import cv2
import requests
import re
import os


class Image_Processing:

    @staticmethod
    def write_image(url: str, filename: str):
        """
        This function downloads an image from the given url argument,
        then hashes that image, and returns the hash as a string of the hex value.
        :param url: url to get the image from. This must be the exact image url.
        Therefore, it must end in ".jpg", or something similar, at the end of the url.
        :param filename: This represents what you will name the file that you are saving / writing to.

        :returns: img_hash hex dtype variable + img_hash as a string variable
        """

        with open(filename, 'wb') as f:
            f.write(requests.get(url).content)

    @staticmethod
    def hash_image(filename: str) -> str:
        """
        Run a difference hash and return the hash string from the given image specified in the file name.

        :param filename: Name of the image file you wish to hash, must include full file name, so extension as well.
        :returns: difference hash string that can be used to compare against other image hashes to find similar images.
        """

        return str(imagehash.dhash(Image.open(filename)))

    @staticmethod
    def get_file_size(url: str) -> float:
        """
        Gets file size of a file given the url for it.

        :param url: This is any url of a given file that you wish to get the file size of.
        :returns: File size of a given file as a floating point number in kilobytes
        """

        # grabbing data from our selected url
        requests_content_length = requests.get(url)

        # divides file size by 1000, so we can get how many kilobytes it is
        length = float(requests_content_length.headers.get('content-length')) / 1000

        return length

    @staticmethod
    def ocr_text(filename: str) -> list[str]:
        """
        This function runs OCR on the given image file below, then returns
        its text as a list of strings.
        :param filename: String of the name of the image file you wish to extract text from.
        :returns: ocr_text_list - which is a list of strings from words in the image
        """

        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        img = cv2.imread(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        ocr_result = pytesseract.image_to_string(img).lower().replace("\n", "")
        ocr_result = re.sub('[^a-zA-Z0-9]', '', ocr_result)
        os.remove(filename)

        ocr_text_list = [word for word in ocr_result]

        return ocr_text_list
