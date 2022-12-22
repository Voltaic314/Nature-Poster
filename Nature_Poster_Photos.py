"""
Author: Logan Maupin
Date: 10/07/2022

Description:
This program's purpose is to call Pexels' API, grab a list of photos
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
import random  # Used to pick a random keyword to search when grabbing a photo
from PIL import Image  # for image hashing
import imagehash  # also, for image hashing
import pytesseract  # used for optical character recognition within images, basically pulling text out of images, so we can analyze it
import cv2  # used for parsing data and converting images before putting into tesseract OCR
from pexels_api import API  # need this to get images to use from Pexels (our source of images for the project)
from datetime import datetime  # used for date and time in the FB log posting, so we know when things were posted to FB
import facebook  # to add captions and comments to existing posts.
import json  # to decipher the dictionary we get back in return from FB servers. (Mainly this is used to edit captions to the posts).
import re  # used for getting rid of special characters in the OCR text.
from database import Database


def write_image(url: str, filename: str) -> str:
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
    img_hash = imagehash.dhash(Image.open(filename))
    return str(img_hash)


def ocr_text(filename: str):
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


def get_file_size(url):
    """
    Gets file size of an image given the url for it.

    :param url: This is any url of an image that you wish to get the file size of.
    :returns: File size of an image as a floating point number.
    """

    # grabbing data from our selected url
    requests_content_length = requests.get(url)

    # divides file size by 1000, so we can get how many kilobytes it is
    length = float(requests_content_length.headers.get('content-length')) / 1000

    return length


def acceptable_extension(photo_extension):
    """
    This function defines the list of acceptable photo extensions
    we can use. It also tells us whether the one we want to use is
    in the acceptable list of extensions.
    :param photo_extension: The end of an image url of an image hosted online.
    :returns: True / False of whether the photo extension matches an
    acceptable format.
    """

    extensions = ['jpg', 'jpeg', 'png', 'webp']
    return any(extensions in photo_extension for extensions in extensions)


def post_to_fb(photo_url):
    """
    This function posts to fb given a specific photo_url that
    you wish to use.
    :param photo_url: any url of an image, must end in .jpg or something similar.
    :returns: response from FB servers with the post id or an error
    """

    fb_page_id = "101111365975816"
    msg = photo_url
    post_url = f'https://graph.facebook.com/{fb_page_id}/photos'
    payload = {
        "url": msg,
        "access_token": config.config_stuff['FB_Access_Token']
    }

    post_to_fb_request = requests.post(post_url, data=payload)
    return post_to_fb_request.text


def get_post_id_from_json(request):
    """
    This function takes the response from FB servers and parses out
    the post ID from it.
    :param request: json response object from FB
    :returns: post id string
    """

    return_text_dict = json.loads(request)
    id_from_json = return_text_dict.get('id')
    return id_from_json


def edit_fb_post_caption(post_id, photo_description, photo_permalink):
    """
    This function takes a given FB post and edits a caption to it.

    :param post_id: any FB post you wish to edit.
    :param photo_description: what you wish to edit to it, preferably a str type
    :param photo_permalink: the link of the original pexels photo for credit
    :returns: None
    """

    fb_page_id = "101111365975816"
    GitHub_Link = 'https://github.com/Voltaic314/Nature-Poster'

    # define fb variable for next line with our access info
    fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

    # edit caption of existing fb post we just made
    fb.put_object(parent_object=f'{fb_page_id}_{post_id}', connection_name='',
                  message=f'''Description: {photo_description}\n\nPexels image link: {photo_permalink}\n\n 
                  P.S. This Facebook post was created by a bot. To learn more about how it works,
                   check out the GitHub page here: {GitHub_Link}''')


def process_photos(photos, attempted_posts, database):
    """
    This is the function that primarily makes decisions with the photos.
    It goes through a series of if statements to figure out if the photo
    is worth posting to FB or not based on a given criteria below.

    :param photos: list of photos to iterate through, retrieved from
    the next function below.
    :param attempted_posts: integer representing the number of times we've already tried to post an image.
    :param database: This represents the database class instance from the database.py file.

    :returns: Spreadsheet values to send, this will evaluate to True and allow
    the code to stop running once the post has been logged to the spreadsheet.
    """
    data_to_log = []

    for photo in photos:

        photo_description = photo.description.replace("-", " ")
        photo_description_word_check = photo_description.split(" ")
        photo_user = photo.photographer
        photo_id = str(photo.id)
        photo_permalink = photo.url
        photo_extension = photo.extension
        photo_url = photo.large
        photo_original = photo.original
        photo_file_size = get_file_size(photo.large)
        bad_words_list = database.retrieve_values_from_table_column("Bad_Words", "Bad_Words")

        # if we've picked 5 different photos, and they all fail to post to FB, there's probably something going on.
        # in this case, if the function returns True, because of the done = False thing in the next function, it will
        # kill the loop. In this case this is like a failsafe to make sure the script doesn't run forever in the case of
        # some issue with FB servers.
        if attempted_posts >= 5:
            return True

        # if the photo doesn't have an acceptable file extention to post, try another photo.
        if not acceptable_extension(photo_extension):
            continue

        # if the photo id is already in the database, we've posted it before, try another photo.
        if str(photo.id) in database.retrieve_values_from_table_column('Nature_Bot_Logged_FB_Posts', 'ID'):
            continue

        # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
        if photo_file_size >= 4000:
            continue

        if any(word in photo_description_word_check for word in bad_words_list):
            continue

        # hash the image we just saved
        hash_str = write_image(photo_url, "image.jpg")

        # if the hash string of the image is already in the database, then we've posted a similar photo before.
        if hash_str in database.retrieve_values_from_table_column('Nature_Bot_Logged_FB_Posts', 'Image_Hash'):
            continue

        image_text = ocr_text("image.jpg")
        if any(word.lower() in image_text for word in bad_words_list):
            continue

        # make a network request to post the current photo to FB
        post_to_fb_request = post_to_fb(photo_url)
        fb_post_id = get_post_id_from_json(post_to_fb_request)
        successful_post = fb_post_id in post_to_fb_request

        if not successful_post:
            attempted_posts += 1
            continue

        else:

            print("Photo was posted to FB")

            dt_string = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

            edit_fb_post_caption(fb_post_id, photo_description, photo_permalink)

            print("Caption has been edited successfully.")

            data_to_log = (
                dt_string, str(post_to_fb_request), str(photo_description), str(photo_user),
                str(photo_id), str(photo_permalink), str(photo_url), str(photo_original),
                float(photo_file_size), hash_str
            )

            database.log_to_DB(data_to_log, "Nature_Bot_Logged_FB_Posts")
            print("Data has been logged to the database. All done!")
            database.connect.close()
            break

    return data_to_log


def main():
    """
    This function does the actual searching of the photos.
    This function calls Pexels' API and pulls a list of photos
    to search through. If none of the photos meet our criteria,
    then load the "next page" which is just another list of 15 photos
    to search through.
    :returns: None
    """

    global done
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path_and_name = os.path.join(BASE_DIR, "Nature_Bot_Data.db")
    database_instance = Database(db_path_and_name)
    PEXELS_API_KEY = config.config_stuff3['PEXELS_API_KEY']
    api = API(PEXELS_API_KEY)
    search_terms = database_instance.retrieve_values_from_table_column("Photo_Search_Terms", "Terms")
    searched_term = str(random.choice(search_terms))
    api.search_photo(searched_term, page=1, results_per_page=15)
    attempted_posts = 0
    done = False
    while not done:
        done = process_photos(photos=api.get_photo_entries(), attempted_posts=attempted_posts,
                              database=database_instance)
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    main()
