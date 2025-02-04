from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .models import Book, Author

def get_books(request):
    books = Book.objects.select_related('author').only(
        'id', 'title', 'author__name', 'languages', 'summary',
        'subjects', 'bookshelves', 'formats', 'media_type',
        'copyright', 'download_count', 'translators'
    )

    books_list = [{
        'id': book.id,
        'title': book.title,
        'author': book.author.name if book.author else "Unknown",
        'languages': book.languages,
        'summary': book.summary if book.summary else "No summary provided",
        'subjects': book.subjects,
        'bookshelves': book.bookshelves,
        'formats': book.formats,
        'media_type': book.media_type if book.media_type else "Unknown",
        'copyright': book.copyright,
        'download_count': book.download_count,
        'translators': book.translators
    } for book in books]

    return JsonResponse({'books': books_list}, safe=False)


def get_book(request, book_id):
    try:
        book = Book.objects.select_related('author').values(
            'id', 'title', 'author__name', 'languages', 'summary', 'download_count', 'text'
        ).get(id=book_id)
        return JsonResponse(book)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Livre introuvable.'}, status=404)

def get_french_books(request):
    books = Book.objects.filter(languages__icontains='fr').values(
        'id', 'title', 'author__name', 'summary'
    )
    return JsonResponse(list(books), safe=False)

def get_english_books(request):
    books = Book.objects.filter(languages__icontains='en').values(
        'id', 'title', 'author__name', 'summary'
    )
    return JsonResponse(list(books), safe=False)


def fetch_book_text(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        if book.text:
            return JsonResponse({'text': book.text.strip()})
        else:
            return JsonResponse({'error': 'Texte non disponible pour ce livre.'}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Livre introuvable.'}, status=404)
    
    
def search(request):
    word = request.GET.get('word')

    if not word:
        return JsonResponse({'error': 'No word provided for search.'}, status=400)

    # Recherche dans le texte et le résumé des livres
    books_found = Book.objects.filter(
        Q(text__icontains=word) | Q(summary__icontains=word)
    ).values('title', 'summary', 'author__name')

    # Si aucun livre n'est trouvé
    if not books_found:
        return JsonResponse({'message': f'No books found for the word "{word}".'}, status=404)

    # Transformer en liste de dictionnaires
    results = [
        {
            'title': book['title'],
            'author': book['author__name'] if book['author__name'] else "Unknown",
            'summary': book['summary']
        }
        for book in books_found
    ]

    return JsonResponse({'books': results}, safe=False)
