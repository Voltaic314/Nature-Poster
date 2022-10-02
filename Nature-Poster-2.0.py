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
from pexels_api import API # need this to get images to use from Pexels (our source of images for the project)
from datetime import datetime  # used for date and time in the FB log posting so we know when things were posted to FB
import facebook  # to add captions and comments to existing posts.
import json  # to decipher the dictionary we get back in return from FB servers. (Mainly this is used to edit captions to the posts).


def flatten(nested_list):
    """
    Flattens a nested list.
    """
    return [item for items in nested_list for item in items]


def no_badwords(sentence):
    """
    Returns True if there is no bad-word
    False otherwise
    """
    return not any(word in sentence for word in flatlist_bw)

def requests_get_info(info):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (HTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
    return requests.get(info, headers=headers)

def write_image(self):
    """
    Write an image
    and return its content and img_hash in str and hex dtype
    """
    with open('image.jpg', 'wb') as f:
        f.write(requests.get(self).content)
    img_hash = imagehash.dhash(Image.open("image.jpg"))
    return img_hash, str(img_hash)

def ocr_text():
    """
    Carry out OCR on an image according to
    our requirements and return its text, and if it has a bad word
    """
    img = cv2.imread('image.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ocr_result = pytesseract.image_to_string(img)

    os.remove("image.jpg")

    ocr_text_list = [word.replace('\n', '') for word in ocr_result.split(' ')]

    return ocr_text_list, no_badwords(ocr_text_list)


def get_file_size(url):
    """
    Gets image from a link and returns its content
    and size.
    """
    # defines R variable as grabbing data from our selected url
    requests_content_length = requests.get(url)

    # divides file size by 1000, so we can get how many kilobytes it is
    length = float(requests_content_length.headers.get('content-length')) / 1000

    return length

def log_to_sheet(two_d_list_to_send):
    sheet.values().append(
        spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
        range="FB-Poster-PE-Log!A:J", valueInputOption="RAW",
        body={"values": two_d_list_to_send}).execute()

def acceptable_extension(photo_extension):
    extensions = ['jpg', 'jpeg', 'png', 'webp']
    return any(extensions in photo_extension for extensions in extensions)

def string_replace(string):
    return string.replace("-", " ")

def split_strings(string):
    list_of_words_from_string = []
    list_of_words_from_string = string.split()
    return list_of_words_from_string

def process_photos(photos):
    spreadsheet_values_to_send = []

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
                if photo_size < 4000:

                    if no_badwords(photo_description_word_check):

                        # img_hash the image we just saved
                        image_hash, hash_str = write_image(photo_url)

                        check_hash_fb = hash_str not in flatlist_fb

                        if check_hash_fb:

                            image_text = ocr_text()

                            if no_badwords(image_text):

                                msg = photo_url
                                post_url = 'https://graph.facebook.com/{}/videos'.format(fb_page_id)
                                payload = {
                                    "url": msg,
                                    "access_token": config.config_stuff['FB_Access_Token']
                                }

                                post_to_fb = requests.post(post_url, data=payload)
                                print(post_to_fb.text)
                                return_text_str = str(post_to_fb.text)
                                return_text_dict = json.loads(post_to_fb.text)
                                post_id = return_text_dict.get('id')

                                if fb_page_id in return_text_str:

                                    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                                    spreadsheet_values_to_send = [
                                        [dt_string, return_text_str, str(photo_description), str(photo_user), str(photo_id),
                                         str(photo_permalink),
                                         str(photo_url), str(photo_original), str(photo_size),
                                         hash_str]]
                                    log_to_sheet(spreadsheet_values_to_send)

                                    print("Logged to FB Poster Spreadsheet")

                                    # define fb variable for next line with our access info
                                    fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

                                    # edit caption of existing fb post we just made
                                    fb.put_object(parent_object=fb_page_id + '_' + post_id, connection_name='',
                                                  message="Description: " + '"' + photo_description + "\n\nPexels image link: " + photo_permalink + "\n\nP.S. This Facebook post was created by a bot. To learn more about how it works, check out the Github page here: https://github.com/Voltaic314/Nature-Poster")

                                    print("Caption has been edited to post successfully.")

                                    break

                                # if the post did not meet our criteria then start again until we find one that does
                                else:
                                    continue
    return spreadsheet_values_to_send


def get_photo():
    global service, done
    api.search(str(random.choice(flatlist_ps)), page=1, results_per_page=15)

    done = False
    while not done:
        done = process_photos(photos=api.get_entries())
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    PEXELS_API_KEY = config.config_stuff3['PEXELS_API_KEY']
    api = API(PEXELS_API_KEY)
    SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Art-Bot/keys.json'  # points to the keys json file that holds the dictionary of the info we need.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # website to send the oauth info to gain access to our data
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)  # writes the creds value with the value from the keys json file above
    service = build('sheets', 'v4', credentials=creds)  # builds a package with all the above info and version we need and the right service we need
    # Call the Sheets API
    sheet = service.spreadsheets()
    result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="FB-Poster-PE-Log!A:J").execute()
    values_fb = result_fb.get('values', [])
    result_bw = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Bad-Topics-NSFW!A:A").execute()
    values_bw = result_bw.get('values', [])
    result_pe = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Pexels-Grabber-Log!A:H").execute()
    values_pe = result_pe.get('values', [])
    result_ps = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Pexels-Sources!A:A").execute()
    values_ps = result_ps.get('values', [])
    flatlist_pe = flatten(values_pe)  # Pexels Log Sheet
    flatlist_fb = flatten(values_fb)  # FB Log Sheet
    flatlist_bw = flatten(values_bw)  # list of bad words to avoid
    flatlist_ps = flatten(values_ps)  # list of art sources to use from Pexels
    randomly_chosen = str(random.choice(flatlist_ps))
    fb_page_id = "101111365975816"


    get_photo()



# just for my own sanity, to make sure we completed the whole loop and script. THe proverbial "The end." lol
print("\nPhoto has been logged to the spreadsheet accordingly.")
