import flet as ft
import requests
from database.api import API_BASE

def rapport_view_Admin(page: ft.Page):
    token = page.session.get("token")
    role = page.session.get("role")

    if not token or role != "ADMIN":
        page.go("/")
        return

    agent_dropdown = ft.Dropdown(
        label="Agent",
        label_style=ft.TextStyle(color="black"),
        width=300,
        color="black",
        options=[]
    )

    def get_all_agents(token):
        try:
            response = requests.get(
                f"{API_BASE}agents/all/",
                headers={"Authorization": f"Token {token}"},
                timeout=5
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Erreur get_all_agents: {e}")
            return []

    def load_agents():
        agents = get_all_agents(token)
        agent_dropdown.options = [
            ft.dropdown.Option(str(agent['id']), agent['name'])
            for agent in agents
        ]
        page.update()

    load_agents()

    mois_input = ft.TextField(
        label="Mois (AAAA-MM)",
        label_style=ft.TextStyle(color="black"),
        color="black",
        border_color=ft.Colors.INDIGO_600,
        hint_text="2025-06",
        width=400
    )
    message = ft.Text(value="", size=16, color="black")
    lien_rapport = ft.TextButton(visible=False)

    def exporter_rapport(e):
        mois = mois_input.value.strip()
        agent_id = agent_dropdown.value

        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            lien_rapport.visible = False
            page.update()
            return

        if not agent_id:
            message.value = "❌ Veuillez sélectionner un agent"
            lien_rapport.visible = False
            page.update()
            return

        message.value = "⏳ Génération du lien du rapport..."
        page.update()

        # Génère l’URL directe du PDF de l’agent
        pdf_url = f"{API_BASE}export/pdf/agent/?mois={mois}&agent_id={agent_id}"

        lien_rapport.text = "📄 Ouvrir le rapport PDF"
        lien_rapport.url = pdf_url
        lien_rapport.visible = True
        message.value = "✅ Lien prêt. Cliquez ci-dessous pour ouvrir :"
        page.update()

    return ft.Column(
        controls=[
            ft.Text("Générer un rapport par agent", size=22, weight="bold", color="black"),
            ft.Row([
                agent_dropdown,
                mois_input,
                ft.ElevatedButton(
                    "Générer le rapport",
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
            ], wrap=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            message,
            lien_rapport
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30,
        expand=True
    )

def rapport_view_global(page: ft.Page):
    token = page.session.get("token")
    role = page.session.get("role")

    if not token or role != "ADMIN":
        page.go("/")
        return

    mois_input = ft.TextField(
        label="Mois (AAAA-MM)",
        color="black",
        border_color=ft.Colors.INDIGO_600,
        hint_text="2025-06",
        width=400
    )
    message = ft.Text(value="", size=16, color=ft.Colors.BLACK)
    lien_rapport = ft.TextButton(visible=False)

    def exporter_rapport(e):
        mois = mois_input.value.strip()

        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            lien_rapport.visible = False
            page.update()
            return

        message.value = "⏳ Génération du lien du rapport global..."
        page.update()

        # Génère l’URL directe du PDF global
        pdf_url = f"{API_BASE}export/pdf/global/?mois={mois}"

        lien_rapport.text = "📄 Ouvrir le rapport global"
        lien_rapport.url = pdf_url
        lien_rapport.visible = True
        message.value = "✅ Lien prêt. Cliquez ci-dessous pour ouvrir :"
        page.update()

    return ft.Column(
        controls=[
            ft.Text("Générer un rapport global mensuel", size=22, weight="bold", color="black"),
            ft.Row([
                mois_input,
                ft.ElevatedButton(
                    "Générer le rapport global",
                    on_click=exporter_rapport,
                    style=ft.ButtonStyle(
                        padding=20,
                        bgcolor=ft.Colors.INDIGO_600,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=300,
                    height=50,
                )
            ], wrap=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            message,
            lien_rapport
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30,
        expand=True
    )
