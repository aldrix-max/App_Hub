import flet as ft
import base64

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
    pdf_viewer = ft.Column([], visible=False)

    async def exporter_rapport(e):
        mois = mois_input.value.strip()
        if not mois:
            message.value = "❌ Veuillez entrer un mois au format AAAA-MM"
            await page.update_async()
            return

        message.value = "⏳ Génération du rapport en cours..."
        pdf_viewer.visible = False
        await page.update_async()

        try:
            # Télécharger le PDF via l'API
            pdf_url = f"https://financial-flow.onrender.com/api/export/pdf/?mois={mois}&type=resume"
            headers = {"Authorization": f"Token {token}"}
            
            response = await page.http_client.get_async(pdf_url, headers=headers)
            
            if response.status_code == 200:
                pdf_bytes = await response.read()
                pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
                
                # Créer un lien de téléchargement
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
                        shape=ft.RoundedRectangleBorder(radius=10),
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