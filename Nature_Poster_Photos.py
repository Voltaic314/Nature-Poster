"""
Author: Logan Maupin
Date: 12/22/2022

Description:
This program's purpose is to call Pexels' API, grab a list of photos given specific search keywords, then iterate
through that list to see if it matches specific criteria for posting. Once we findone that we can use, we will post it
to FB, edit a caption to the post that we just made, then log the details of what we posted to a sqlite3 db file so
that we don't post it again. Some features of this script include: list comprehension, image hashing, optical character
recognition, three different APIs, json parsing, and more.
"""

import config  # used to get the secret info needed for our APIs - not uploaded to GitHub for security purposes
import os
import random
from pexels_api import API
from datetime import datetime
from database import Database
from text_processing import Text_Processing
from fb_posting import FB_Posting
from nature_photo import NaturePhoto


class Pexels_Photo_Processing:

    @staticmethod
    def process_photos(photos, database: Database):
        """
        This is the function that primarily makes decisions with the photos. It goes through a series of if statements to
        figure out if the photo is worth posting to FB or not based on a given criteria below.

        :param photos: list of photos to iterate through, retrieved from
        the next function below.
        :param database: This represents the database class instance from the database.py file.

        :returns: Spreadsheet values to send, this will evaluate to True and allow
        the code to stop running once the post has been logged to the spreadsheet.
        """

        checked_photos = 0
        attempted_posts = 0

        for photo in photos:

            current_photo = NaturePhoto(photo)

            print(f'Checked {checked_photos} photos so far...')

            checked_photos += 1


            # if we've picked 5 different photos, and they all fail to post to FB, there's probably something going on.
            # in this case, if the function returns True, because of the done = False thing in the next function, it will
            # kill the loop. In this case this is like a failsafe to make sure the script doesn't run forever in the case of
            # some issue with FB servers.
            if attempted_posts >= 5:
                return True

            # if the photo doesn't have an acceptable file extention to post, try another photo.
            if current_photo.unacceptable_extension():
                continue

            # if the photo id is already in the database, we've posted it before, try another photo.
            if current_photo.has_been_posted_to_FB_before():
                continue

            # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
            if current_photo.is_too_large():
                continue

            if current_photo.caption_has_bad_words():
                continue

            # if the hash string of the image is already in the database, then we've posted a similar photo before.
            if current_photo.hash_in_db_already():
                continue

            # make a network request to post the current photo to FB
            post_to_fb_request = FB_Posting.post_photo_to_fb(current_photo)
            print(f'FB Response: {post_to_fb_request}')
            fb_post_id = Text_Processing.get_post_id_from_json(post_to_fb_request)
            successful_post = fb_post_id in post_to_fb_request

            if not successful_post:
                attempted_posts += 1
                continue

            else:

                print("Photo was posted to FB")

                dt_string = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

                FB_Posting.edit_fb_post_caption_for_pexels_photo_posting(fb_post_id, current_photo.description, current_photo.url)

                print("Caption has been edited successfully.")

                data_to_log = (
                    dt_string, str(post_to_fb_request), str(current_photo.description), str(current_photo.photographer),
                    str(current_photo.id), str(current_photo.url), str(current_photo.large2x), str(current_photo.original),
                    float(current_photo.file_size), current_photo.hash_str
                )

                database.log_to_DB(data_to_log, "Nature_Bot_Logged_FB_Posts")
                print("Data has been logged to the database. All done!")
                database.connect.close()
                return True


def main():
    """
    This function calls Pexels' API and pulls a list of photos to search through. If none of the photos meet our
    criteria, then load the "next page" which is just another list of 15 photos to search through.

    :returns: None
    """

    global done
    CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    db_path_and_name = os.path.join(CURRENT_DIRECTORY, "Nature_Bot_Data.db")
    database_instance = Database(db_path_and_name)
    PEXELS_API_KEY = config.secret_stuff['PEXELS_API_KEY']
    api = API(PEXELS_API_KEY)
    search_terms = database_instance.retrieve_values_from_table_column("Photo_Search_Terms", "Terms")
    searched_term = str(random.choice(search_terms))
    api.search_photo(searched_term, page=1, results_per_page=15)
    done = False
    while not done:
        done = Pexels_Photo_Processing.process_photos(photos=api.get_photo_entries(),
                                                      database=database_instance)
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    main()
