from django.urls import path
from .views import (
    BookListView,
    BookDetailView,
    FrenchBooksView,
    EnglishBooksView,
    BookTextView,
    BookSearchView
)

urlpatterns = [
    path('books/', BookListView.as_view(), name='all-books'),
    path('book/<int:id>/', BookDetailView.as_view(), name='book-detail'),
    path('frenchbooks/', FrenchBooksView.as_view(), name='french-books'),
    path('englishbooks/', EnglishBooksView.as_view(), name='english-books'),
    path('book/<int:book_id>/text/', BookTextView.as_view(), name='fetch_book_text'),
    path('search/', BookSearchView.as_view(), name='search'),
]
