import config  # used to get the secret sensitive info needed for our APIs - not uploaded to GitHub for security purposes
import requests  # needed to get image file size before we download images (to make sure we don't download images too large that we can't upload elsewhere).
import random  # needed to pick a random subreddit to grab data from. In theory, you don't have to pick a random one, you could do all at once or just one, either or.
from googleapiclient.discovery import build  # python.exe -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account  # this and the above package are for the spreadsheet usage -- the pip command is a pain, so I pasted it above.
from pexels_api import API, API_V # need this to get images to use from Pexels (our source of images for the project)

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

def get_file_size(url):
    """
    Gets video from a link and returns its content
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
        range="Nature-Videos!A:H", valueInputOption="RAW",
        body={"values": two_d_list_to_send}).execute()

def acceptable_extension(video_extension):
    extensions = ['jpg', 'jpeg', 'png', 'webp']
    return any(extensions in video_extension for extensions in extensions)

def string_replace(string):
    return string.replace("-", " ")

def process_videos(videos):
    spreadsheet_values_to_send = []
    for video in videos:
        video_name = string_replace(video.description)
        video_user = video.videographer
        video_id = str(video.id)
        video_permalink = video.url
        video_size = get_file_size(video.url)
        video_duration = video.duration

        check_id_pe = bool(video_id not in flatlist_pe)
        check_id_fb = bool(video_id not in flatlist_fb)
        # make sure the link we want to use is not already in the DA log sheet of images we've collected
        if check_id_pe:

            if check_id_fb:

                # make sure the file size is less than 4 MB. (This is primarily for FB posting limitations).
                if video_duration < 1200:

                    if video_size < 1000000:

                        if width >= 1920 and height >= 1080:

                            if no_badwords(video_name):

                                spreadsheet_values_to_send = [
                                    [str(video_name), str(video_user), str(video_id), str(video_permalink),
                                     str(video_url), str(video_original), str(video_size),
                                     hash_str]]

                                log_to_sheet(spreadsheet_values_to_send)

                                print("Post logged to Pexels Log Spreadsheet")

                                break

                            # if the post did not meet our criteria then start again until we find one that does
                            else:
                                continue
    return spreadsheet_values_to_send


def main():
    global service, done
    api.search(str(random.choice(flatlist_ps)), page=1, results_per_page=15)

    done = False
    while not done:
        done = process_videos(videos=api.get_entries())
        if not done:
            api.search_next_page()


if __name__ == "__main__":
    PEXELS_API_KEY = config.config_stuff3['PEXELS_API_KEY']
    api = API_V(PEXELS_API_KEY)
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
    result_nv = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Nature-Videos!A:F").execute()
    values_nv = result_nv.get('values', [])
    result_ps = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Pexels-Sources!A:A").execute()
    values_ps = result_ps.get('values', [])
    flatlist_nv = flatten(values_nv)  # Pexels Log Sheet
    flatlist_fb = flatten(values_fb)  # FB Log Sheet
    flatlist_bw = flatten(values_bw)  # list of bad words to avoid
    flatlist_ps = flatten(values_ps)  # list of art sources to use from Pexels
    randomly_chosen = str(random.choice(flatlist_ps))

    main()

# just for my own sanity, to make sure we completed the whole loop and script. THe proverbial "The end." lol
print("\nAll posts have been logged to the spreadsheet accordingly.")
