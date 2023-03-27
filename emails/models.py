from django.db import models

class Emails(models.Model):
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    sender = models.EmailField()
    donations = models.DecimalField(max_digits=12, decimal_places=2, default=100)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender

    class Meta:
        app_label = 'emails'