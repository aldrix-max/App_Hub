# --- IMPORTS ---
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, permissions
from rest_framework import generics
from rest_framework.response import Response
from datetime import datetime
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from collections import defaultdict
from rest_framework import status
from django.db.models import Q


# =========================
# AUTHENTIFICATION PERSONNALISÉE
# =========================
class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Authentification standard via super()
        response = super().post(request, *args, **kwargs)

        try:
            # Récupération du token et de l'utilisateur
            token = Token.objects.get(key=response.data['token'])
            user = token.user

            # Récupérer le profil Agent lié
            agent = Agent.objects.get(user=user)
            role = agent.role

            # Retourne le token, le nom d'utilisateur et le rôle
            return Response({
                "token": token.key,
                "username": user.username,
                "role": role
            })

        except Agent.DoesNotExist:
            # Si aucun profil agent n'est trouvé
            return Response({
                "error": "Profil agent introuvable pour cet utilisateur."
            }, status=status.HTTP_404_NOT_FOUND)

# =========================
# CATEGORIE – Consultation seulement (lecture seule)
# =========================
class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.IsAuthenticated]

# =========================
# TRANSACTIONS – CRUD restreint à l’utilisateur connecté
# =========================
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retourne uniquement les transactions de l'utilisateur connecté
        return Transaction.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        # Lors de la création, ajoute l'utilisateur et le type selon la catégorie
        categorie = Categorie.objects.get(id=self.request.data["categorie"])
        serializer.save(utilisateur=self.request.user, type=categorie.type)

# =========================
# STATISTIQUES – dépenses & revenus par mois et catégorie
# =========================
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def stats_view(request):
    transactions = Transaction.objects.filter(utilisateur=request.user)
    resume = {"depenses": 0, "entrees": 0, "total_depenses": 0, "total_entrees": 0}
    evolution = defaultdict(lambda: {"DEPENSE": 0, "ENTREE": 0})
    par_categorie = defaultdict(float)

    for tr in transactions:
        mois = tr.date.strftime("%Y-%m")
        evolution[mois][tr.type] += float(tr.montant)
        par_categorie[tr.categorie.nom] += float(tr.montant)
        if tr.type == "DEPENSE":
            resume["depenses"] += 1
            resume["total_depenses"] += float(tr.montant)
        else:
            resume["entrees"] += 1
            resume["total_entrees"] += float(tr.montant)
    # dernières opérations (5 plus récentes)
    dernieres = TransactionSerializer(transactions[:5], many=True).data

    # Retourne toutes les statistiques
    return Response({
        "resume": resume,
        "evolution": evolution,
        "categorie_totaux": par_categorie,
        "dernieres": dernieres
    })

# =========================
# DEPENSES – Liste filtrée des dépenses de l'utilisateur
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def depenses_view(request):
    user = request.user
    qs = Transaction.objects.filter(utilisateur=user, type="DEPENSE")

    # Filtre par recherche dans la description
    search = request.GET.get("search")
    if search:
        qs = qs.filter(description__icontains=search)

    # Filtre par catégorie (si précisé)
    categorie_name = request.GET.get("categorie")
    if categorie_name:
        qs = qs.filter(categorie__id=categorie_name)

    qs = qs.order_by("-date")

    # Sérialise les résultats
    data = []
    for op in qs:
        data.append({
            "id": op.id,
            "date": op.date.strftime("%Y-%m-%d"),
            "montant": op.montant,
            "description": op.description,
            "categorie_nom": op.categorie.nom,
        })

    return Response(data)

# =========================
# ENTREES – Liste filtrée des entrées de l'utilisateur
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def entrees_view(request):
    user = request.user
    qs = Transaction.objects.filter(utilisateur=user, type="ENTREE")

    # Filtre par recherche dans la description
    search = request.GET.get("search")
    if search:
        qs = qs.filter(description__icontains=search)

    # Filtre par catégorie (si précisé)
    categorie_name = request.GET.get("categorie")
    if categorie_name:
        qs = qs.filter(categorie__id=categorie_name)

    qs = qs.order_by("-date")

    # Sérialise les résultats
    data = []
    for op in qs:
        data.append({
            "id": op.id,
            "date": op.date.strftime("%Y-%m-%d"),
            "montant": op.montant,
            "description": op.description,
            "categorie_nom": op.categorie.nom,
        })

    return Response(data)

# =========================
# EVOLUTION MENSUELLE – Données pour graphique par mois/catégorie
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def evolution_mensuelle(request):
    user = request.user
    type_op = request.GET.get("type")  # "DEPENSE" ou "ENTREE"
    annee = request.GET.get("annee")   # ex: "2025"

    # Récupère toutes les transactions de l'utilisateur
    qs = Transaction.objects.filter(utilisateur=user)

    # Filtre par type d'opération (dépense ou entrée)
    if type_op:
        qs = qs.filter(categorie__type=type_op)

    # Filtre par année si précisé
    if annee:
        qs = qs.filter(date__year=annee)

    # Structure de données : {mois: {catégorie: montant}}
    data = defaultdict(lambda: defaultdict(float))

    # Remplit la structure avec les montants par mois et catégorie
    for op in qs:
        mois = op.date.strftime("%Y-%m")
        data[mois][op.categorie.nom] += float(op.montant)

    # Retourne la structure pour affichage graphique
    return Response(data)

#============================
# LISTE DES TRANSACTIONS
#=============================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def liste_transactions(request):
    type_op = request.GET.get("type")  # "DEPENSE" ou "ENTREE"
    categorie_name = request.GET.get("categorie")  # Changé de categorie_id à categorie_name
    date_filtre = request.GET.get("date")
    search = request.GET.get("search")  # Nouveau paramètre de recherche

    transactions = Transaction.objects.filter(utilisateur=request.user).select_related('categorie', 'agent')

    # Filtre par type
    if type_op in ["DEPENSE", "ENTREE"]:
        transactions = transactions.filter(type=type_op)

    # Filtre par nom de catégorie (au lieu de l'ID)
    if categorie_name:
        transactions = transactions.filter(categorie__nom__icontains=categorie_name)

    # Filtre par date
    if date_filtre:
        if len(date_filtre) == 7:  # Format mois (AAAA-MM)
            transactions = transactions.filter(date__year=date_filtre[:4], 
                                            date__month=date_filtre[5:7])
        elif len(date_filtre) == 10:  # Format jour (AAAA-MM-JJ)
            transactions = transactions.filter(date=date_filtre)

    # Filtre par recherche globale
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(categorie__nom__icontains=search) |
            Q(type__icontains=search) |
            Q(agent__user__username__icontains=search)
        )

    # Sérialisation des résultats
    data = []
    for tr in transactions.order_by("-date"):
        data.append({
            "id": tr.id,
            "date": tr.date.strftime("%Y-%m-%d"),
            "type": tr.type,
            "montant": float(tr.montant),
            "description": tr.description,
            "categorie": tr.categorie.nom,
            "categorie_id": tr.categorie.id,  # Gardé pour référence
            "agent_nom": tr.agent.user.username if tr.agent else ""
        })

    return Response({"count": len(data), "results": data})

#========================
# DEFINITION DU BUDGET
#========================
class BudgetMensuelListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetMensuelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        mois = self.request.query_params.get("mois")
        qs = BudgetMensuel.objects.filter(utilisateur=user)
        if mois:
            qs = qs.filter(mois=mois)
        return qs

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def budget_mensuel_actuel(request):
    """Retourne le budget du mois courant pour l'utilisateur connecté."""
    from datetime import datetime
    mois = request.GET.get("mois") or datetime.now().strftime("%Y-%m")
    try:
        budget = BudgetMensuel.objects.get(utilisateur=request.user, mois=mois)
        serializer = BudgetMensuelSerializer(budget)
        return Response(serializer.data)
    except BudgetMensuel.DoesNotExist:
        return Response({"detail": "Aucun budget pour ce mois."}, status=404)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def budget_resume(request):
    """
    Retourne le budget global, les dépenses totales, le solde,
    et le détail par catégorie pour le mois donné.
    """
    user = request.user
    mois = request.GET.get("mois") or datetime.now().strftime("%Y-%m")

    # Budget global
    try:
        budget = BudgetMensuel.objects.get(utilisateur=user, mois=mois)
        montant_total = float(budget.montant_total)
    except BudgetMensuel.DoesNotExist:
        return Response({"detail": "Aucun budget pour ce mois."}, status=404)

    # Toutes les catégories
    categories = Categorie.objects.all()

    # Transactions du mois
    transactions = Transaction.objects.filter(
        utilisateur=user,
        type="DEPENSE",
        date__startswith=mois
    )

    depenses_totales = sum(float(tr.montant) for tr in transactions)
    solde = montant_total - depenses_totales

    # Dépenses par catégorie
    categories_stats = []
    for cat in categories:
        montant_cat = sum(
            float(tr.montant)
            for tr in transactions
            if tr.categorie_id == cat.id
        )
        pourcentage = (montant_cat / montant_total * 100) if montant_total else 0
        categories_stats.append({
            "id": cat.id,
            "nom": cat.nom,
            "montant": montant_cat,
            "pourcentage": pourcentage
        })

    return Response({
        "mois": mois,
        "montant_total": montant_total,
        "depenses_totales": depenses_totales,
        "solde": solde,
        "categories": categories_stats
    })