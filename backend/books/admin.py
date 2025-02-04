from django.contrib import admin
from .models import Book, Author

# Enregistrer les modèles pour qu'ils apparaissent dans l'interface d'administration
admin.site.register(Book)
admin.site.register(Author)
