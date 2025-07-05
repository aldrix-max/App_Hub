# Importation du module requests pour faire des requêtes HTTP
import requests
import datetime

# URL de base de l'API Django (backend)
API_BASE = "http://127.0.0.1:8000/api"  # Adresse locale avec le port par défaut de Django

# =========================
# Authentification utilisateur
# =========================
def login_user(username, password):
    url = f"{API_BASE}/login/"
    try:
        # Envoie une requête POST avec les identifiants pour obtenir un token
        response = requests.post(url, data={
            "username": username,
            "password": password
        })
        return response  # Retourne la réponse complète (pour gérer le code et le token)
    except requests.exceptions.RequestException as e:
        print("Erreur lors de la connexion à l'API :", e)
        return None

# =========================
# Récupération des catégories
# =========================
def get_categories(token):
    """Récupère la liste des catégories depuis Django."""
    url = f"{API_BASE}/categories/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Retourne la liste des catégories
    return []

# =========================
# Création d'une opération (transaction)
# =========================
def create_operation(token, data):
    print("🔍 Données envoyées :", data)
    print("🔐 Token :", token)

    headers = {
        "Authorization": f"Token {token}"
    }

    # Envoie une requête POST pour créer une transaction
    response = requests.post(
        f"{API_BASE}/transactions/",
        headers=headers,
        data=data  # ⚠️ Utilise data= pour un formulaire, pas json=
    )

    print("📦 Réponse backend :", response.status_code, response.text)
    return response

# =========================
# Statistiques globales de l'utilisateur
# =========================
def get_stats(token):
    try:
        # Récupère les statistiques globales (totaux, dernières opérations, etc.)
        res = requests.get(f"{API_BASE}/stats/", headers={"Authorization": f"Token {token}"})
        return res.json() if res.status_code == 200 else None
    except:
        return None

# =========================
# Liste des dépenses filtrées
# =========================
def get_depenses(token, search="", categorie_name=""):
    try:
        params = {}
        if search:
            params["search"] = search  # Filtre sur la description
        if categorie_name and categorie_name not in ["", "Toutes"]:
            params["categorie"] = categorie_name  # Filtre sur la catégorie (c'est l'API qui gère)
        res = requests.get(
            f"{API_BASE}/depense/",  # Endpoint pour les dépenses (vérifie bien le nom dans ton backend)
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print("Erreur get_depenses:", e)
        return []

# =========================
# Liste des entrées filtrées
# =========================
def get_entrees(token, search="", categorie_name=""):
    try:
        params = {}
        if search:
            params["search"] = search  # Filtre sur la description
        if categorie_name and categorie_name not in ["", "Toutes"]:
            params["categorie"] = categorie_name  # Filtre sur la catégorie (c'est l'API qui gère)
        res = requests.get(
            f"{API_BASE}/entree/",  # Endpoint pour les entrées (vérifie bien le nom dans ton backend)
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print("Erreur get_depenses:", e)
        return []

# =========================
# Données d'évolution pour les graphiques (par mois et catégorie)
# =========================
def get_evolution_data(token, type_op="DEPENSE", annee=None):
    try:
        params = {"type": type_op}
        if annee:
            params["annee"] = annee  # Filtre sur l'année
        res = requests.get(
            f"{API_BASE}/evolution/",
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

# =========================
# Vérification du budget global pour un mois donné
# =========================
def verifier_budget_global(token, mois):
    try:
        response = requests.get(
            f"{API_BASE}/budget/verifier/",
            headers={"Authorization": f"Token {token}"},
            params={"mois": mois}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None
    
# =========================
# Liste des transactions avec filtres
# =========================
def get_transactions(token, type_op=None, categorie_name=None, date=None, search=None):
    try:
        params = {}
        if type_op:
            params["type"] = type_op
        if categorie_name:
            params["categorie"] = categorie_name  # Maintenant le nom au lieu de l'ID
        if date:
            params["date"] = date
        if search:
            params["search"] = search  # Nouveau paramètre

        res = requests.get(
            f"{API_BASE}/transactions/",
            headers={"Authorization": f"Token {token}"},
            params=params,
            timeout=5
        )
        
        if res.status_code == 200:
            return res.json()
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erreur get_transactions: {e}")
        return []
    
#==============================
# Récupération du budget mensuel
#==============================
import requests

API_BASE = "http://127.0.0.1:8000/api"  # adapte selon ton projet

def get_budget_mensuel(token, mois):
    try:
        res = requests.get(
            f"{API_BASE}/budget/actuel/",
            headers={"Authorization": f"Token {token}"},
            params={"mois": mois},
            timeout=5
        )
        if res.status_code == 200:
            return res.json()
        return None
    except Exception as e:
        print(f"Erreur get_budget_mensuel: {e}")
        return None

def ajouter_budget_mensuel(token, mois, montant_total):
    try:
        res = requests.post(
            f"{API_BASE}/budget/",
            headers={"Authorization": f"Token {token}"},
            data={"mois": mois, "montant_total": montant_total},
            timeout=5
        )
        return res
    except Exception as e:
        print(f"Erreur ajouter_budget_mensuel: {e}")
        return None
    
def get_budget_resume(token, mois):
    try:
        res = requests.get(
            f"{API_BASE}/budget/resume/",
            headers={"Authorization": f"Token {token}"},
            params={"mois": mois},
            timeout=5
        )
        if res.status_code == 200:
            return res.json()
        return None
    except Exception as e:
        print(f"Erreur get_budget_resume: {e}")
        return None