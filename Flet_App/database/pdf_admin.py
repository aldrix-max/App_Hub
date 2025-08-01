import flet as ft
import base64
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

    async def get_all_agents():
        try:
            response = await page.http_client.get_async(
                f"{API_BASE}agents/all/",
                headers={"Authorization": f"Token {token}"}
            )
            if response.status_code == 200:
                agents = await response.json()
                agent_dropdown.options = [
                    ft.dropdown.Option(str(agent['id']), agent['name'])
                    for agent in agents
                ]
                await page.update_async()
        except Exception as e:
            print(f"Erreur get_all_agents: {e}")

    get_all_agents()

    mois_input = ft.TextField(
        label="Mois (AAAA-MM)",
        label_style=ft.TextStyle(color="black"),
        color="black",
        border_color=ft.Colors.INDIGO_600,
        hint_text="2025-06",
        width=400
    )
    message = ft.Text(value="", size=16, color="black")
    pdf_viewer = ft.Column([], visible=False)

    async def exporter_rapport(e):
        mois = mois_input.value.strip()
        agent_id = agent_dropdown.value

        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            await page.update_async()
            return

        if not agent_id:
            message.value = "❌ Veuillez sélectionner un agent"
            await page.update_async()
            return

        message.value = "⏳ Génération du rapport en cours..."
        pdf_viewer.visible = False
        await page.update_async()

        try:
            pdf_url = f"{API_BASE}export/pdf/agent/?mois={mois}&agent_id={agent_id}"
            headers = {"Authorization": f"Token {token}"}
            
            response = await page.http_client.get_async(pdf_url, headers=headers)
            
            if response.status_code == 200:
                pdf_bytes = await response.read()
                pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
                
                download_button = ft.ElevatedButton(
                    "📄 Télécharger le rapport",
                    on_click=lambda _: page.launch_url(
                        f"data:application/pdf;base64,{pdf_b64}"
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.INDIGO_100,
                        color=ft.Colors.INDIGO_800
                    )
                )
                
                pdf_viewer.controls = [download_button]
                pdf_viewer.visible = True
                message.value = "✅ Rapport généré avec succès"
            else:
                message.value = f"❌ Erreur: {response.status_code} - {response.text}"
                
        except Exception as ex:
            message.value = f"❌ Erreur lors de la génération: {str(ex)}"
        
        await page.update_async()

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
            pdf_viewer
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=30,
        expand=True
    )