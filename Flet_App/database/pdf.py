import flet as ft

def rapport_view(page: ft.Page):
    token = page.session.get("token")
    
    # Composants UI
    mois_input = ft.TextField(label="Mois (AAAA-MM)", width=300)
    message = ft.Text()
    generate_btn = ft.ElevatedButton("Générer le PDF")
    
    def generate_pdf(e):
        mois = mois_input.value.strip()
        if not mois:
            message.value = "Veuillez entrer un mois valide"
            page.update()
            return
        
        # Construction de l'URL avec le token
        pdf_url = f"https://financial-flow.onrender.com/generate-pdf/?mois={mois}"
        
        # Solution 1: Ouverture dans un nouvel onglet (recommandé)
        page.launch_url(pdf_url)
        
        # Solution alternative: Téléchargement forcé
        # page.launch_url(pdf_url + "&download=1")
        
    generate_btn.on_click = generate_pdf
    
    return ft.Column(
        controls=[
            ft.Text("Génération de rapport PDF", size=20),
            mois_input,
            generate_btn,
            message
        ],
        spacing=20
    )