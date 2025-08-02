import flet as ft
import base64
import re
import requests

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
    pdf_viewer = ft.Column(visible=False)

    def exporter_rapport(e):
        mois = mois_input.value.strip()

        # Vérification du format AAAA-MM
        if not re.match(r"^\d{4}-\d{2}$", mois):
            message.value = "❌ Veuillez entrer un mois valide au format AAAA-MM"
            pdf_viewer.visible = False
            page.update()
            return

        message.value = "⏳ Génération du rapport..."
        pdf_viewer.visible = False
        page.update()

        try:
            pdf_url = f"https://financial-flow.onrender.com/api/export/pdf/?mois={mois}&type=resume"
            headers = {"Authorization": f"Token {token}"}
            response = requests.get(pdf_url, headers=headers)

            if response.status_code == 200:
                pdf_bytes = response.content
                pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
                data_url = f"data:application/pdf;base64,{pdf_b64}"

                download_button = ft.ElevatedButton(
                    "📄 Télécharger le rapport",
                    on_click=lambda _: page.launch_url(data_url),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.INDIGO_100,
                        color=ft.Colors.INDIGO_800
                    )
                )

                pdf_viewer.controls = [download_button]
                pdf_viewer.visible = True
                message.value = "✅ Rapport généré avec succès"
            elif response.status_code == 401:
                message.value = "❌ Accès non autorisé : token invalide ou expiré"
            else:
                message.value = f"❌ Erreur {response.status_code} : {response.text}"

        except Exception as ex:
            message.value = f"❌ Erreur de connexion : {str(ex)}"

        page.update()

    return ft.Column(
        controls=[
            ft.Text("Générer un rapport mensuel", size=22, weight="bold", color="black"),
            ft.Row([
                mois_input,
                ft.ElevatedButton(
                    "Générer le rapport",
                    on_click=exporter_rapport,
                    style=ft.ButtonStyle(
                        padding=20,
                        bgcolor=ft.Colors.INDIGO_600,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=300,
                    height=50
                )
            ]),
            message,
            pdf_viewer
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30
    )
