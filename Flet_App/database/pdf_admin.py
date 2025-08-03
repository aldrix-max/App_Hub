import flet as ft
from datetime import datetime

def rapport_view_Admin(page: ft.Page):
    token = page.session.get("token")
    role = page.session.get("role")

    if not token or role != "ADMIN":
        page.go("/")
        return

    # Contrôles UI
    mois_input = ft.TextField(
        label="Mois (AAAA-MM)",
        label_style=ft.TextStyle(color="black"),
        color="black",
        width=300,
        hint_text="Ex: 2025-07",
        keyboard_type="text"
    )

    message = ft.Text("", size=14, color="black")
    generate_btn = ft.ElevatedButton("Générer le rapport global",width=350, color="white", bgcolor=ft.Colors.INDIGO_600,
                               style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2)))

    def generate_pdf(e):
        mois = mois_input.value.strip()
        
        # Validation du format de date
        try:
            datetime.strptime(mois, "%Y-%m")
        except ValueError:
            message.value = "Format invalide. Utilisez AAAA-MM"
            message.color = "red"
            page.update()
            return

        # Construction de l'URL
        pdf_url = f"/api/generate-global-pdf/?mois={mois}&token={token}"

        # Ouverture dans nouvel onglet
        page.launch_url(
            pdf_url,
            web_window_name="_blank"
        )
        
        # Feedback utilisateur
        message.value = "Génération du rapport global en cours..."
        message.color = "green"
        page.update()

    # Configuration des événements
    generate_btn.on_click = generate_pdf

    return ft.Column(
        controls=[
            ft.Text("Génération de rapport global", size=20, weight="bold"),
            ft.Row([ mois_input,
            generate_btn], spacing=12, alignemt=ft.MainAxisAlignment.CENTER),
            message
        ],
        spacing=20,
        horizontal_alignment="center",
        alignment=ft.MainAxisAlignment.CENTER,
        width=400
    )