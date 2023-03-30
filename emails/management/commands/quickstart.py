import datetime

import os
import os.path
import sys
import random
import base64
import django
from django.core.management.base import BaseCommand

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailprocess.settings')
django.setup()

from bs4 import BeautifulSoup
from django.core.mail import send_mail
from emails.models import Emails
from django.conf import settings


# Manage credentials and Gmail console configuration at https://console.cloud.google.com/welcome?project=mygmailapi-381619

# Define the scopes to authorize access to user's Gmail account
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # Check if there are saved credentials, and load them if there are
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Check if there are saved credentials, and load them if there are
        if os.path.exists(os.path.join(script_dir, 'token.json')):
            creds = Credentials.from_authorized_user_file(os.path.join(script_dir, 'token.json'), SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            # If credentials have expired but can be refreshed, refresh them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            # Otherwise, start the authorization flow to get new credentials
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'emails\management\commands\credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(script_dir, 'token.json'), 'w') as token:
                token.write(creds.to_json())

        try:
            # Build the Gmail API client with the user's credentials
            service = build('gmail', 'v1', credentials=creds)
            # List all unread message resources (JSON objects) in the user's inbox
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
            # Note: len(messages) will include all emails within a single email thread!
            messages = results.get('messages', [])

            if not messages:
                pass
                # print("You have no new messages.")
            else:

                for msg in messages:

                    # Get the full message data from its id
                    txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                    try:
                        # Get value of 'payload'(actual content) and 'headers' from dictionary 'txt'
                        payload = txt['payload']
                        headers = payload['headers']

                        # Look for Subject and Sender Email in the headers
                        for d in headers:
                            if d['name'] == 'Subject':
                                subject = d['value']
                            if d['name'] == 'From':
                                sender = d['value']
                                if '<' in sender and '>' in sender:
                                    sender_name, sender_address = sender.split('<')
                                    sender_name = sender_name.strip()
                                    sender_address = sender_address.strip('>')
                                else:

                                    sender_address = sender

                        # Extract the message body (in HTML format) from the payload
                        if 'parts' in payload:
                            data = None
                            for part in payload['parts']:
                                if part.get('filename'):
                                    # This part contains an attachment
                                    continue
                                if part.get('parts'):
                                    # This part is multipart, so check each subpart
                                    for subpart in part['parts']:
                                        if subpart.get('filename'):
                                            # This subpart contains an attachment
                                            continue
                                        if 'data' in subpart['body']:
                                            data = subpart['body']['data']
                                            break
                                else:
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
                            # file = open(r'C:\Users\timmu\Documents\Coding Projects\email_processor\emails\management\commands\loggingtest.txt', 'a')
                            # file.write(f'{datetime.datetime.now()} - {soup} \n')
                            # body = soup.body()

                            # search for all occurrences of target words in the soup content using lambda function
                            targets = ["testing", "database", "donation"]
                            results = soup.find_all(string=lambda text: text and any(target in text.lower() for target in targets))
                            if len(results) > 0:
                                try:
                                    random_int = int(random.uniform(100, 1000)*100)/100
                                    body_str = " ".join(results)
                                    # new_donation = Emails(subject=subject, body=body_str, sender=sender, donations=random_int)
                                    # new_donation.save()
                                    try:
                                        # Define email content and send thank you email
                                        subject_admin = 'Thank you for your donation.'
                                        message_admin = f"Dear {sender},\n\nThank you for your donation.\nIt has been added to our database.\nPapa needs a new pair of shoes!"
                                        if sender_address in ['rmurph1@comcast.net', 'timothymurphy123@gmail.com',  'sylvieanna_15@hotmail.com']:
                                            admin_recipient = [sender_address]
                                            # Send the email
                                            send_mail(
                                                subject=subject_admin,
                                                message=message_admin,
                                                from_email=settings.EMAIL_HOST_USER,
                                                recipient_list=admin_recipient,
                                                fail_silently=False
                                                )
                                            # print("'Thank you' email sent.\n")

                                        else:
                                            # print("Sender not authorized, no email sent.\n")
                                            return
                                    except Exception as e:
                                        pass
                                        # print("Error with sending ty email:", str(e), "\n")

                                except Exception as e:
                                    pass
                                    # print("Error with donation database processing:", str(e), "\n")

                                    # Define the email content
                                    subject_admin = 'Urgent: Model saving issue'
                                    message_admin = 'Dear Administrator,\n\nAn issue occurred that requires your immediate attention.\n\nBest regards,\nMy nifty little script.'
                                    # from_email_admin = 'timothymurphy123@gmail.com'
                                    # recipient_list_admin = ['timothymurphy123@gmail.com']
                                    # Send the email
                                    send_mail(
                                        subject=subject_admin,
                                        message=message_admin,
                                        from_email=settings.EMAIL_HOST_USER,
                                        recipient_list=[settings.RECIPIENT_ADDRESS],
                                        fail_silently=False
                                        )
                                    # print("Error email sent to admin.\n")

                            else:
                                pass
                                # print(f"No occurrences of '{results}' found.\n")

                            # search specific elements and remove their attr for easier viewing in terminal
                            # for a in soup.find_all('a'):
                            #     a.attrs = {}
                            # for p in soup.find_all('p'):
                            #     p.attrs = {}
                            #     print(p)
                        else:
                            pass
                            # print(f"Message {msg['id']} has no parsable body data.")

                    except Exception as e:
                        pass
                        # If there was an error parsing the message, print the error
                        # print(f"Error parsing message {msg['id']}: {str(e)}")

        except HttpError as error:
            pass
            # TODO(developer) - Handle errors from gmail API.
            # print(f'An error occurred: {error}')








