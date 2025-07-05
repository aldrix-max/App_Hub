from django.contrib import admin
from .models import *

# Configuration de l'interface admin pour le modèle Agent
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Colonnes affichées dans la liste des agents
    list_filter = ('role',)          # Filtres disponibles par rôle
    search_fields = ('user__username',)  # Barre de recherche par nom d'utilisateur

# Enregistrement des modèles dans l'interface admin
admin.site.register(Agent, ProfilUtilisateurAdmin)  # Agent avec configuration personnalisée
admin.site.register(Categorie)  # Catégorie avec configuration par défaut
admin.site.register(Transaction)  # Transaction avec configuration par défaut
admin.site.register(BudgetMensuel)
