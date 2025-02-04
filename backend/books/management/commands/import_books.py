import requests
import concurrent.futures
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import Book, Author
from tqdm import tqdm

GUTENDEX_API = "https://gutendex.com/books/"
MAX_BOOKS = 1664
MAX_WORKERS = 20  # Adjust based on your system's capabilities

class Command(BaseCommand):
    help = "Import books from Gutendex API and store them in the database."

    def fetch_book_text(self, book):
        text_url = book['formats'].get("text/plain; charset=us-ascii") or book['formats'].get("text/plain")
        if not text_url:
            return None

        try:
            text_response = requests.get(text_url, timeout=10)
            text_response.raise_for_status()
            text = text_response.text
            
            # Text cleaning
            text = text.replace("\ufeff", "").replace("\r", "").replace("\n", " ")
            text = re.sub(r"\*\*\* START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", "", text, flags=re.S)
            text = re.sub(r"\*\*\* END OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", "", text, flags=re.S)
            
            return text.strip()
        except requests.exceptions.RequestException:
            return None

    def handle(self, *args, **kwargs):
        books_imported = 0
        page = 1

        with tqdm(total=MAX_BOOKS, desc="Importing books", ncols=100) as pbar:
            while books_imported < MAX_BOOKS:
                try:
                    response = requests.get(GUTENDEX_API, params={"languages": "en", "page": page}, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f"API Error: {e}"))
                    break

                data = response.json()
                books = data.get("results", [])

                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    # Prepare book texts concurrently
                    book_texts = list(executor.map(self.fetch_book_text, books))

                    # Bulk create authors and books
                    with transaction.atomic():
                        for book, text in zip(books, book_texts):
                            if books_imported >= MAX_BOOKS:
                                break

                            # Handle author
                            authors = book.get('authors', [])
                            author_data = authors[0] if authors else {'name': 'Unknown'}

                            author, _ = Author.objects.get_or_create(
                                name=author_data.get('name', 'Unknown'),
                                defaults={
                                    'birth_year': author_data.get('birth_year'),
                                    'death_year': author_data.get('death_year')
                                }
                            )

                            if text:
                                summary = book.get('summaries', [None])[0] if book.get('summaries') else None
                                
                                Book.objects.get_or_create(
                                    gutenberg_id=book['id'],
                                    defaults={
                                        'title': book['title'],
                                        'author': author,
                                        'subjects': book.get('subjects', []),
                                        'bookshelves': book.get('bookshelves', []),
                                        'formats': book.get('formats', {}),
                                        'media_type': book.get('media_type'),
                                        'copyright': book.get('copyright', False),
                                        'download_count': book.get('download_count', 0),
                                        'languages': ','.join(book.get('languages', [])),
                                        'translators': book.get('translators', []),
                                        'text': text,
                                        'summary': summary
                                    }
                                )
                                books_imported += 1
                                pbar.update(1)

                page += 1

        self.stdout.write(self.style.SUCCESS(f"Import completed: {books_imported} books imported."))