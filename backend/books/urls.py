from django.urls import path
from .views import get_books, get_book, get_french_books, get_english_books

urlpatterns = [
    path('books/', get_books, name='all-books'),
    path('book/<int:book_id>/', get_book, name='book-detail'),
    path('frenchbooks/', get_french_books, name='french-books'),
    path('englishbooks/', get_english_books, name='english-books'),
]
