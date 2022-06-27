import os  # used for getting date and time and file paths
import requests  # used for getting img file size in later code
import random  # used for picking a random log to use for posting
import config  # used to call sensitive info
from datetime import datetime  # used for date and time in the FB log posting so we know when things were posted to FB
from googleapiclient.discovery import build  # for spreadsheet stuff
from google.oauth2 import service_account  # also for spreadsheet stuff
import facebook  # to add captions and comments to existing posts.
import json  # to decipher the dictionary we get back in return from FB servers. (Mainly this is used to edit captions to the posts).
import numpy as np

def formatted_parameters(title, user, id, permalink, url, size, hash):
    """
    Accepts a submission object and returns
    the parameters formatted as a list
    """

    lst = [title
        , user
        , id
        , f"https://www.reddit.com{permalink}"
        , url
        , size
        , hash]

    return [str(item) for item in lst]


def one_d_list_to_two_d_list(self):
    length_of_to_be_sent_list = len(self)
    reshaped_list = np.reshape(self, (1, length_of_to_be_sent_list))
    array_to_list = reshaped_list.tolist()
    return array_to_list


def clear_spreadsheet():
    request_clear = sheet.values().clear(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                         range="Pexels-Grabber-Log!A:G").execute()


def rewrite_spreadsheet(values):
    request_rewrite = sheet.values().update(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                            range="Pexels-Grabber-Log!A:G", valueInputOption="RAW",
                                            body={"values": values}).execute()


def sheet_append(one_d_list):
    log_to_fb_sheet = sheet.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                            range="FB-Poster-PE-Log!A:I", valueInputOption="USER_ENTERED",
                                            body={"values": one_d_list}).execute()


def flatten(two_d_list):
    return [item for items in two_d_list for item in items]


if __name__ == '__main__':

    fb_page_id = "101111365975816"

    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

    SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Art-Bot/keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="FB-Poster-PE-Log!A:I").execute()
    values_fb = result_fb.get('values', [])
    result_pe = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Pexels-Grabber-Log!A:G").execute()
    values_pe = result_pe.get('values', [])

    flatlist_rg = flatten(values_pe)
    flatlist_fb = flatten(values_fb)

    count = 0

    for posts in values_pe:

        chosen_post = []

        # pick a random value from reddit spreadsheet
        chosen_post = random.choice(values_pe)

        formatted_parameters(chosen_post[0], chosen_post[1], chosen_post[2], chosen_post[3], chosen_post[4],
                             chosen_post[5], chosen_post[6])

        chosen_title = str(chosen_post[0])
        chosen_user = str(chosen_post[1])
        chosen_id = str(chosen_post[2])
        chosen_permalink = str(chosen_post[3])
        chosen_url = str(chosen_post[4])
        chosen_size = str(chosen_post[5])
        chosen_hash = str(chosen_post[6])

        # make sure that the hash did not come up in the search results - if none then it's not a duplicate image
        if chosen_hash not in flatlist_fb:

            msg = chosen_url
            post_url = 'https://graph.facebook.com/{}/photos'.format(fb_page_id)
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

                spreadsheet_values_to_log = [dt_string, return_text_str, chosen_title, chosen_user, chosen_id, chosen_permalink,
                                             chosen_url, chosen_size, chosen_hash]
                sheet_append(one_d_list_to_two_d_list(spreadsheet_values_to_log))
                print("Logged to FB Poster Spreadsheet")

                chosen_generated = [chosen_title, chosen_user, chosen_id, chosen_permalink, chosen_url, chosen_size, chosen_hash]
                values_pe.remove(chosen_generated)
                clear_spreadsheet()
                rewrite_spreadsheet(values_pe)

                # define fb variable for next line with our access info
                fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

                # edit caption of existing fb post we just made
                fb.put_object(parent_object=fb_page_id + '_' + post_id, connection_name='',
                              message="Description: " + '"' + chosen_title + '"' + "\n\nOriginally posted by: " + '"' + chosen_user + '"' + " on Pexels." + "\n\nPexels image link: " + chosen_permalink + "\n\nP.S. This Facebook post was created by a bot. To learn more about how it works, check out the Github page here: https://github.com/Voltaic314/Art-Poster")

                count += 5  # increases the count so that this breaks the loop later

            else:
                count += 1  # increases count by 1, try to post 4 more times then stop when count = 5.

        else:
            continue

        # starting for loop to establish checking the count
        for x in values_fb:

            # if the count goes to 5 (will because of the top condition) then...
            if count >= 5:
                # break the loop. Note that the count will only go up if a successful post goes through. Meaning it can keep constantly posting errors over and over until it finally gets a successful post.
                break
        break

# print to show successful post & edit made.
print("Caption has been edited to post successfully.")
