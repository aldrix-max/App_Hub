# Importation du module requests pour faire des requêtes HTTP
import requests
import datetime
import os

# URL de base de l'API Django (backend)
API_BASE = "https://financial-flow.onrender.com/api/"  # Adresse locale avec le port par défaut de Django

# =========================
# SECTION AUTHENTIFICATION
# =========================

def login_user(username, password):
    """
    Authentifie un utilisateur auprès du backend Django.
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe
    
    Returns:
        Response: Objet Response de requests contenant:
                 - Token JWT si succès (status_code 200)
                 - Message d'erreur si échec (status_code 400/401)
                 - None si erreur de connexion au serveur
    
    Process:
        1. Envoie une requête POST à /api/login/
        2. Le backend vérifie les credentials
        3. Retourne le token si valide
    """
    url = f"{API_BASE}/login/"
    try:
        response = requests.post(url, data={
            "username": username,
            "password": password
        })
        return response
    except requests.exceptions.RequestException as e:
        print("Erreur lors de la connexion à l'API :", e)
        return None

# =========================
# SECTION CATEGORIES
# =========================

def get_categories(token):
    """
    Récupère la liste complète des catégories depuis le backend.
    
    Args:
        token (str): Token JWT d'authentification
    
    Returns:
        list: Liste des catégories (format JSON) ou [] si erreur
    
    Notes:
        - Les catégories sont utilisées pour classer les transactions
        - Requête GET protégée par token
    """
    url = f"{API_BASE}/categories/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

# =========================
# SECTION TRANSACTIONS
# =========================

def create_operation(token, data):
    """
    Crée une nouvelle transaction (dépense ou entrée).
    
    Args:
        token (str): Token JWT
        data (dict): Doit contenir:
                    - type: "DEPENSE" ou "ENTREE"
                    - montant: float
                    - categorie: str
                    - date: str (YYYY-MM-DD)
                    - description: str (optionnel)
    
    Returns:
        Response: Réponse du serveur avec:
                  - Status 201 si créé
                  - Status 400 si données invalides
    
    Debug:
        Affiche les données envoyées et la réponse pour traçage
    """
    print("🔍 Données envoyées :", data)
    print("🔐 Token :", token)

    headers = {
        "Authorization": f"Token {token}"
    }

    response = requests.post(
        f"{API_BASE}/transactions/",
        headers=headers,
        data=data  # Format form-data (compatible avec Django)
    )

    print("📦 Réponse backend :", response.status_code, response.text)
    return response

def get_transactions(token, type_op=None, categorie_name=None, date=None, search=None):
    """
    Récupère les transactions avec filtres avancés.
    
    Args:
        token (str): Token JWT
        type_op (str): "DEPENSE" ou "ENTREE" (optionnel)
        categorie_name (str): Nom de catégorie (optionnel)
        date (str): Date au format YYYY-MM-DD (optionnel)
        search (str): Terme de recherche dans description (optionnel)
    
    Returns:
        list: Liste des transactions filtrées ou [] si erreur
    
    Features:
        - Filtrage multi-critères
        - Timeout de 5s pour éviter les blocages
    """
    try:
        params = {}
        if type_op:
            params["type"] = type_op
        if categorie_name:
            params["categorie"] = categorie_name
        if date:
            params["date"] = date
        if search:
            params["search"] = search

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

# =========================
# SECTION DEPENSES/ENTREES
# =========================

def get_depenses(token, search="", categorie_name=""):
    """
    Récupère uniquement les dépenses avec filtres optionnels.
    
    Args:
        token (str): Token JWT
        search (str): Filtre sur la description
        categorie_name (str): Filtre sur une catégorie
    
    Returns:
        list: Dépenses filtrées ou [] si erreur
    
    Notes:
        - Ignore le filtre si categorie_name est "Toutes" ou vide
        - Endpoint dédié /depense/ pour performances
    """
    try:
        params = {}
        if search:
            params["search"] = search
        if categorie_name and categorie_name not in ["", "Toutes"]:
            params["categorie"] = categorie_name
        res = requests.get(
            f"{API_BASE}/depense/",
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print("Erreur get_depenses:", e)
        return []

def get_entrees(token, search="", categorie_name=""):
    """
    Récupère uniquement les entrées (revenus) avec filtres.
    
    Args:
        token (str): Token JWT
        search (str): Filtre sur la description
        categorie_name (str): Filtre sur une catégorie
    
    Returns:
        list: Entrées filtrées ou [] si erreur
    
    Parallel:
        Même fonctionnement que get_depenses mais sur /entree/
    """
    try:
        params = {}
        if search:
            params["search"] = search
        if categorie_name and categorie_name not in ["", "Toutes"]:
            params["categorie"] = categorie_name
        res = requests.get(
            f"{API_BASE}/entree/",
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print("Erreur get_entrees:", e)
        return []

# =========================
# SECTION STATISTIQUES
# =========================

def get_stats(token):
    """
    Récupère les statistiques globales de l'utilisateur.
    
    Args:
        token (str): Token JWT
    
    Returns:
        dict: Contient typiquement:
              - solde_actuel
              - depenses_mois_courant
              - entrees_mois_courant
              - None si erreur
    
    Usage:
        Pour les widgets de dashboard
    """
    try:
        res = requests.get(f"{API_BASE}/stats/", headers={"Authorization": f"Token {token}"})
        return res.json() if res.status_code == 200 else None
    except:
        return None

def get_evolution_data(token, type_op="DEPENSE", annee=None):
    """
    Récupère les données temporelles pour graphiques.
    
    Args:
        token (str): Token JWT
        type_op (str): "DEPENSE" (défaut) ou "ENTREE"
        annee (int): Année à filtrer (optionnel)
    
    Returns:
        dict: Format:
              {
                  "mois": ["Jan", "Feb", ...],
                  "montants": [100, 200, ...],
                  "par_categorie": {"Alimentation": [50, ...], ...}
              }
              ou {} si erreur
    
    Usage:
        Visualisation des tendances mensuelles
    """
    try:
        params = {"type": type_op}
        if annee:
            params["annee"] = annee
        res = requests.get(
            f"{API_BASE}/evolution/",
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else {}
    except:
        return {}

# =========================
# SECTION BUDGETS
# =========================

def verifier_budget_global(token, mois):
    """
    Vérifie l'existence d'un budget pour un mois donné.
    
    Args:
        token (str): Token JWT
        mois (str): Format YYYY-MM
    
    Returns:
        dict: Budget existant ou None si non trouvé
    
    Usage:
        Avant de créer un nouveau budget
    """
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

def get_budget_mensuel(token, mois):
    """
    Récupère le budget mensuel complet.
    
    Args:
        token (str): Token JWT
        mois (str): Format YYYY-MM
    
    Returns:
        dict: Contient:
              - montant_total
              - date_creation
              - ou None si erreur
    
    Différence avec verifier_budget_global:
        Retourne plus de détails
    """
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
    """
    Crée ou met à jour un budget mensuel.
    
    Args:
        token (str): Token JWT
        mois (str): Format YYYY-MM
        montant_total (float): Montant du budget
    
    Returns:
        Response: Réponse brute du serveur
    
    Notes:
        - POST car création/modification
        - Géré par le même endpoint
    """
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
    """
    Récupère un résumé complet du budget.
    
    Args:
        token (str): Token JWT
        mois (str): Format YYYY-MM
    
    Returns:
        dict: Format complet:
              {
                  "montant_total": 3000,
                  "depenses_totales": 1500,
                  "solde": 1500,
                  "categories": [
                      {"nom": "Alimentation", "montant": 500, "pourcentage": 50},
                      ...
                  ]
              }
              ou None si erreur
    
    Usage:
        Pour l'affichage des tableaux de bord
    """
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
    

def download_summary_pdf(token: str, mois: str):
    url = f"http://127.0.0.1:8000/api/export/pdf/?mois={mois}&type=resume"
    headers = {
        "Authorization": f"Token {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            filepath = os.path.join("temp", f"resume_{mois}.pdf")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return os.path.abspath(filepath)
        else:
            print(f"Erreur HTTP {response.status_code} : {response.text}")
            return None
    except Exception as e:
        print("Erreur lors du téléchargement :", e)
        return None

#================================
# SECTION ADMINISTRATION
#=================================
#==================================
# Ajoutez ces nouvelles fonctions à la fin de api.py
def get_global_stats(token):
    """Récupère les statistiques consolidées pour tous les agents"""
    print("Appel à get_global_stats")
    try:
        response = requests.get(
            f"{API_BASE}/stats/global/",
            headers={"Authorization": f"Token {token}"},
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Erreur get_global_stats: {e}")
        return None

def get_global_transactions(token, filters={}):
    """Récupère toutes les transactions avec filtres"""
    try:
        response = requests.get(
            f"{API_BASE}/transactions_global/",
            headers={"Authorization": f"Token {token}"},
            params=filters,
            timeout=10
        )
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Erreur get_global_transactions: {e}")
        return []

def get_all_agents(token):
    """Liste tous les agents avec leurs rôles"""
    try:
        response = requests.get(
            f"{API_BASE}/agents/all/",
            headers={"Authorization": f"Token {token}"},
            timeout=5
        )
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"Erreur get_all_agents: {e}")
        return []

def get_global_budgets(token, mois=None):
    """Récupère tous les budgets avec filtres optionnels"""
    try:
        params = {}
        if mois:
            params["mois"] = mois
            
        print(f"🔍 Envoi requête GET à {API_BASE}/budget/global/ avec params={params}")  # Debug
        
        response = requests.get(
            f"{API_BASE}/budget/global/",
            headers={"Authorization": f"Token {token}"},
            params=params,
            timeout=10
        )
        
        print(f"📡 Réponse API : {response.status_code} - {response.text}")  # Debug
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"❌ Erreur get_global_budgets: {e}")
        return []
def get_global_evolution_data(token, type_op="DEPENSE", annee=None):
    """Récupère les données temporelles globales pour graphiques"""
    try:
        params = {"type": type_op}
        if annee:
            params["annee"] = annee
            
        response = requests.get(
            f"{API_BASE}/evolution_global/",
            headers={"Authorization": f"Token {token}"},
            params=params,
            timeout=10
        )
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"Erreur get_global_evolution_data: {e}")
        return {}
    
def download_agent_report_pdf(token: str, mois: str, agent_id: str):
    """Télécharge un rapport PDF pour un agent spécifique"""
    url = f"{API_BASE}/export/pdf/agent/?mois={mois}&agent_id={agent_id}"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            filename = f"rapport_agent_{agent_id}_{mois}.pdf"
            with open(filename, "wb") as f:
                f.write(response.content)
            return os.path.abspath(filename)
        else:
            print(f"Erreur HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Erreur download_agent_report_pdf: {e}")
        return None
    
    
