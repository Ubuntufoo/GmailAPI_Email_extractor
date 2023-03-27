from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import base64

# Manage credentials and Gmail console configuration at https://console.cloud.google.com/welcome?project=mygmailapi-381619

# Define the scopes to authorize access to user's Gmail account
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # Check if there are saved credentials, and load them if there are
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # If credentials have expired but can be refreshed, refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # Otherwise, start the authorization flow to get new credentials
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Build the Gmail API client with the user's credentials
        service = build('gmail', 'v1', credentials=creds)
        # List all unread message resources (JSON objects) in the user's inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        # Note: len(messages) will include all emails within a single email thread!
        messages = results.get('messages', [])

        if not messages:
            print("You have no new messages.")
        else:
            print('Number of messages before parse:', len(messages))
            for msg in messages:
                # Get the full message data from its id
                txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                try:
                    print("Message ID:", msg['id'])
                    # Get value of 'payload'(actual content) and 'headers' from dictionary 'txt'
                    payload = txt['payload']
                    headers = payload['headers']

                    # Look for Subject and Sender Email in the headers
                    for d in headers:
                        if d['name'] == 'Subject':
                            subject = d['value']
                        if d['name'] == 'From':
                            sender = d['value']

                    # Extract the message body (in HTML format) from the payload
                    if 'parts' in payload:
                        for part in payload['parts']:
                            if 'data' in part['body']:
                                data = part['body']['data']
                                break
                    else:
                        data = payload['body']['data']

                    if data is not None:
                        # The Body of the message is in Encrypted format.
                        # Get the data and decode it with base 64 decoder.
                        data = data.replace("-","+").replace("_","/")
                        decoded_data = base64.b64decode(data)
                        # Parse the decoded HTML using BS4 and the 'lxml' parser which covers XML and HTML
                        soup = BeautifulSoup(decoded_data, 'lxml')
                        body = soup.body()
                        print("Subject: ", subject)
                        print("From: ", sender)

                        # search for all occurances of target words in the soup content using lambda function
                        targets = ["testing", "database", "donation", "contact"]
                        results = soup.find_all(string=lambda text: text and any(target in text.lower() for target in targets))
                        if len(results) > 0:
                            for result in results:
                                print(result)
                        else:
                            print(f"No occurrences of '{results}' found in the soup.")

                        # search specific elements and remove their attr for easier viewing in terminal
                        # for a in soup.find_all('a'):
                        #     a.attrs = {}
                        # for p in soup.find_all('p'):
                        #     p.attrs = {}
                        #     print(p)
                        print('\n')
                    else:
                        print(f"Message {msg['id']} has no parsable body data.")

                except Exception as e:
                    # If there was an error parsing the message, print the error
                    print(f"Error parsing message {msg['id']}: {str(e)}")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()


