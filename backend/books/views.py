import requests
from django.http import JsonResponse

GUTENDEX_API = "https://gutendex.com/books/"

def get_books(request):
    response = requests.get(GUTENDEX_API)
    return JsonResponse(response.json(), safe=False)

def get_book(request, book_id):
    response = requests.get(f"{GUTENDEX_API}?ids={book_id}")
    return JsonResponse(response.json(), safe=False)

def get_french_books(request):
    response = requests.get(f"{GUTENDEX_API}?languages=fr")
    return JsonResponse(response.json(), safe=False)

def get_english_books(request):
    response = requests.get(f"{GUTENDEX_API}?languages=en")
    return JsonResponse(response.json(), safe=False)
