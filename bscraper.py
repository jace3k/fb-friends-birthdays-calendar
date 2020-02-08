from __future__ import print_function
from bs4 import BeautifulSoup
from datetime import datetime
import re


import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

"""
HOW IT WORKS
1. Download fully scrolled page from Birthday Events from Facebook
2. Put it next to the script as 'Events.html'
3. Put credentials.json next to the script
4. Choose CALENDAR_NAME and YEAR of starting events
5. Update 'mapper' dict properly to current day
6. Run script
"""


CALENDAR_NAME = 'Urodziny Facebook'
YEAR = 2020

# UPDATE IT IN CASE OF NEXT DAYS. TODAY: 2/8 (Saturday) (08.02.2020)
mapper = {
    'Sunday': '2/9',
    'Monday': '2/10',
    'Tuesday': '2/11',
    'Wednesday': '2/12',
    'Thursday': '2/13',
    'Friday': '2/14',
    'Saturday': '2/15',
}


birthdays = {}
with open('Events.html') as f:
    soup = BeautifulSoup(f, features='html.parser')
    a = soup.find(id="birthdays_monthly_card").find_all("li")
    # print(a)

    for item in a:
        # print(item.a['data-tooltip-content'])
        item.a['data-tooltip-content']
        birthday_date = re.search(
            r'\((.*)\)', item.a['data-tooltip-content']).group(1)
        person = item.a['data-tooltip-content'].split('(')[0].strip()
        if not re.match(r'\d{1,2}\/\d{1,2}', birthday_date):
            birthday_date = mapper[birthday_date]

        # print(person, birthday_date)
        b_mo, b_day = birthday_date.split('/')
        birthday_date = "{}-{:02d}-{:02d}".format(YEAR, int(b_mo), int(b_day))
        # print(birthday_date)
        birthdays[person] = birthday_date
# print(birthdays)

SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

result = service.calendarList().list().execute()

# print(result['items'])

birthday_calendar = list(
    filter(lambda cal: cal['summary'] == CALENDAR_NAME, result['items']))[0]
print(birthday_calendar['id'])

cal_id = birthday_calendar['id']

events = service.events()

for person, birthday in birthdays.items():
    event = {
        'summary': '{} urodziny'.format(person),
        'start': {
            'date': birthday
        },
        'end': {
            'date': birthday
        },
        'recurrence': [
            'RRULE:FREQ=YEARLY;INTERVAL=1'
        ],
    }
    print('Inserting {} {}'.format(person, birthday))
    events.insert(calendarId=cal_id, body=event).execute()
