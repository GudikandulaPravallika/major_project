from django.db import models

# Create your models here.
class SocialMediaAccount(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)  # e.g., Instagram, Facebook, Twitter, WhatsApp

    def __str__(self):
        return f"{self.platform}: {self.username}"