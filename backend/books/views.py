import re
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from .models import Book, Author, InvertedIndex
from .serializers import BookSerializer

# ✅ Liste des livres
class BookListView(generics.ListAPIView):
    queryset = Book.objects.select_related('author')
    serializer_class = BookSerializer

# ✅ Détail d'un livre
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.select_related('author')
    serializer_class = BookSerializer
    lookup_field = 'id'

# ✅ Liste des livres en fonction des langues
class BooksByLanguageView(APIView):
    def get(self, request, language):
        books = Book.objects.filter(languages__icontains=language)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

# ✅ Liste des langues disponibles
class AvailableLanguagesView(APIView):
    def get(self, request):
        languages = Book.objects.values_list('languages', flat=True).distinct()
        return Response({"languages": list(languages)})

# ✅ Récupérer le texte d'un livre
class BookTextView(APIView):
    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            if book.text:
                return Response({'text': book.text.strip()})
            return Response({'error': 'Texte non disponible.'}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'error': 'Livre introuvable.'}, status=status.HTTP_404_NOT_FOUND)

# ✅ Recherche basique d'un mot dans les livres
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

# ✅ Recherche avancée avec RegEx (optimisée avec indexation inversée)
class AdvancedBookSearchView(APIView):
    def get(self, request):
        regex_pattern = request.GET.get('pattern')
        if not regex_pattern:
            return Response({'error': 'Veuillez fournir une expression régulière.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            re.compile(regex_pattern)  # Vérifier si la regex est valide
        except re.error:
            return Response({'error': 'Expression régulière invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        words = re.findall(r'\w+', regex_pattern)

        if len(words) == 1:
            try:
                index_entry = InvertedIndex.objects.get(word=words[0].lower())
                books = index_entry.books.values('id', 'title', 'languages', 'summary', 'author__name')
            except InvertedIndex.DoesNotExist:
                return Response({'message': f'Aucun livre trouvé pour "{regex_pattern}".'}, status=status.HTTP_404_NOT_FOUND)
        else:
            books = Book.objects.filter(
                Q(text__regex=regex_pattern) | Q(summary__regex=regex_pattern)
            ).values('id', 'title', 'languages', 'summary', 'author__name')

        return Response({'books': list(books)})

# ✅ Recherche optimisée avec l'index inversé
class InvertedIndexSearchView(APIView):
    def get(self, request):
        word = request.GET.get('word', '').lower()
        if not word:
            return Response({'error': 'Veuillez fournir un mot-clé.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            index_entry = InvertedIndex.objects.get(word=word)
            books = index_entry.books.values('id', 'title', 'languages', 'summary', 'author__name')
        except InvertedIndex.DoesNotExist:
            return Response({'message': f'Aucun livre trouvé pour "{word}".'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'books': list(books)})

# ✅ Recherche classée par pertinence (nombre d'occurrences)
class RankedBookSearchView(APIView):
    def get(self, request):
        word = request.GET.get('word', '').lower()
        if not word:
            return Response({'error': 'Veuillez fournir un mot-clé.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            index_entry = InvertedIndex.objects.get(word=word)
            books = index_entry.books.annotate(
                occurrence_count=Count('text')
            ).order_by('-occurrence_count').values(
                'id', 'title', 'languages', 'summary', 'author__name', 'occurrence_count'
            )
        except InvertedIndex.DoesNotExist:
            return Response({'message': f'Aucun livre trouvé pour "{word}".'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'books': list(books)})

# ✅ Recherche classée par proximité (Closeness)
class ClosenessBookSearchView(APIView):
    def get(self, request):
        word = request.GET.get('word', '').lower()
        
        if not word:
            return Response({'error': 'Veuillez fournir un mot-clé.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            index_entry = InvertedIndex.objects.get(word=word)
            books_with_distances = []

            for book in index_entry.books.all():
                positions = [m.start() for m in re.finditer(r'\b' + re.escape(word) + r'\b', book.text, re.IGNORECASE)]
                
                if not positions:
                    continue

                if len(positions) == 1:
                    avg_distance = 1
                else:
                    distances = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
                    avg_distance = sum(distances) / len(distances)

                closeness_score = 1 / avg_distance if avg_distance > 0 else 0
                books_with_distances.append({
                    'id': book.id,
                    'title': book.title,
                    'languages': book.languages,
                    'summary': book.summary,
                    'author': book.author.name,
                    'closeness_score': closeness_score
                })

            books_with_distances.sort(key=lambda x: x['closeness_score'], reverse=True)

            if not books_with_distances:
                return Response({'message': f'Aucun livre trouvé pour "{word}".'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'books': books_with_distances, 'total_books': len(books_with_distances)})

        except InvertedIndex.DoesNotExist:
            return Response({'message': f'Aucun livre trouvé pour le mot clé "{word}".'}, status=status.HTTP_404_NOT_FOUND)

