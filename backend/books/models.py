from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import re

# Modèle des auteurs
class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

# Modèle des livres
class Book(models.Model):
    gutenberg_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books')
    languages = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    subjects = models.JSONField(default=list, blank=True)
    bookshelves = models.JSONField(default=list, blank=True)
    formats = models.JSONField(default=dict, blank=True)
    media_type = models.CharField(max_length=50, null=True, blank=True)
    copyright = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    translators = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title

# Modèle pour l'index inversé
class InvertedIndex(models.Model):
    word = models.CharField(max_length=255, unique=True)
    books = models.ManyToManyField(Book)
    positions = models.JSONField(default=list, blank=True)  # Stocker les positions des mots
    

    def __str__(self):
        return self.word

    def update_positions(self, book, positions):
        """Met à jour les positions d'un mot dans un livre"""
        # Ajoute les nouvelles positions de ce livre pour le mot
        self.positions.append({'book': book.id, 'positions': positions})
        self.save()

# Fonction d'indexation des livres
def index_book(book):
    """Crée une indexation inversée du texte d'un livre avec les positions des mots"""
    if not book.text:
        return
    
    words = re.findall(r'\w+', book.text.lower())  # Extraction des mots dans le texte
    word_positions = {}

    for index, word in enumerate(words):
        if word not in word_positions:
            word_positions[word] = []
        word_positions[word].append(index)

    for word, positions in word_positions.items():
        # Créer ou récupérer une entrée dans l'index inversé pour ce mot
        index_entry, created = InvertedIndex.objects.get_or_create(word=word)
        index_entry.books.add(book)
        index_entry.update_positions(book, positions)  # Mettre à jour les positions du mot dans ce livre

# Signal pour mettre à jour l'index après l'ajout/modification d'un livre
@receiver(post_save, sender=Book)
def update_inverted_index(sender, instance, **kwargs):
    """Met à jour l'index inversé après la sauvegarde d'un livre"""
    index_book(instance)
