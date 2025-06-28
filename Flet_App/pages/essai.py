
import flet as ft
from database.api import login_user  # Cette fonction fait la requête POST /api/login/

def login_view(page: ft.Page):
    page.title = "Connexion"
    page.theme_mode = ft.ThemeMode.LIGHT  # Ou DARK si tu préfères

    # Champs d’entrée
    username = ft.TextField(
        label="Nom d’utilisateur",
        label_style=ft.TextStyle(italic=True, color="#2563eb"),
        border_radius=8,
        width=350,
        filled=True,
        bgcolor="white",
        border_color="#2563eb",
        focused_border_color="#2563eb",
        shift_enter=True,
    )

    password = ft.TextField(
        label="Mot de passe",
        label_style=ft.TextStyle(italic=True, color="#2563eb"),
        password=True,
        can_reveal_password=True,
        border_radius=8,
        width=350,
        filled=True,
        bgcolor="white",
        border_color="#2563eb",
        shift_enter=True,
    )

    message = ft.Text("", color="red")
    bouton = ft.ElevatedButton("Se connecter", bgcolor="#2563eb", color="white")

    def on_login(e):
        if not username.value or not password.value:
            message.value = "❗ Tous les champs sont obligatoires."
            page.update()
            return

        bouton.text = "Connexion..."
        bouton.disabled = True
        page.update()

        response = login_user(username.value, password.value)

        bouton.text = "Se connecter"
        bouton.disabled = False

        if response is None:
            message.value = "❌ Erreur : le serveur est inaccessible."
        elif response.status_code == 200:
            data = response.json()
            token = data.get("token")
            role = data.get("role")
            username_session = data.get("username")

            page.session.set("token", token)
            page.session.set("role", role)
            page.session.set("username", username_session)

            if role == "ADMIN":
                page.go("/admindashboard")
            elif role == "AGENT":
                page.go("/agentdashboard")
            else:
                page.go("/visionneurdashboard")
        else:
            message.value = "❌ Identifiants incorrects."

        page.update()
    def on_login(e):
        # Appel à l'API Django
        response = login_user(username.value, password.value)
        
        if response is None:
            message.value = "❌ Serveur Django inaccessible"
        elif response.status_code == 200:
            # Succès - extraction des données
            data = response.json()
            token = data['token']
            role = data['role']
            
            # Stockage dans la session Flet
            page.session.set("token", token)  # Token d'authentification
            page.session.set("role", role)    # Rôle de l'utilisateur
            
            # Redirection basée sur le rôle
            if role == "ADMIN":
                page.go("/admin-dashboard")
            elif role == "AGENT":
                page.go("/agent-dashboard")
            elif role == "AUTRE":
                page.go("/visionneur-dashboard")
        else:
            message.value = "❌ Identifiants incorrects"
        
        page.update()  # Met à jour l'interface

    bouton.on_click = on_login

    page.views.clear()
    page.views.append(
        ft.View(
            route="/",
            controls=[
                ft.Column([
                    ft.Text("🔐 Connexion", size=30, weight="bold", color="#2563eb"),
                    username,
                    password,
                    bouton,
                    message
                ], spacing=20
                )
            ],))