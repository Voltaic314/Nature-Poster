"""
Author: Logan Maupin
Date: 10/07/2022

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
import requests  # needed to get image file size before we download images (to make sure we don't download images too large that we can't upload elsewhere).
import os  # needed to get the file paths
import random  # Used to pick a random keyword to search when grabbing a video
from pexels_api import API  # need this to get images to use from Pexels (our source of images for the project)
from datetime import datetime  # used for date and time in the FB log posting, so we know when things were posted to FB
import json  # to decipher the dictionary we get back in return from FB servers. (Mainly this is used to edit captions to the posts).
import sqlite3  # our database access, where all the posts get logged to, a local DB file on the Raspberry Pi.


def no_badwords(sentence: list[str]):
    """
    This function checks a list of strings to see if there is a bad word in the given list of strings.

    :param sentence: This is any list of strings you wish to check for bad words in.
    :returns:  Returns True if there is no bad-word in the given sentence list of strings, false otherwise.
    """
    cursor.execute('SELECT * FROM Bad_Words')
    Bad_Words_from_DB = cursor.fetchall()
    Bad_Words_List = [item for word in Bad_Words_from_DB for item in word]

    return not any(word in sentence for word in Bad_Words_List)


def get_file_size(url: str):
    """
    Gets file size of an image given the url for it.

    :param url: This is any url of an image that you wish to get the file size of.
    :returns: File size of an image as a floating point number.
    """

    # grabbing data from our selected url
    requests_content_length = requests.get(url)

    # divides file size by 1000, so we can get how many kilobytes it is
    length_as_str = requests_content_length.headers.get('content-length')
    if length_as_str:
        return float(length_as_str) / 1_000_000
    else:
        return None


def acceptable_extension(video_extension: str):
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


def post_to_fb(video_link: str, video_description: str, video_permalink: str):
    """
    This function posts to fb given a specific video.url that you wish to use.

    :param video_link: any url of a pexels video, must end in .mp4 or something similar.
    :param video_description: the description attribute of the video class instance, ideally like the alt txt of the vid
    :param video_permalink: the permalink of the video that links back to the original Pexels post.
    :returns: response from FB servers with the post id or an error
    """

    fb_page_id = "101111365975816"
    post_url = f'https://graph.facebook.com/{fb_page_id}/videos'
    GitHub_Link = 'https://github.com/Voltaic314/Nature-Poster'
    message = f'Description: {video_description}\n\nPexels link: {video_permalink}\n\n' \
              f'P.S. This Facebook post was created by a bot. To learn more about how it works,' \
              f' check out the GitHub page here: {GitHub_Link}'
    payload = {
        "file_url": video_link,
        "title": video_description,
        "description": message,
        "access_token": config.config_stuff['FB_Access_Token']
    }

    post_to_fb_request = requests.post(post_url, data=payload)
    return post_to_fb_request.text


def get_post_id_from_json(request: str):
    """
    This function takes the response from FB servers and parses out
    the post ID from it.
    :param request: json response string object from FB
    :returns: post id string
    """

    return_text_dict = json.loads(request)
    id_from_json = return_text_dict.get('id')

    if id_from_json:
        return id_from_json

    else:
        return None


def id_is_in_db(table_name: str, id_string: str):
    """
    The purpose of this function is to check if the video ID we have is in our database or not.
    :param table_name: Which DB table we want to look through to see if the ID is in there.
    :param id_string: The ID of the video returned by Pexels API (the video.id object value)
    :returns: True if the video ID is in the DB, else, false.
    """

    cursor.execute(f'SELECT ID FROM {table_name} WHERE ID="{id_string}"')

    IDs_from_db = cursor.fetchall()

    if IDs_from_db:
        return True

    else:
        return False


def get_search_terms():
    """
    This function gets the search terms from the search terms table_name in the DB. It will return a list of search term
    that we can use for the keyword searches. In reality, we will pick a random one from this 1d array that it returns.
    :returns: 1 dimensional list containing a list of strings that represent our search terms to be used later.
    """

    cursor.execute('Select * FROM Photo_Search_Terms')
    Search_Terms_from_DB = cursor.fetchall()

    return [item for word in Search_Terms_from_DB for item in word]


def log_to_DB(formatted_tuple: tuple):
    """
    The purpose of this function is to log our grabbed info from the get_video function over to the database
    :param formatted_tuple: tuple containing the info that the user wishes to log to the database
    :returns: None
    """
    cursor.execute('INSERT INTO Nature_Bot_Logged_FB_Posts_Videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', formatted_tuple)


def process_videos(videos: list, attempted_posts: int):
    """
    This is the function that primarily makes decisions with the videos.
    It goes through a series of if statements to figure out if the video
    is worth posting to FB or not based on a given criteria below.
    :param videos: list of videos to iterate through, retrieved from
    the next function below.
    :param attempted_posts: This is an integer which will represent the number of times it posted to FB or not.
    :returns: Spreadsheet values to send, this will evaluate to True and allow
    the code to stop running once the post has been logged to the spreadsheet.
    """
    data_to_log = []

    for video in videos:
        video_description = video.description
        video_user = video.videographer
        video_id = str(video.id)
        video_permalink = video.url
        video_extension = video.extension
        video_link = video.link
        video_file_size = get_file_size(video.link)

        # if we've picked 5 different photos, and they all fail to post to FB, there's probably something going on.
        # in this case, if the function returns True, because of the done = False thing in the next function, it will
        # kill the loop. In this case this is like a failsafe to make sure the script doesn't run forever in the case of
        # some issue with FB servers.
        if attempted_posts >= 5:
            return True

        if not acceptable_extension(video_extension):
            continue

        if id_is_in_db('Nature_Bot_Logged_FB_Posts_Videos', str(video.id)):
            continue

        # make sure the file size is less than 1 GB. (This is primarily for FB posting limitations).
        if video_file_size >= 1000:
            continue

        # If the video is greater than 20 minutes long, start over. (also for FB Positing limitations)
        if video.duration >= 1200:
            continue

        if not no_badwords(video_description.lower().split(" ")):
            continue

        post_to_fb_request = post_to_fb(video_link, video.description, video_permalink)
        fb_post_id = get_post_id_from_json(post_to_fb_request)

        if not fb_post_id:
            print("Post was not successful")
            attempted_posts += 1
            continue

        else:

            print("Photo was posted to FB")

            dt_string = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

            data_to_log = (
                dt_string, str(post_to_fb_request), str(video_description), str(video_user),
                str(video_id), searched_term, int(video.duration), str(video_permalink),
                str(video_link), float(video_file_size),
            )

            log_to_DB(data_to_log)

            print("Data has been logged to the database. All done!")

            connect.commit()
            connect.close()

            break

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

    global done, connect, cursor, searched_term
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "Nature_Bot_Data.db")
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    PEXELS_API_KEY = config.config_stuff3['PEXELS_API_KEY']
    api = API(PEXELS_API_KEY)
    Search_Terms = get_search_terms()  # list of art sources to use from Pexels
    searched_term = str(random.choice(Search_Terms))
    api.search_video(searched_term, page=1, results_per_page=15)

    attempted_posts = 0
    done = False
    while not done:
        done = process_videos(videos=api.get_video_entries(), attempted_posts=attempted_posts)
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    main()
