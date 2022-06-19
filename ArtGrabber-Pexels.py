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
from pexels_api import API


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (HTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
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


def get_image(url):
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
        range="Pexels-Grabber-Log!A:G", valueInputOption="RAW",
        body={"values": two_d_list_to_send}).execute()

if __name__ == "__main__":

    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

    PEXELS_API_KEY = config.config_stuff3['PEXELS_API_KEY']

    api = API(PEXELS_API_KEY)

    SERVICE_ACCOUNT_FILE = 'keys.json'  # points to the keys json file that holds the dictionary of the info we need.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # website to send the oauth info to gain access to our data

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)  # writes the creds value with the value from the keys json file above

    service = build('sheets', 'v4',
                    credentials=creds)  # builds a package with all the above info and version we need and the right service we need

    # Call the Sheets API
    sheet = service.spreadsheets()

    result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="FB-Poster-Log!A:G").execute()
    values_fb = result_fb.get('values', [])

    result_bw = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Bad-Topics-NSFW!A:A").execute()
    values_bw = result_bw.get('values', [])

    result_pe = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Pexels-Grabber-Log!A:G").execute()
    values_pe = result_pe.get('values', [])

    result_ps = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Pexels-Sources!A:A").execute()
    values_ps = result_ps.get('values', [])

    flatlist_pe = flatten(values_pe) # Pexels Log Sheet
    flatlist_fb = flatten(values_fb) # FB Log Sheet
    flatlist_bw = flatten(values_bw) # list of bad words to avoid
    flatlist_ps = flatten(values_ps) # list of art sources to use from Pexels

    current_row_count = (int(len(flatlist_pe)) / 7)

    print(current_row_count)

    randomly_chosen = str(random.choice(flatlist_ps))

    chosen_source = api.search("Sunset")
    photos = api.get_entries()

    count = 0

running = True
while running:

    for photo in photos:
        photo_name = photo.description
        photo_user = photo.photographer
        photo_id = photo.id
        photo_permalink = photo.url
        photo_extension = photo.extension
        photo_url = photo.large
        photo_size = get_image(photo.large)

        # make sure the link we want to use is not already in the DA log sheet of images we've collected
        if photo_id not in (flatlist_pe + flatlist_fb):

            # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
            if photo_size < 4000:

                if no_badwords(photo_name):

                    # img_hash the image we just saved
                    image_hash, hash_str = write_image(photo_url)

                    # make sure the image img_hash is not in the DA log sheet
                    if hash_str not in (flatlist_pe + flatlist_fb):
                        image_text = ocr_text()
                        if no_badwords(image_text):
                            spreadsheet_values_to_send = [
                                [str(photo_name), str(photo_id), str(photo_user), str(photo_permalink), str(photo_url), str(photo_size),
                                 hash_str]]
                            log_to_sheet(spreadsheet_values_to_send)
                            print("Post logged to Pexels Log Spreadsheet")

                            if spreadsheet_values_to_send:
                                count += 1
                                if count == 1:
                                    break

                            # go to the next page and try results from it instead
                            else:
                                api.search_next_page()
                                continue

                        # if the post did not meet our criteria then start again until we find one that does
                        else:
                            continue


# just for my own sanity, to make sure we completed the whole loop and script. THe proverbial "The end." lol
print("\nAll posts have been logged to the spreadsheet accordingly.")
