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
import random  # needed to pick a random subreddit to grab data from. In theory, you don't have to pick a random one, you could do all at once or just one, either or.
from googleapiclient.discovery import build  # python.exe -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account  # this and the above package are for the spreadsheet usage -- the pip command is a pain, so I pasted it above.
from PIL import Image  # for image hashing
import imagehash  # also, for image hashing
import pytesseract  # used for optical character recognition within images, basically pulling text out of images, so we can analyze it
import cv2  # used for parsing data and converting images before putting into tesseract OCR
from pexels_api import API  # need this to get images to use from Pexels (our source of images for the project)
from datetime import datetime  # used for date and time in the FB log posting so we know when things were posted to FB
import facebook  # to add captions and comments to existing posts.
import json  # to decipher the dictionary we get back in return from FB servers. (Mainly this is used to edit captions to the posts).


def flatten(nested_list):
    """
    Flattens a nested list.

    :param nested_list: This is a 2d list that you wish to flatten into one list

    :returns: 1d list. i.e. ["1", "2"]
    """

    return [item for items in nested_list for item in items]


def no_badwords(sentence):
    """
    Returns True if there is no bad-word
    False otherwise

    :param sentence: This is any string you wish to check for bad words in.
    """

    return not any(word in sentence for word in flatlist_bw)


def write_image(url):
    """
    This function downloads an image from the given url argument,
    then hashes that image, and returns the hash as a string + hex dtype.

    :param url: url to get the image from. This must be the exact image url.
    So therefore it must end in ".jpg", or something similar, at the end of the url.

    :returns: img_hash hex dtype variable + img_hash as a string variable
    """

    with open('image.jpg', 'wb') as f:
        f.write(requests.get(url).content)
    img_hash = imagehash.dhash(Image.open("image.jpg"))
    return img_hash, str(img_hash)


def ocr_text():
    """
    This function runs OCR on the given image file below, then returns
    its text as a list of strings.

    :returns: ocr_text_list - which is a list of strings from words in the image
    """

    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    img = cv2.imread('image.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ocr_result = pytesseract.image_to_string(img)

    os.remove("image.jpg")

    ocr_text_list = [word.replace('\n', '') for word in ocr_result.split(' ')]

    return ocr_text_list


def get_file_size(url):
    """
    Gets image from a link and returns its content
    and size.

    :param url: This is any url of an image that you wish to get the file size of.

    :returns: File size of an image as a floating point number.
    """

    # defines R variable as grabbing data from our selected url
    requests_content_length = requests.get(url)

    # divides file size by 1000, so we can get how many kilobytes it is
    length = float(requests_content_length.headers.get('content-length')) / 1000

    return length


def sheets_variables():
    """
    This function builds the Google sheets services and points to where
    our keys.json file is to gain access to the sheet via the API keys.

    :returns: sheets_service variable so that we can use the sheets API.
    """
    SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Art-Bot/keys.json'  # points to the keys json file that holds the dictionary of the info we need.
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets']  # website to send the oauth info to gain access to our data
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,
                                                                  scopes=SCOPES)  # writes the creds value with the value from the keys json file above
    sheets_service = build('sheets', 'v4',
                           credentials=creds)  # builds a package with all the above info and version we need and the right service we need
    return sheets_service


def format_sheets_variable(sheet_name_and_range):
    """
    This function is used so that I don't have to keep repeating 3-4 variables
    all with the same format other than the name / range string.

    :param sheet_name_and_range: This is a sheet name, followed by
    an exclamation point, then a cell range.
    Example: "Sheet1!A1:D4"

    :returns: Sheet values variable which represents all the data in that sheet from the range
    we specified above in the argument when running the function.
    Note that this will be a 2d list. each row will be a list, and it wil lbe a list of those lists.
    """

    sheet_result = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                      range=sheet_name_and_range).execute()
    sheet_values = sheet_result.get('values', [])
    return sheet_values


def log_to_sheet(two_d_list_to_send):
    """
    This function takes a 2d list and appends the spreadsheet
    database with the info you want to add to it.

    :param two_d_list_to_send: This is the 2d list you wish to send to the spreadsheet

    :returns: None
    """

    sheet.values().append(
        spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
        range="FB-Poster-PE-Log!A:J", valueInputOption="RAW",
        body={"values": two_d_list_to_send}).execute()


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


def string_replace(string):
    """
    This function takes any string with hyphens and removes them.
    This is primarily used because pexels likes to store all their
    photo alt text with hyphens between each word instead of spaces.

    :param string: Any string you want to use

    :returns: that same string but without hyphens.
    """

    return string.replace("-", " ")


def split_strings(string):
    """
    This function takes a string and splits it using the python split function.

    :param string: Any string you want to use

    :returns: list of those words in the string.
    """

    list_of_words_from_string = string.split()
    return list_of_words_from_string


def process_image_words(image_text):
    """
    This function takes a string and splits it up into a list of strings,
    then for each word in the new list, converts it all to lower case.
    Then joins the list back into a new string.

    :param image_text: any string you want, preferably more than one word (lol)

    :returns: new_string - which is the image_text string but every word is lower case
    """
    word_list = image_text().split()

    for word in word_list:
        word.lower()

    new_string = word_list.join()

    return new_string


def post_to_fb(photo_url):
    """
    This function posts to fb given a specific photo_url that
    you wish to use.

    :param photo_url: any url of an image, must end in .jpg or something similar.

    :returns: response from FB servers with the post id or an error
    """

    fb_page_id = "101111365975816"
    msg = photo_url
    post_url = 'https://graph.facebook.com/{}/photos'.format(fb_page_id)
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

    :returns: post id integer
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
    # define fb variable for next line with our access info
    fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

    # edit caption of existing fb post we just made
    fb.put_object(parent_object=fb_page_id + '_' + post_id, connection_name='',
                  message="Description: " + '"' + photo_description + '"' + "\n\nPexels image link: " + photo_permalink + "\n\nP.S. This Facebook post was created by a bot. To learn more about how it works, check out the GitHub page here: https://github.com/Voltaic314/Nature-Poster")

    return print("Caption has been edited to post successfully.")


def process_photos(photos):
    """
    This is the function that primarily makes decisions with the photos.
    It goes through a series of if statements to figure out if the photo
    is worth posting to FB or not based on a given criteria below.

    :param photos: list of photos to iterate through, retrieved from
    the next function below.

    :returns: Spreadsheet values to send, this will evaluate to True and allow
    the code to stop running once the post has been logged to the spreadsheet.
    """

    spreadsheet_values_to_send = []
    fb_page_id = "101111365975816"

    for photo in photos:

        photo_description_word_check = split_strings(string_replace(photo.description.lower()))
        photo_description = string_replace(photo.description)
        photo_user = photo.photographer
        photo_id = str(photo.id)
        photo_permalink = photo.url
        photo_extension = photo.extension
        photo_url = photo.large
        photo_original = photo.original
        photo_size = get_file_size(photo.large)

        if acceptable_extension(photo_extension):

            check_id_fb = bool(photo_id not in flatlist_fb)

            if check_id_fb:

                # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
                if photo_size < 4000 and no_badwords(photo_description_word_check):

                    if no_badwords(photo_description_word_check):

                        # img_hash the image we just saved
                        image_hash, hash_str = write_image(photo_url)

                        check_hash_fb = hash_str not in flatlist_fb

                        if check_hash_fb:

                            no_badwords_in_img = no_badwords(ocr_text())

                            if no_badwords_in_img:

                                post_to_fb_request = post_to_fb(photo_url)
                                post_id = get_post_id_from_json(post_to_fb_request)

                                if fb_page_id in post_to_fb_request:

                                    dt_string = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

                                    edit_fb_post_caption(post_id, photo_description, photo_permalink)

                                    spreadsheet_values_to_send = [
                                        [dt_string, str(post_to_fb_request), str(photo_description), str(photo_user),
                                         str(photo_id),
                                         str(photo_permalink),
                                         str(photo_url), str(photo_original), str(photo_size),
                                         hash_str]]
                                    log_to_sheet(spreadsheet_values_to_send)

                                    print("Logged to FB Poster Spreadsheet")

                                    break

                                # if the post did not meet our criteria then start again until we find one that does
                                else:
                                    continue
    return spreadsheet_values_to_send

def get_photo():
    """
    This function does the actual searching of the photos.
    This function calls Pexels' API and pulls a list of photos
    to search through. If none of the photos meet our criteria,
    then load the "next page" which is just another list of 15 photos
    to search through.

    :returns: None
    """

    global service, done
    PEXELS_API_KEY = config.config_stuff3['PEXELS_API_KEY']
    api = API(PEXELS_API_KEY)
    values_ps = format_sheets_variable("Pexels-Sources!A:A")
    flatlist_ps = flatten(values_ps)  # list of art sources to use from Pexels
    api.search(str(random.choice(flatlist_ps)), page=1, results_per_page=15)

    done = False
    while not done:
        done = process_photos(photos=api.get_entries())
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    sheet = sheets_variables().spreadsheets()
    values_fb = format_sheets_variable("FB-Poster-PE-Log!A:J")
    values_bw = format_sheets_variable("Bad-Topics-NSFW!A:A")
    flatlist_fb = flatten(values_fb)  # FB Log Sheet
    flatlist_bw = flatten(values_bw)  # list of bad words to avoid

    get_photo()
