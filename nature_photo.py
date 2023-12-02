'''
Author: Logan Maupin

The purpose of this module is to house the nature photo class object.
It's primarily just an extension of the Pexels API photo class objects.
'''
import os
from pexels_api import photo
from database import Database
from image_processing import Image_Processing
from text_processing import Text_Processing

class NaturePhoto(photo):

    def __init__(self) -> None:
        super().__init__(self)
        self.description = self.description.replace("-", " ")
        self.description_words = self.description.split(" ")
        self.file_size = Image_Processing.get_file_size(photo.original)
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        db_path_and_name = os.path.join(self.cwd, "Nature_Bot_Data.db")
        self.database = Database(db_path_and_name)

    def caption_has_bad_words(self) -> bool:
        bad_words_list = self.database.retrieve_values_from_table_column("Bad_Words", "Bad_Words")
        return any(word in self.description_words for word in bad_words_list)
    
    def is_too_large(self) -> bool:
        return self.file_size >= 4_000
    
    def has_been_posted_to_FB_before(self) -> bool:
        previous_post_ids = self.database.retrieve_values_from_table_column('Nature_Bot_Logged_FB_Posts', 'ID')
        return str(self.id) in previous_post_ids
    
    def unacceptable_extension(self) -> bool:
        return not Text_Processing.acceptable_extension_for_photo_posting(self.extension)
    
    @property
    def hash_str(self) -> str:
            # download the image
            Image_Processing.write_image(self.original, "image.jpg")

            # hash the image we just downloaded
            hash_str = Image_Processing.hash_image("image.jpg")
            os.remove("image.jpg")
            return hash_str
    
    def hash_in_db_already(self) -> bool:
        return self.hash_str in self.database.retrieve_values_from_table_column('Nature_Bot_Logged_FB_Posts', 'Image_Hash')