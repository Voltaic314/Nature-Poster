"""
Author: Logan Maupin
Date: 12/22/2022

Description:
This program's purpose is to call Pexels' API, grab a list of videos
given specific search keywords, then iterate through that list to
see if it matches specific criteria for posting. Once we find
one that we can use, we will post it to FB, edit a caption to the post
that we just made, then log the details of what we posted to a Google
sheets spreadsheet so that we don't post it again.
Some features of this script include: list comprehension, image hashing,
optical character recognition, three different APIs, json parsing, and more.
"""
import config  # used to get the secret sensitive info needed for our APIs - not uploaded to GitHub for security purposes
import os  # needed to get the file paths
import random  # Used to pick a random keyword to search when grabbing a video
import requests
from pexels_api import API  # need this to get images to use from Pexels (our source of images for the project)
from datetime import datetime  # used for date and time in the FB log posting, so we know when things were posted to FB
from database import Database
from text_processing import Text_Processing
from fb_posting import FB_Posting
from nature_video import NatureVideo


class Pexels_Video_Posting:

    @staticmethod
    def process_videos(videos: list, attempted_posts: int, database, searched_term):
        """
        This is the function that primarily makes decisions with the videos.
        It goes through a series of if statements to figure out if the video
        is worth posting to FB or not based on a given criteria below.
        :param videos: list of videos to iterate through, retrieved from
        the next function below.
        :param attempted_posts: This is an integer which will represent the number of times it posted to FB or not.
        :param database: sqlite3 database file to add values to.
        :param searched_term: The search key term that we used to search for the right video through pexels api search.
        :returns: Spreadsheet values to send, this will evaluate to True and allow
        the code to stop running once the post has been logged to the spreadsheet.
        """

        for video in videos:

            current_video = NatureVideo(video)
            
            # if we've picked 5 different photos, and they all fail to post to FB, there's probably something going on.
            # in this case, if the function returns True, because of the done = False thing in the next function, it will
            # kill the loop. In this case this is like a failsafe to make sure the script doesn't run forever in the case of
            # some issue with FB servers.
            if attempted_posts >= 5:
                return True

            if not Text_Processing.acceptable_extension_for_video_posting(video.extension):
                continue

            if str(video.id) in database.retrieve_values_from_table_column('Nature_Bot_Logged_FB_Posts_Videos', 'ID'):
                continue

            # make sure the file size is less than 1 GB. (This is primarily for FB posting limitations).
            if current_video.too_large():
                continue

            # If the video is greater than 20 minutes long, start over. (also for FB Positing limitations)
            if current_video.too_long():
                continue

            if current_video.caption_contains_bad_words():
                continue

            post_to_fb_request = FB_Posting.post_video_to_fb(video)
            fb_post_id = Text_Processing.get_post_id_from_json(post_to_fb_request)

            if not fb_post_id:
                print("Post was not successful")
                attempted_posts += 1
                continue

            else:
                print("Photo was posted to FB")

                dt_string = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

                data_to_log = (
                    dt_string, str(post_to_fb_request), str(current_video.description), str(current_video.videographer),
                    str(current_video.id), searched_term, int(current_video.duration), str(current_video.url),
                    str(current_video.link), float(current_video.file_size),
                )

                database.log_to_DB(formatted_tuple=data_to_log,
                                   table_to_add_values_to="Nature_Bot_Logged_FB_Posts_Videos")
                print("Data has been logged to the database. All done!")
                database.connect.close()
                return data_to_log


def main():
    """
    This function does the actual searching of the videos.
    This function calls Pexels' API and pulls a list of videos
    to search through. If none of the videos meet our criteria,
    then load the "next page" which is just another list of 15 videos
    to search through.
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
    api.search_video(searched_term, page=1, results_per_page=15)

    attempted_posts = 0
    done = False
    while not done:
        done = Pexels_Video_Posting.process_videos(videos=api.get_video_entries(), attempted_posts=attempted_posts,
                                                   database=database_instance, searched_term=searched_term)
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    main()
