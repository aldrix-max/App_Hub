from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()  # Routeur DRF pour les vues standardisées
router.register(r"categories", CategorieViewSet)  # CRUD catégories
router.register(r"transactions", TransactionViewSet, basename='transactions')  # CRUD transactions

urlpatterns = [
    path("", include(router.urls)),  # URLs générées par le routeur
    # URLs personnalisées :
    path("stats/", stats_view),  # Statistiques globales
    path("depense/", depenses_view),  # Liste des dépenses filtrées
    path("entree/", entrees_view),  # Liste des entrées filtrées
    path("transactions/", liste_transactions),  # Transactions avec filtres avancés
    path("evolution/", evolution_mensuelle),  # Données pour graphiques
    path("login/", CustomLoginView.as_view()),  # Connexion personnalisée
    path("budget/", BudgetMensuelListCreateView.as_view()),  # Gestion des budgets
    path("budget/actuel/", budget_mensuel_actuel),  # Budget du mois courant
    path("budget/resume/", budget_resume),  # Résumé détaillé du budget,
    path("export/pdf/", export_pdf_operations, name="export-pdf"), # exportation des donneees
    path("stats/global/", global_stats),
    path("transactions_global/", global_transactions),
    path("agents/all/", all_agents),
    path("budget/global/", budget_global),
    path("evolution_global/", evolution_mensuelle_globale),  # Graphique global
]