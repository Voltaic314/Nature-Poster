'''
Author: Logan Maupin

The purpose of this module is to house the functionality for the Nature Video class object.
'''
import requests
import os
from database import Database
from pexels_api import video


class NatureVideo(video):

    def __init__(self) -> None:
        super().__init__(self)
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        db_path_and_name = os.path.join(self.cwd, "Nature_Bot_Data.db")
        self.database = Database(db_path_and_name)
        self.file_size = float(requests.get(self.url).headers.get('content-length'))
    
    def too_large(self) -> bool:
        return self.file_size >= 1_000_000

    def too_long(self) -> bool:
        return self.duration >= 1_200
    
    def caption_contains_bad_words(self) -> bool:
        bad_words_list = self.database.retrieve_values_from_table_column("Bad_Words", "Bad_Words")
        return any(word for word in self.description.lower().split(" ") if word in bad_words_list)
    
