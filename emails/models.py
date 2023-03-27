from django.db import models

class Emails(models.Model):
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    sender = models.EmailField()
    received_at = models.DateTimeField(auto_now_add=True)
