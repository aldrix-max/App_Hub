import flet as ft

def rapport_view(page: ft.Page):
    token = page.session.get("token")
    
    # Composants UI
    mois_input = ft.TextField(
        label="Mois (AAAA-MM)", 
        width=300,
        hint_text="Ex: 2025-07",
        keyboard_type="text"
    )
    message = ft.Text()
    generate_btn = ft.ElevatedButton("Générer le PDF")
    
    def generate_pdf(e):
        mois = mois_input.value.strip()
        
        # Validation simple du format
        if len(mois) != 7 or mois[4] != '-':
            message.value = "Format invalide. Utilisez AAAA-MM"
            message.color = "red"
            page.update()
            return
        
        # Construction de l'URL sécurisée
        pdf_url = (
            f"https://financial-flow.onrender.com/api/generate-pdf/"
            f"?mois={mois}&token={token}"
        )
        
        # Solution 1: Ouverture dans nouvel onglet
        page.launch_url(
            pdf_url,
            web_window_name="_blank"  # Force nouvel onglet
        )
        
        # Feedback utilisateur
        message.value = "Ouverture du PDF..."
        message.color = "green"
        page.update()
        
    generate_btn.on_click = generate_pdf
    
    return ft.Column(
        controls=[
            ft.Text("Génération de rapport PDF", size=20, weight="bold"),
            mois_input,
            generate_btn,
            message
        ],
        spacing=20,
        horizontal_alignment="center",
        width=400
    )