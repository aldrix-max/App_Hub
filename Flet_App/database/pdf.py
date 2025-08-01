import flet as ft

def rapport_view(page: ft.Page):
    token = page.session.get("token")
    if not token:
        page.go("/")
        return

    mois_input = ft.TextField(
        label="Mois (AAAA-MM)",
        color="black",
        border_color=ft.Colors.INDIGO_600,
        hint_text="2025-06",
        width=400
    )
    message = ft.Text(value="", size=16, color="black")
    lien_rapport = ft.TextButton(visible=False)

    def exporter_rapport(e):
        mois = mois_input.value.strip()
        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            lien_rapport.visible = False
            page.update()
            return

        message.value = "⏳ Génération du lien du rapport..."
        page.update()

        # Génère un lien direct vers le PDF fourni par ton backend
        pdf_url = f"https://financial-flow.onrender.com/api/export/pdf/?mois={mois}&type=resume"

        # Le lien est visible et cliquable
        lien_rapport.text = "📄 Ouvrir le rapport PDF"
        lien_rapport.url = pdf_url
        lien_rapport.visible = True
        message.value = "✅ Lien prêt. Cliquez ci-dessous pour ouvrir :"
        page.update()

    return ft.Column(
        controls=[
            ft.Text("Générer un rapport mensuel", size=22, weight="bold", color="black"),
            ft.Row([
                mois_input, 
                ft.ElevatedButton(
                    "Générer le lien du résumé",
                    on_click=exporter_rapport,
                    style=ft.ButtonStyle(
                        padding=20,
                        bgcolor=ft.Colors.INDIGO_600,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=300,
                    height=50
                )
            ]),
            message,
            lien_rapport
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30
    )
