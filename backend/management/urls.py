from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategorieViewSet, TransactionViewSet,CustomLoginView, budget_view, stats_view, depenses_view, entrees_view

router = DefaultRouter()
router.register(r"categories", CategorieViewSet, basename="categorie")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
    path("budget/", budget_view),
    path("stats/", stats_view),
    path("depense/", depenses_view),
    path("entree/", entrees_view),
    path("login/", CustomLoginView.as_view()),  # 👈 important
]
