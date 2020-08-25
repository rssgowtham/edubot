from django.db import models

# Create your models here.


class User(models.Model):
    number = models.CharField(max_length=50, primary_key=True)
    service = models.CharField(max_length=50, null=True)
    language = models.CharField(max_length=50, null=True)
    searchQuery = models.CharField(max_length=500, null=True)
    requireLanguage = models.BooleanField(default=False)
    changeLanguageOrService = models.BooleanField(default=False)
    requireService = models.BooleanField(default=True)
    requireUseOldData = models.BooleanField(default=False)

    def __str__(self):
        return self.number
