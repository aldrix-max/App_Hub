import flet as ft
import datetime
import os
from database.api import download_summary_pdf
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
    message = ft.Text(value="", size=16)
    

    def exporter_rapport(e):
        mois = mois_input.value.strip()
        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            page.update()
            return

        message.value = "⏳ Génération du rapport en cours..."
        page.update()

        try:
            filename = download_summary_pdf(token, mois)  # Télécharge le PDF
            if filename:
                message.value = f"✅ Rapport généré pour {mois}"
            else:
                message.value = "❌ Échec lors de la récupération du fichier PDF."
        except Exception as ex:
            message.value = f"❌ Erreur : {ex}"

        page.update()

    return ft.Column(
        controls=[
            ft.Text("Générer un rapport mensuel", size=22, weight="bold", color="black"),
            ft.Row([mois_input, ft.ElevatedButton("Télécharger le résumé", on_click=exporter_rapport,style=ft.ButtonStyle(
            padding=20,bgcolor=ft.Colors.INDIGO_600 ,color="white",shape=ft.RoundedRectangleBorder(radius=10),),width=300,height=50,)]),
            message,
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30
    )
    
def download_summary_pdf(token: str, mois: str, agent_id=None):
    """Génère un PDF pour un mois donné, optionnellement filtré par agent"""
    base_url = "http://127.0.0.1:8000/api/export/pdf/"
    params = f"?mois={mois}&type=resume"
    if agent_id:
        params += f"&agent_id={agent_id}"
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(base_url + params, headers=headers)
        if response.status_code == 200:
            filename = f"rapport_{mois}"
            if agent_id:
                filename += f"_agent_{agent_id}"
            filename += ".pdf"
            
            with open(filename, "wb") as f:
                f.write(response.content)
            return os.path.abspath(filename)
        return None
    except Exception as e:
        print(f"Erreur download_summary_pdf: {e}")
        return None
