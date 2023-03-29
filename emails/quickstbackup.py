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
        # Build the Gmail API client with the user's credentials
        service = build('gmail', 'v1', credentials=creds)
        # List all unread message resources (JSON objects) in the user's inbox
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        # Note: len(messages) will include all emails within a single email thread!
        messages = results.get('messages', [])

        if not messages:
            print("You have no new messages.")
        else:
            print('Number of messages before parse:', len(messages), '\n')
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
                        # body = soup.body()
                        print("Subject: ", subject)
                        print("From: ", sender)

                        # search for all occurrences of target words in the soup content using lambda function
                        targets = ["testing", "database", "donation"]
                        results = soup.find_all(string=lambda text: text and any(target in text.lower() for target in targets))
                        if len(results) > 0:
                            for result in results:
                                print("Email body:", result)

                            random_int = int(random.uniform(100, 1000)*100)/100
                            body_str = " ".join(results)

                            try:
                                # new_donation = Emails(subject=subject, body=body_str, sender=sender, donations=random_int)
                                # new_donation.save()
                                print("New donation saved successfully. \n")
                                try:
                                    # Define email content and send thank you email
                                    subject_admin = 'Thank you for your donation.'
                                    message_admin = f"Dear {sender},\n\nThank you for your donation.\nIt has been added to our database.\nPapa needs a new pair of shoes!"
                                    if sender_address in ['timothymurphy123@gmail.com', 'rmurph1@comcast.net', 'sylvieanna_15@hotmail.com']:
                                        admin_recipient = [sender_address]
                                        # Send the email
                                        send_mail(
                                            subject=subject_admin,
                                            message=message_admin,
                                            from_email=settings.EMAIL_HOST_USER,
                                            recipient_list=admin_recipient,
                                            fail_silently=False
                                            )
                                        print("'Thank you' email sent.\n")

                                    else:
                                        print("Sender not authorized, no email sent.\n")
                                        return
                                except Exception as e:
                                    print("Error with sending ty email:", str(e), "\n")

                            except Exception as e:
                                print("Error with donation database processing:", str(e), "\n")

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
                                print("Error email sent to admin.\n")

                        else:
                            print(f"No occurrences of '{results}' found.\n")

                        # search specific elements and remove their attr for easier viewing in terminal
                        # for a in soup.find_all('a'):
                        #     a.attrs = {}
                        # for p in soup.find_all('p'):
                        #     p.attrs = {}
                        #     print(p)
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


