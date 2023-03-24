from exchangelib import Credentials, Account, HTMLBody
from bs4 import BeautifulSoup

creds = Credentials(username='timmurphy19@hotmail.com', password='Themurph23')

account = Account(primary_smtp_address='timmurphy19@hotmail.com',
                  credentials=creds, autodiscover=True)

# inbox = account.inbox

messages = account.inbox.all()

print(messages.count())

# Extract text from HTML
for msg in messages:
    print(msg.subject, msg.sender.email_address)

    html_content = msg.body
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div')    # find all divs
    for div in divs:
        print(div.text)
