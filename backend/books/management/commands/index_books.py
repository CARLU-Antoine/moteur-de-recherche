from django.core.management.base import BaseCommand
from books.models import Book, InvertedIndex
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import nltk
from nltk.corpus import stopwords

class Command(BaseCommand):
    help = "Index existing books in the database."

    def handle(self, *args, **kwargs):
        books_indexed = 0

        # Télécharger les stopwords si ce n’est pas déjà fait
        nltk.download('stopwords')

        # Récupérer tous les livres de la base de données
        books = Book.objects.all()

        # Nombre de workers pour exécuter l’indexation en parallèle
        num_workers = 20

        # Utiliser tqdm pour la barre de progression
        with tqdm(total=books.count(), desc="Indexing books", ncols=100) as pbar:
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                for book in books:
                    if book.text and book.languages:  # Vérifier si le livre a du texte et une langue
                        # Soumettre la tâche d’indexation pour chaque livre
                        futures.append(executor.submit(self.index_book, book, pbar))

                for future in as_completed(futures):
                    books_indexed += 1
                    pbar.update(1)

        self.stdout.write(self.style.SUCCESS(f"Indexation terminée : {books_indexed} livres indexés."))

    def index_book(self, book, pbar):
        """Crée une indexation inversée du texte d’un livre en fonction des langues associées"""
        
        # Extraire toutes les langues associées au livre
        languages = [lang.strip().lower() for lang in book.languages.split(',')]
        
        # Initialiser les mots extraits du texte
        words = re.findall(r'\w+', book.text.lower())

        # Filtrer les mots en excluant les stopwords pour chaque langue associée au livre
        for lang_code in languages:
            stopwords_list = self.get_stopwords(lang_code)
            words = [word for word in words if word not in stopwords_list]  # Exclure les stopwords pour la langue spécifique

        # Dictionnaire pour stocker les positions des mots dans le texte
        word_positions = {}

        # Calculer les positions des mots dans le texte
        for index, word in enumerate(words):
            if word not in word_positions:
                word_positions[word] = []
            word_positions[word].append(index)

        # Mettre à jour l'index inversé avec les mots et leurs positions
        for word, positions in word_positions.items():
            # Créer ou récupérer une entrée dans l'index inversé pour ce mot
            index_entry, created = InvertedIndex.objects.get_or_create(word=word)
            index_entry.books.add(book)
            # Ajouter les positions du mot dans l'index
            index_entry.update_positions(book, positions)  # Mettre à jour les positions du mot pour ce livre

    def get_stopwords(self, lang_code):
        """Retourne la liste des stopwords pour la langue donnée"""
        lang_map = {
            'en': 'english',
            'fr': 'french',
            'es': 'spanish',
            'de': 'german',
            'it': 'italian',
            'pt': 'portuguese',
            'nl': 'dutch',
            'tl': 'tagalog',
            'ang': 'old_english',
            'cy': 'welsh',
            'nah': 'nahuatl',
            'eo': 'esperanto',
            'ko': 'korean'
        }

        # Si la langue n'est pas supportée, renvoyer un ensemble vide
        if lang_code not in lang_map:
            return set()

        return set(stopwords.words(lang_map[lang_code]))
