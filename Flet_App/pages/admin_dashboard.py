import flet as ft

def admindashboard(page: ft.Page):
    token = page.session.get("token")
    if not token:
        page.go("/")  # retour à la connexion si pas connecté
        return

    return ft.View(
        "/admin-dashboard",
        controls=[
            ft.Text("Bienvenue dans votre tableau de bord", size=24),
            ft.Text(f"Votre token : {token[:20]}...", color="gray"),
        ]
    )
