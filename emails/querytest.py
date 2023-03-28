import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailprocess.settings')
django.setup()

from emails.models import Emails

for email in Emails.objects.all().values():
    email['body'] = email['body'].replace('\\r', '').replace('\\n', '')
    print(f"id: {email['id']}, subject: {email['subject']}, body: {email['body']}, sender: {email['sender']}, donations: {email['donations']}, received_at: {email['received_at']}\n")
