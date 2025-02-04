from django.urls import path
from .views import get_books, get_book, get_french_books, get_english_books,fetch_book_text,search

urlpatterns = [
    path('books/', get_books, name='all-books'),
    path('book/<int:book_id>/', get_book, name='book-detail'),
    path('frenchbooks/', get_french_books, name='french-books'),
    path('englishbooks/', get_english_books, name='english-books'),
    path('api/book/<int:book_id>/text/', fetch_book_text, name='fetch_book_text'),
    path('search/', search, name='search'),
]
