from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer

# Liste des livres
class BookListView(generics.ListAPIView):
    queryset = Book.objects.select_related('author')
    serializer_class = BookSerializer

# Détail d'un livre
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.select_related('author')
    serializer_class = BookSerializer
    lookup_field = 'id'

# Liste des livres en français
class FrenchBooksView(generics.ListAPIView):
    queryset = Book.objects.filter(languages__icontains='fr')
    serializer_class = BookSerializer

# Liste des livres en anglais
class EnglishBooksView(generics.ListAPIView):
    queryset = Book.objects.filter(languages__icontains='en')
    serializer_class = BookSerializer

# Récupérer le texte d'un livre
class BookTextView(APIView):
    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            if book.text:
                return Response({'text': book.text.strip()})
            return Response({'error': 'Texte non disponible.'}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'error': 'Livre introuvable.'}, status=status.HTTP_404_NOT_FOUND)

# Recherche d'un mot dans les livres
class BookSearchView(APIView):
    def get(self, request):
        word = request.GET.get('word')
        if not word:
            return Response({'error': 'Veuillez fournir un mot clé.'}, status=status.HTTP_400_BAD_REQUEST)

        books_found = Book.objects.filter(
            Q(text__icontains=word) | Q(summary__icontains=word)
        ).values('id', 'title', 'languages', 'summary', 'author__name')

        if not books_found:
            return Response({'message': f'Aucun livre trouvé pour "{word}".'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'books': list(books_found)})
