from __future__ import print_function

import datetime
import os.path
import pymongo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
from dateutil import parser


connection_string = "mongodb+srv://bfan:PASSWORD@tlcluster.jf40bf4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string,
                     tls=True,
                     tlsCertificateKeyFile='/Applications/Python 3.11/X509-cert-6425077195416651859.pem')
db = client.TLDB
collection = db.TimeLordTestDB



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            if event.get('start', {}).get('dateTime') == None:
                continue
            elif event.get('end', {}).get('dateTime') == None:
                continue
            else:
                start = event.get('start', {}).get('dateTime')
                end = event.get('end', {}).get('dateTime')
                start_time = parser.parse(start)
                end_time = parser.parse(end)
                length = end_time-start_time
                summary = event['summary']
                print(start_time, end_time, length, summary)
                mydict = {"event":event['summary'], "length_mins":length.seconds/60}
                print(mydict)
                x = collection.insert_one(mydict)
                print(x)
                


    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
"""Next-add logic so it doesnt add events that already exist in mongoDB, 
choose an AWS architecture and deploy so you have a simple UI to link your GCal to the system's DB (Dynamo or RDS). 
You could then use the Salesforce Dev account to build something that writes to an SFDC object via API as a proof of concept.
It can be event driven as anytime changes are detected in GCal can trigger the sync"""
