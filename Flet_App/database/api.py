# Importation du module requests pour faire des requêtes HTTP
import requests
import datetime

# URL de base de l'API Django (backend)
API_BASE = "http://127.0.0.1:8000/api"  # Adresse locale avec le port par défaut de Django

def login_user(username, password):
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
# definition de la fonction pour creer une opération
# Cette fonction envoie une requête POST à l'API pour créer une nouvelle opération 
def get_categories(token):
    """Récupère la liste des catégories depuis Django."""
    url = f"{API_BASE}/categories/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def create_operation(token, data):
    print("🔍 Données envoyées :", data)
    print("🔐 Token :", token)

    headers = {
        "Authorization": f"Token {token}"
    }

    response = requests.post(
        f"{API_BASE}/transactions/",
        headers=headers,
        data=data  # ⚠️ pas json=data
    )

    print("📦 Réponse backend :", response.status_code, response.text)
    return response

def get_stats(token):
    try:
        res = requests.get(f"{API_BASE}/stats/", headers={"Authorization": f"Token {token}"})
        return res.json() if res.status_code == 200 else None
    except:
        return None
    
def get_depenses(token, search="", categorie_name=""):
    try:
        params = {}
        if search:
            params["search"] = search
        if categorie_name and categorie_name not in ["", "Toutes"]:
            params["categorie"] = categorie_name  # <-- c'est l'API qui filtrera
        res = requests.get(
            f"{API_BASE}/depense/",  # <-- vérifie bien l'URL (avec "s")
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print("Erreur get_depenses:", e)
        return []
    
def get_entrees(token, search="", categorie_name=""):
    try:
        params = {}
        if search:
            params["search"] = search
        if categorie_name and categorie_name not in ["", "Toutes"]:
            params["categorie"] = categorie_name  # <-- c'est l'API qui filtrera
        res = requests.get(
            f"{API_BASE}/entree/",  # <-- vérifie bien l'URL (avec "s")
            headers={"Authorization": f"Token {token}"},
            params=params
        )
        return res.json() if res.status_code == 200 else []
    except Exception as e:
        print("Erreur get_depenses:", e)
        return []

    


