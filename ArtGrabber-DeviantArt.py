import config # used to get the secret sensitive info needed for our APIs - not uploaded to github for security purposes
import requests # needed to get image file size before we download images (to make sure we don't download images too large that we can't upload elsewhere).
import os # needed to get the file paths
import random # needed to pick a random subreddit to grab data from. In theory you don't have to pick a random one, you could do all at once or just one, either or.
from googleapiclient.discovery import build # python.exe -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account # this and the above package are for the spreadsheet usage -- the pip command is a pain so I pasted it above.
from PIL import Image # for image hashing
import imagehash # also for image hashing
import pytesseract # used for optical character recognition within images, basically pulling text out of images so we can analyze it
import cv2 # used for parsing data and converting images before putting into tesseract OCR
from bs4 import BeautifulSoup # also for web scraping -- mainly to read the HTML file


SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Art-Bot/keys.json' # points to the keys json file that holds the dictionary of the info we need.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # website to send the oauth info to gain access to our data

creds = None # writes this variable to no value before overwriting it with the info we need, basically cleaning and prepping it
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES) #writes the creds value with the value from the keys json file above

service = build('sheets', 'v4', credentials=creds) # builds a package with all the above info and version we need and the right service we need

# Call the Sheets API
sheet = service.spreadsheets()

result_da = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="DeviantArt-Grabber-Log!A:F").execute()

values_da = result_da.get('values', []) #get values from spreadsheet

result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="FB-Poster-Log!A:G").execute() # to specify this variable as all of the reddit grabber spreadsheet

values_fb = result_fb.get('values', []) #get values from spreadsheet

#flatten the list of lists returned from the deviant art log spreadsheet
flatlist_da = [item for items in values_da for item in items]

#flatten the list of lists returned from the FB poster log spreadsheet
flatlist_fb =[item for items in values_fb for item in items]

#list of bad words / topics to avoid in our posts
bad_topics = ["faggot", "femboy", "nigger", "fat", "skinny", "horny", "masturbate", "anal", "sex",
              "racist", "homophobic", "rape", "rapist", "BDSM", "dom", "fucked", "hentai",
              "Joe Biden", "Biden", "Trump", "Donald Trump", "disease", "symptom", "Parkinson", "Alzhemier", "memeory loss",
              "COVID", "covid-19", "Virus", "bacteria", "Pandemic", "quarantine", "NATO", "Ukraine", "Russia", "Putin", "fatal",
              "lethal", "no cure", "cock", "pussy", "dick", "vagina", "penis", "reddit",
              "u/", "/r/", "feminists", "qanon", "shooting", "Uvalde"]

# List of sources to grab images from
deviant_art_source_list = ["https://www.deviantart.com/tag/naturephotography?order=all-time",
                           "https://www.deviantart.com/tag/naturephotograph?order=all-time",
                           "https://www.deviantart.com/tag/naturebeautiful?order=all-time",
                           "https://www.deviantart.com/tag/photographynature?order=all-time",
                           "https://www.deviantart.com/tag/animalphotography?order=all-time",
                           "https://www.deviantart.com/tag/wildlifephotography?order=all-time",
                           "https://www.deviantart.com/tag/seasidelandscape?order=all-time",
                           "https://www.deviantart.com/tag/travelphotography?order=all-time",
                           "https://www.deviantart.com/tag/flowerphotography?order=all-time"]

chosen_source = random.choice(deviant_art_source_list)

# This is to pose as a windows chrome user to get the data we need a little better -- also some sites block python requests user headers
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"}


# Pick a random Deviant Art link to go to and make an HTTP request to get there
html_text = requests.get(chosen_source, headers=headers)

# Print whichever link it choose
print("The chosen source was:\n" + str(chosen_source))

# Parse the data from the site to grab the info we need
html_parse = BeautifulSoup(html_text.text, "html.parser")

# Inspect the site and grab a certain number of image links and data from it
images_from_page = html_parse.find_all(class_='_3bcZ2 _2VvAH')

# create empty list to store the image links in
all_images = []

for div in images_from_page:
    image_hrefs = div.find('a')['href']
    all_images.append(image_hrefs)

for link in all_images:

    #make sure the link we want to use is not already in the DA log sheet of images we've collected
    if link not in flatlist_da:

        # make sure the link we want to use is not already in the FB post log sheet of images we've posted
        if link not in flatlist_fb:

            # Make a new HTTP request to the image page itself (so we're grabbing the actual image, not the img preview).
            html_text_individual_image = requests.get(link, headers=headers)

            # parse the page of the image (like if you were to click on a post and open the image post page in its own tab)
            html_parse_individual_image = BeautifulSoup(html_text_individual_image.text, "html.parser")

            # Grab the image link for the original source image of the one we clicked on
            img_link = [img["src"] for img in html_parse_individual_image.select("._1cVSI img")]

            # convert the one and only "list" item from the above variable into a string that we can pass to requests next
            img_link_string = str(img_link[0])

            # make an HTTP request to the actual image link, not just the post page
            img_link_request = requests.get(img_link_string, headers=headers)

            # get image file size
            length = float(img_link_request.headers.get('content-length')) / 1000

            # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
            if float(length) < 4000:

                # Get the span text after the image post title within the div
                span_tag = html_parse_individual_image.find('span', class_='_2P31x rNwfh')

                # Nuke that span out of existence
                span_tag.decompose()

                # Get the actual div we want without having to worry about that span nonsense text.
                img_caption_without_span = html_parse_individual_image.get_text()

                # Grab the caption / title of the image post
                img_caption = html_parse_individual_image.find('div', class_='_1FuUQ').text.strip()

                if not any(word in img_caption for word in bad_topics):

                    # Get the name of the user who posted the image for credit purposes
                    img_poster = str(html_parse_individual_image.find('span', class_='_2COLT').text)

                    # download the image from the "url" variable link using requests function
                    open("image.jpg", 'wb').write(img_link_request.content)

                    # hash the image we just saved
                    hash = imagehash.dhash(Image.open("image.jpg"))

                    hash_string = str(hash)

                    # check to make sure the hash of the image we just tested is in the DA spreadsheet. False means that it's not which means it's not a duplicate image (which is good).
                    check_hash_da = hash_string in flatlist_da

                    # check to make sure the hash of the image we just tested is in the reddit grabber spreadsheet. (We want false values only here).
                    check_hash_fb = hash_string in flatlist_fb

                    # make sure the image hash is not in the DA log sheet
                    if check_hash_da == False:

                        # make sure the image hash is not in the FB log sheet
                        if check_hash_fb == False:

                            ##run OCR
                            # point to where the tesseract files are in our directory
                            pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

                            # read BGR values from image
                            img = cv2.imread('image.jpg')

                            # convert BGR values to RGB values
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                            # give us the resulting text (strings) from the image
                            ocr_result = pytesseract.image_to_string(img)
                            os.remove("image.jpg")  # remove the image we just saved (since we don't actually need the file after hashing it)


                            # this function converts the text from OCR into a list of individual strings, where each string is an element in a list
                            def Convert(string):
                                li = list(string.split(" "))
                                return li
                            list_text = Convert(ocr_result)

                            # this section cleans up the list to remove the "\n' from each string in the newly created list
                            # you may be wondering why we don't just use .strip() and that's because that's for strings and this is a list of strings so we have to iterate through the list to do that for each string in the list.
                            replaced_list = []
                            for string in list_text:
                                replaced_list.append(string.strip())

                            # check to see if within the image itself if there are bad words in the list above
                            check_ocr_bad_topics = [word for word in replaced_list if word in bad_topics]

                            # if no matches of bad topics in the ocr text, then proceed. But if so, try a new image.
                            if not check_ocr_bad_topics:

                                # create an empty list to store data
                                spreadsheet_values_append = []

                                # append list with data from variables above
                                spreadsheet_values_append.append([str(img_caption), str(img_poster), str(link), str(img_link_string), str(length), hash_string])

                                # send the 2d list we just made above to the spreadsheet API (writing to spreadsheet)
                                request = sheet.values().append(
                                    spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                    range="DeviantArt-Grabber-Log!A:F", valueInputOption="RAW",
                                    body={"values": spreadsheet_values_append}).execute()

                                # print statement showing it was written -- in reality it would be better to chedc if one of the variables are actually in the spreadsheet, but this will work for now
                                print("Post logged to DA Spreadsheet")

                                # break out of the loop (good to go)
                                break

                            # if the post did not meet our criteria then start again until we find one that does
                            else:
                                continue

# just for my own sanity, to make sure we completed the whole loop and script. THe proverbial "The end." lol
print("\nAll posts have been logged to the spreadsheet accordingly.")