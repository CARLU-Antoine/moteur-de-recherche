from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=50)
    gutenberg_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.title
