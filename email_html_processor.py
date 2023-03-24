from pathlib import Path
import datetime
import re
from bs4 import BeautifulSoup

import win32com.client  # pip install pywin32


# Create output folder
output_dir = Path.cwd() / "Output"
output_dir.mkdir(parents=True, exist_ok=True)

# Connect to outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# Connect to folder
# inbox = outlook.Folders("youremail@provider.com").Folders("Inbox")
inbox = outlook.GetDefaultFolder(6)
# https://docs.microsoft.com/en-us/office/vba/api/outlook.oldefaultfolders
# DeletedItems=3, Outbox=4, SentMail=5, Inbox=6, Drafts=16, FolderJunk=23

# Get messages
messages = inbox.Items

for message in messages:
    html_body = message.HTMLBody
    subject = message.Subject

    # Create separate folder for each message, exclude special characters and timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_folder = output_dir / \
        re.sub('[^0-9a-zA-Z]+', '', subject) / current_time

    target_folder.mkdir(parents=True, exist_ok=True)

    # Write the plain text and HTML body to the same text file
    with open(Path(target_folder / "EMAIL_HTML.txt"), "w", encoding="utf-8") as f:
        f.write(html_body)
