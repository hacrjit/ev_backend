from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    last_otp_sent_at = models.DateTimeField(null=True, blank=True)
    otp_sent_count = models.IntegerField(default=0, blank=True, null=True)
