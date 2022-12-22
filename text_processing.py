"""
Author: Logan Maupin

The point of this module is to provide a collection of text manipulation methods to be used in other modules like the
nature poster photo / video modules.
"""
import json


class Text_Processing:
    def __init__(self):
        pass

    @staticmethod
    def acceptable_extension_for_photo_posting(file_extension: str) -> bool:
        """
        This function defines the list of acceptable photo extensions
        we can use. It also tells us whether the one we want to use is
        in the acceptable list of extensions.
        :param file_extension: The end of an image url of an image hosted online.
        :returns: True / False of whether the photo extension matches an
        acceptable format.
        """

        extensions = ['jpg', 'jpeg', 'png', 'webp']
        return any(extensions in file_extension for extensions in extensions)

    @staticmethod
    def acceptable_extension_for_video_posting(video_extension: str):
        """
        This function defines the list of acceptable video extensions
        we can use. It also tells us whether the one we want to use is
        in the acceptable list of extensions.
        :param video_extension: The end of an image url of an image hosted online.
        :returns: True / False of whether the video extension matches an
        acceptable format.
        """

        extensions = ['mp4', 'mov', 'wmv', 'avi']
        return any(extensions in video_extension for extensions in extensions)

    @staticmethod
    def get_post_id_from_json(api_web_request: str):
        """
        This function takes the response from FB servers and parses out
        the post ID from it.
        :param api_web_request: json response object from FB
        :returns: post id string
        """

        return_text_dict = json.loads(api_web_request)
        id_from_json = return_text_dict.get('id')
        return id_from_json

    @staticmethod
    def there_are_badwords(text_list: list[str], bad_words_list: list[str]) -> bool:
        """
        Simple list comprehension to check if the given text list contains bad words or not.

        :param text_list: list of all the words you want to check. If you're checking a string, split it somehow, then
        pass it into this function. If not I did do a simple str.split() to help with this at least.
        :param bad_words_list: list of bad words you want to use
        :returns: True if any of words in the text list match the bad words list words
        """

        if isinstance(text_list, str):
            text_list = text_list.lower().split()

        return any(word.lower() in text_list for word in bad_words_list)
