# --- IMPORTS ---
from rest_framework.permissions import *
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
from django.http import FileResponse
from .reportlab import *
from django.db.models.functions import Concat
from django.db.models import Value, Sum


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
    
# =========================
# EXPORT PDF DES TRANSACTIONS
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # <- on autorise tout le monde à appeler, vérification manuelle ensuite
def export_pdf_operations(request):
    mois = request.query_params.get('mois')  # ex: 2025-07
    type_rapport = request.query_params.get('type', 'liste')  # "liste" ou "resume"
    token_key = request.query_params.get('token')  # <- on récupère le token dans l'URL

    if not mois:
        return Response({"error": "Le paramètre 'mois' est requis"}, status=400)

    if not token_key:
        return Response({"error": "Token requis dans l'URL"}, status=401)

    try:
        token = Token.objects.get(key=token_key)
        user = token.user
    except Token.DoesNotExist:
        return Response({"error": "Token invalide"}, status=401)

    try:
        date_obj = datetime.strptime(mois, "%Y-%m")
    except ValueError:
        return Response({"error": "Format de date invalide. Utilisez AAAA-MM"}, status=400)

    if type_rapport == "resume":
        buffer = generate_monthly_summary_pdf(mois, user.username)
        return FileResponse(buffer, as_attachment=True, filename=f"resume_{mois}.pdf")

    # Si type = "liste"
    from .models import Transaction  # adapte selon ton app
    operations = Transaction.objects.filter(
        date__year=date_obj.year,
        date__month=date_obj.month
    ).select_related("categorie", "utilisateur")

    data = []
    for op in operations:
        data.append({
            "date": op.date.strftime("%Y-%m-%d"),
            "type": op.categorie.type,
            "categorie": op.categorie.nom,
            "montant": float(op.montant),
            "description": op.description or "",
            "agent_nom": op.utilisateur.username,
        })

    buffer = generate_monthly_summary_pdf(data, title=f"Rapport des opérations – {mois}")
    return FileResponse(buffer, as_attachment=True, filename=f"rapport_{mois}.pdf")


# CREATION D'UNE AUTRE FONCTION POUR LES PDF
from io import BytesIO
from django.http import FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf(request):
    """
    Génère un PDF immédiatement sans le stocker
    Exemple d'URL: /api/generate-pdf/?mois=2023-10
    """
    mois = request.GET.get('mois', '')
    
    # 1. Crée un buffer mémoire pour le PDF
    buffer = BytesIO()
    
    # 2. Utilise ta fonction existante de génération PDF
    # (Remplace ceci par ta logique réelle)
    from reportlab.pdfgen import canvas
    p = canvas.Canvas(buffer)
    p.drawString(100, 100, f"Rapport du mois: {mois}")
    p.showPage()
    p.save()
    
    # 3. Retourne le PDF directement
    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=False,  # = affichage dans le navigateur
        filename=f"rapport_{mois}.pdf",
        content_type='application/pdf'
    )
#=====================================
#=====================================
# SECTION ADMINISTRATION
#=====================================
#=====================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def global_stats(request):
    """Statistiques consolidées pour l'admin"""
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)
    
    # Calcul des statistiques globales
    stats = {
        "total_entrees": float(Transaction.objects.filter(type="ENTREE")
                         .aggregate(Sum('montant'))['montant__sum'] or 0),
        "total_depenses": float(Transaction.objects.filter(type="DEPENSE")
                          .aggregate(Sum('montant'))['montant__sum'] or 0),
        "count_entrees": Transaction.objects.filter(type="ENTREE").count(),
        "count_depenses": Transaction.objects.filter(type="DEPENSE").count(),
    }

    # Dernières opérations avec le nom de l'agent
    dernieres_ops = Transaction.objects.all() \
    .select_related('utilisateur', 'categorie') \
    .order_by('-date')[:10] \
    .annotate(
        agent_name=Concat('utilisateur__first_name', Value(' '), 
                        'utilisateur__last_name')
    ) \
    .values(
        'id', 'date', 'type', 'montant', 'description',
        'categorie__nom',
        'agent_name'
    )
    
    stats["dernieres_operations"] = list(dernieres_ops)
    
    return Response(stats)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def global_transactions(request):
    """Liste toutes les transactions avec filtres"""
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)
    
    # Filtres
    type_op = request.GET.get("type")
    agent_id = request.GET.get("agent_id")
    search = request.GET.get("search")
    date = request.GET.get("date")

    qs = Transaction.objects.all().select_related('utilisateur', 'categorie')

    if type_op in ["DEPENSE", "ENTREE"]:
        qs = qs.filter(type=type_op)
    if agent_id:
        qs = qs.filter(utilisateur__agent__id=agent_id)
    if search:
        qs = qs.filter(
            Q(description__icontains=search) | 
            Q(categorie__nom__icontains=search) |
            Q(utilisateur__username__icontains=search) |
            Q(utilisateur__first_name__icontains=search) |
            Q(utilisateur__last_name__icontains=search) |
            Q(id__icontains=search)
        )
    if date:
        if len(date) == 10:  # Format YYYY-MM-DD
            qs = qs.filter(date=date)
        elif len(date) == 7:  # Format YYYY-MM
            qs = qs.filter(date__year=date[:4], date__month=date[5:7])

    transactions = qs.order_by('-date').values(
        'id', 'date', 'type', 'montant', 'description',
        'categorie__nom',
        agent_name=Concat('utilisateur__first_name', Value(' '), 
                         'utilisateur__last_name')
    )
    return Response(list(transactions))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_agents(request):
    """Liste tous les agents"""
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)
    
    agents = Agent.objects.all().select_related('user').values(
        'id', 'role',
        name=Concat('user__first_name', Value(' '), 'user__last_name')
    )
    return Response(list(agents))

from decimal import Decimal

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def budget_global(request):
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)
    
    mois = request.GET.get("mois")
    agents = Agent.objects.filter(role="AGENT").select_related('user')
    budgets_data = []
    
    for agent in agents:
        budgets_query = BudgetMensuel.objects.filter(utilisateur=agent.user)
        if mois:
            budgets_query = budgets_query.filter(mois=mois)
        
        for budget in budgets_query.order_by('-mois'):
            depenses = Transaction.objects.filter(
                utilisateur=agent.user,
                type="DEPENSE",
                date__year=budget.mois[:4],
                date__month=budget.mois[5:7]
            ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
            
            progression = (depenses / budget.montant_total) if budget.montant_total != Decimal('0') else Decimal('0')
            
            budgets_data.append({
                "agent_id": agent.id,
                "agent_name": f"{agent.user.first_name} {agent.user.last_name}",
                "mois": budget.mois,
                "budget": str(budget.montant_total),  # Conversion en string pour le JSON
                "depenses": str(depenses),
                "solde": str(budget.montant_total - depenses),
                "progression": float(progression)  # Conversion pour le frontend
            })
    
    return Response(budgets_data)
# =========================
# GRAPHIQUE GLOBAL - Statistiques pour tous les agents
# =========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def evolution_mensuelle_globale(request):
    """Données pour graphique global par mois/catégorie"""
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)

    type_op = request.GET.get("type")  # "DEPENSE" ou "ENTREE"
    annee = request.GET.get("annee")   # ex: "2025"

    # Récupère toutes les transactions
    qs = Transaction.objects.all()

    # Filtre par type d'opération
    if type_op:
        qs = qs.filter(categorie__type=type_op)

    # Filtre par année si précisé
    if annee:
        qs = qs.filter(date__year=annee)

    # Structure de données: {mois: {catégorie: montant}}
    data = defaultdict(lambda: defaultdict(float))

    # Remplit la structure avec les montants par mois et catégorie
    for op in qs:
        mois = op.date.strftime("%Y-%m")
        data[mois][op.categorie.nom] += float(op.montant)

    # Ajoute le nom de l'agent pour chaque transaction
    transactions_agents = qs.annotate(
        agent_name=Concat('utilisateur__first_name', Value(' '), 'utilisateur__last_name')
    ).values('date', 'categorie__nom', 'montant', 'agent_name')

    return Response({
        'par_categorie': data,
        'transactions_agents': transactions_agents
    })
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pdf_agent(request):
    """Export PDF pour un agent spécifique"""
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)
    
    mois = request.query_params.get('mois')
    agent_id = request.query_params.get('agent_id')

    if not mois or not agent_id:
        return Response({"error": "Les paramètres 'mois' et 'agent_id' sont requis"}, status=400)

    try:
        agent = Agent.objects.get(id=agent_id)
        buffer = generate_agent_report_pdf(mois, agent)
        return FileResponse(buffer, as_attachment=True, filename=f"rapport_{agent.user.username}_{mois}.pdf")
    except Agent.DoesNotExist:
        return Response({"error": "Agent introuvable"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_global_report_pdf(request):
    if not request.user.is_superuser:
        return Response({"error": "Accès non autorisé"}, status=403)
    
    mois = request.query_params.get('mois')
    if not mois:
        return Response({"error": "Le paramètre 'mois' est requis"}, status=400)

    try:
        # Validation du format de date
        datetime.strptime(mois, "%Y-%m")
    except ValueError:
        return Response({"error": "Format de mois invalide. Utilisez AAAA-MM"}, status=400)

    try:
        buffer = generate_global_report_pdf(mois)
        if not buffer:
            return Response({"error": "Aucune donnée à exporter pour ce mois"}, status=404)
            
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="rapport_global_{mois}.pdf"'
        return response
        
    except Exception as e:
        return Response({"error": f"Erreur lors de la génération du rapport: {str(e)}"}, status=500)