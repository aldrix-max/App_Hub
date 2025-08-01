import flet as ft
import os
import requests
import tempfile
import webbrowser

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

    def download_summary_pdf(token: str, mois: str):
        """Télécharge le PDF dans un fichier temporaire"""
        base_url = "https://financial-flow.onrender.com/api/export/pdf/"
        params = f"?mois={mois}&type=resume"
        headers = {"Authorization": f"Token {token}"}
        
        try:
            response = requests.get(base_url + params, headers=headers)
            if response.status_code == 200:
                temp_dir = tempfile.gettempdir()
                temp_pdf_path = os.path.join(temp_dir, f"rapport_{mois}.pdf")
                
                with open(temp_pdf_path, "wb") as f:
                    f.write(response.content)
                return temp_pdf_path
            return None
        except Exception as e:
            print(f"Erreur download_summary_pdf: {e}")
            return None

    def exporter_rapport(e):
        mois = mois_input.value.strip()
        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            page.update()
            return

        message.value = "⏳ Génération du rapport en cours..."
        page.update()

        try:
            final_path = download_summary_pdf(token, mois)
            if final_path:
                message.value = "✅ Rapport généré ! Ouverture dans le navigateur..."
                webbrowser.open(f"file://{final_path}")
            else:
                message.value = "❌ Échec lors de la génération du PDF"
        except Exception as ex:
            message.value = f"❌ Erreur : {ex}"

        page.update()

    return ft.Column(
        controls=[
            ft.Text("Générer un rapport mensuel", size=22, weight="bold", color="black"),
            ft.Row([
                mois_input, 
                ft.ElevatedButton(
                    "Télécharger le résumé",
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
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30
    )
