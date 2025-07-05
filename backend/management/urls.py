from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Routeur DRF pour les vues ViewSet
router = DefaultRouter()

# Enregistrement des ViewSets avec :
# - URL préfixe (ex: /categories/)
# - Vue associée
# - Nom de base pour les URLs
router.register(r"categories", CategorieViewSet, basename="categorie")
router.register(r"transactions", TransactionViewSet, basename="transaction")

# URLs principales de l'application
urlpatterns = [
    # Inclusion des URLs du routeur
    path("", include(router.urls)),
    
    # URLs personnalisées :
    path("stats/", stats_view),  # Statistiques
    path("depense/", depenses_view),  # Liste dépenses
    path("entree/", entrees_view),  # Liste entrées
    path("transactions/", liste_transactions),
    path("evolution/", evolution_mensuelle),  # Évolution mensuelle
    path("login/", CustomLoginView.as_view()),  # Connexion personnalisée
    path("budget/", BudgetMensuelListCreateView.as_view(), name="budget-list-create"),
    path("budget/actuel/", budget_mensuel_actuel, name="budget-actuel"),
    path("budget/resume/", budget_resume, name="budget-resume"),
    
]