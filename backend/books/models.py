from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    # Core book information
    gutenberg_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books')
    languages = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    subjects = models.JSONField(default=list, blank=True)
    bookshelves = models.JSONField(default=list, blank=True)
    formats = models.JSONField(default=dict, blank=True)
    media_type = models.CharField(max_length=50, null=True, blank=True)
    copyright = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    translators = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title