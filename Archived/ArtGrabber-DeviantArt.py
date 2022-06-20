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
from bs4 import BeautifulSoup  # also, for web scraping -- mainly to read the HTML file


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


def write_image(content):
    """
    Write an image
    and return its content and img_hash in str and hex dtype
    """
    open("image.jpg", 'wb').write(content)
    img_hash = imagehash.dhash(Image.open("image.jpg"))
    return img_hash, str(img_hash)


def requests_get_info(info):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (HTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}
    return requests.get(info, headers=headers)


def parse(info):
    return BeautifulSoup(info.text, "html.parser")


def list_of_image_links(tag, class_):
    return [img[tag] for img in html_parse_individual_image.select(class_)]


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

    return requests_content_length.content, length


def get_image_title():
    span_tag = html_parse_individual_image.find('span', class_='_2P31x rNwfh')
    span_tag.decompose()
    html_parse_individual_image.get_text()
    return html_parse_individual_image.find('div', class_='_1FuUQ').text.strip()


def log_to_sheet(two_d_list_to_send):
    sheet.values().append(
        spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
        range="DeviantArt-Grabber-Log!A:F", valueInputOption="RAW",
        body={"values": two_d_list_to_send}).execute()


def get_user(self):
    return str(self.find('span', class_='_2COLT').text)


if __name__ == "__main__":

    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Art-Bot/keys.json'  # points to the keys json file that holds the dictionary of the info we need.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # website to send the oauth info to gain access to our data

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)  # writes the creds value with the value from the keys json file above

    service = build('sheets', 'v4',
                    credentials=creds)  # builds a package with all the above info and version we need and the right service we need

    # Call the Sheets API
    sheet = service.spreadsheets()

    result_da = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="DeviantArt-Grabber-Log!A:F").execute()
    values_da = result_da.get('values', [])

    result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="FB-Poster-Log!A:G").execute()
    values_fb = result_fb.get('values', [])

    result_bw = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Bad-Topics-NSFW!A:A").execute()
    values_bw = result_bw.get('values', [])

    flatlist_da = flatten(values_da)
    flatlist_fb = flatten(values_fb)
    flatlist_bw = flatten(values_bw)

    # List of sources to grab images from
    deviant_art_source_list = ["https://www.deviantart.com/tag/naturephotography?order=all-time",
                               "https://www.deviantart.com/tag/naturephotograph?order=all-time",
                               "https://www.deviantart.com/tag/naturebeautiful?order=all-time",
                               "https://www.deviantart.com/tag/photographynature?order=all-time",
                               "https://www.deviantart.com/tag/animalphotography?order=all-time",
                               "https://www.deviantart.com/tag/wildlifephotography?order=all-time",
                               "https://www.deviantart.com/tag/seasidelandscape?order=all-time",
                               "https://www.deviantart.com/tag/travelphotography?order=all-time",
                               "https://www.deviantart.com/tag/flowerphotography?order=all-time",
                               "https://www.deviantart.com/tag/oceanlandscape?order=all-time"]

    chosen_source = random.choice(deviant_art_source_list)
    # This is to pose as a windows chrome user to get the data we need a little better -- also some sites block python requests user headers
    print("The chosen source was:\n" + str(chosen_source))
    html_text = requests_get_info(chosen_source)
    html_parse = BeautifulSoup(html_text.text, "html.parser")
    images_from_page = html_parse.find_all(class_='_3bcZ2 _2VvAH')

    # create empty list to store the image links in
    all_images = []

    count = 0

    for div in images_from_page:
        image_hrefs = div.find('a')['href']
        all_images.append(image_hrefs)

    for link in all_images:

        # make sure the link we want to use is not already in the DA log sheet of images we've collected
        if link not in (flatlist_da + flatlist_fb):

            # Make a new HTTP request to the image page itself (so we're grabbing the actual image, not the img preview).
            html_text_individual_image = requests_get_info(link)
            html_parse_individual_image = parse(html_text_individual_image)
            img_link = list_of_image_links("src", "._1cVSI img")
            img_link_string = str(img_link[0])

            image_content, image_length = get_image(img_link_string)

            # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
            if image_length < 4000:

                img_caption = get_image_title()
                if no_badwords(img_caption):

                    # Get the name of the user who posted the image for credit purposes
                    img_poster = get_user(html_parse_individual_image)

                    # img_hash the image we just saved
                    image_hash, hash_str = write_image(image_content)

                    # make sure the image img_hash is not in the DA log sheet
                    if hash_str not in (flatlist_da + flatlist_fb):
                        image_text = ocr_text()
                        if no_badwords(image_text):
                            spreadsheet_values_to_send = [
                                [str(img_caption), str(img_poster), str(link), str(img_link_string), str(image_length),
                                 hash_str]]
                            log_to_sheet(spreadsheet_values_to_send)
                            print("Post logged to DA Spreadsheet")
                            break

                        # if the post did not meet our criteria then start again until we find one that does
                        else:
                            continue

# just for my own sanity, to make sure we completed the whole loop and script. THe proverbial "The end." lol
print("\nAll posts have been logged to the spreadsheet accordingly.")
