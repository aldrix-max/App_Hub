
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from datetime import datetime
from .models import Categorie, Transaction, Budget, Agent
from .serializers import CategorieSerializer, TransactionSerializer, BudgetSerializer, LoginSerializer
from rest_framework.decorators import api_view, permission_classes
from collections import defaultdict
from rest_framework import status




# Vue personnalisée pour la connexion (authentification)


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

            return Response({
                "token": token.key,
                "username": user.username,
                "role": role
            })

        except Agent.DoesNotExist:
            return Response({
                "error": "Profil agent introuvable pour cet utilisateur."
            }, status=status.HTTP_404_NOT_FOUND)


# 🔹 CATEGORIE – Consultation seulement
class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [permissions.IsAuthenticated]

# 🔹 TRANSACTIONS – CRUD restreint à l’utilisateur connecté
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        categorie = Categorie.objects.get(id=self.request.data["categorie"])
        serializer.save(utilisateur=self.request.user, type=categorie.type)

# 🔹 BUDGET – créer ou consulter le budget mensuel
@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def budget_view(request):
    if request.method == "GET":
        mois = request.query_params.get("mois")  # format YYYY-MM
        if not mois:
            return Response({"error": "Mois requis"}, status=400)
        mois_date = datetime.strptime(mois + "-01", "%Y-%m-%d").date()
        try:
            budget = Budget.objects.get(utilisateur=request.user, mois=mois_date)
            serializer = BudgetSerializer(budget)
            return Response(serializer.data)
        except Budget.DoesNotExist:
            return Response({"message": "Aucun budget défini pour ce mois."}, status=404)

    elif request.method == "POST":
        data = request.data.copy()
        data["utilisateur"] = request.user.id
        serializer = BudgetSerializer(data=data)
        if serializer.is_valid():
            serializer.save(utilisateur=request.user)
        
# 🔹 STATISTIQUES – dépenses & revenus par mois et catégorie
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
     # dernières opérations
    dernieres = TransactionSerializer(transactions[:5], many=True).data

    return Response({
        "resume": resume,
        "evolution": evolution,
        "categorie_totaux": par_categorie,
        "dernieres": dernieres
        
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def depenses_view(request):
    user = request.user
    qs = Transaction.objects.filter(utilisateur=user, type="DEPENSE")

    search = request.GET.get("search")
    if search:
        qs = qs.filter(description__icontains=search)

    categorie_name = request.GET.get("categorie")
    if categorie_name:
        qs = qs.filter(categorie__id=categorie_name)

    qs = qs.order_by("-date")

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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def entrees_view(request):
    user = request.user
    qs = Transaction.objects.filter(utilisateur=user, type="ENTREE")

    search = request.GET.get("search")
    if search:
        qs = qs.filter(description__icontains=search)

    categorie_name = request.GET.get("categorie")
    if categorie_name:
        qs = qs.filter(categorie__id=categorie_name)

    qs = qs.order_by("-date")

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
