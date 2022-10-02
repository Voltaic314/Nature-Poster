import discord
from discord.ext import commands
from googleapiclient.discovery import build  # python.exe -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account  # this and the above package are for the spreadsheet usage -- the pip command is a pain, so I pasted it above.
import config
import random

def flatten(nested_list):
    """
    Flattens a nested list.
    """
    return [item for items in nested_list for item in items]


if __name__ == '__main__':
    #### Discord info ####
    TOKEN = config.config_stuff5['TOKEN']
    client = discord.Client()

    #### Google Sheets Info ####
    SERVICE_ACCOUNT_FILE = 'keys.json'  # points to the keys json file that holds the dictionary of the info we need.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # website to send the oauth info to gain access to our data
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)  # writes the creds value with the value from the keys json file above
    service = build('sheets', 'v4', credentials=creds)  # builds a package with all the above info and version we need and the right service we need
    # Call the Sheets API
    sheet = service.spreadsheets()
    result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="FB-Poster-PE-Log!A:J").execute()
    values_fb = result_fb.get('values', [])
    flatlist_fb = flatten(values_fb)  # FB Log Sheet

def generate_message():
    randomly_chosen = random.choice(values_fb)

    randomly_chosen_alt_text = randomly_chosen[2]
    randomly_chosen_Pexels_url = randomly_chosen[5]
    randomly_chosen_link_to_send = randomly_chosen[7]
    message_to_send = "Description: " + '"' + randomly_chosen_alt_text + '"' + "\n\nOriginally posted on Pexels at <" + randomly_chosen_Pexels_url + ">\n\n" + "Image link here: " + randomly_chosen_link_to_send
    return message_to_send

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
@commands.cooldown(1, 600, commands.BucketType.user)
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)

    if message.author == client.user:
        return

    if message.content.startswith('nb!video'):
        await message.channel.send(generate_message())
        return

client.run(TOKEN)
