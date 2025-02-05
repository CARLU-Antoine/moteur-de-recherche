from rest_framework import serializers
from .models import Author, Book

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'birth_year', 'death_year']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'gutenberg_id', 'title', 'author', 'languages', 'summary',
            'subjects', 'bookshelves', 'formats', 'media_type',
            'copyright', 'download_count', 'translators'
        ]
