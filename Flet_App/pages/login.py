# Importation de la fonction login_user depuis api.py
from database.api import login_user
# Importation de Flet pour l'interface utilisateur
from flet import *

def login_view(page: Page):
    # Crée une vue de connexion Flet avec gestion d'authentification.
    # Composants UI
    
    page.title = "Connexion"  # Titre de la page
    page.theme_mode = ThemeMode.DARK  # Mode de thème clair
    
    
    username = TextField(label="Nom complet",label_style=TextStyle(italic=True, color="#2563eb"),border_radius=8,width=350, filled=True, bgcolor="white", border_color="#2563eb",
                             focused_border_color="#2563eb",shift_enter=True, )
    password = TextField(label="Mot de passe",label_style=TextStyle(italic=True, color="#2563eb"), password=True,width=350, can_reveal_password=True,shift_enter=True,
                             border_radius=8, filled=True, bgcolor="white", border_color="#2563eb",)
    message = Text("")  # Pour afficher les messages d'erreur/succès

    def on_login(e):
        # Appel à l'API Django
        response = login_user(username.value, password.value)
        
        if response is None:
            message.value = "❌ Serveur Django inaccessible"
        elif response.status_code == 200:
            # Succès - extraction des données
            data = response.json()
            token = data.get("token")
            role = data.get("role")
            username_session = data.get("username")
            
            # Stockage dans la session Flet
            page.session.set("token", token)  # Token d'authentification
            page.session.set("role", role)    # Rôle de l'utilisateur
            page.session.set("username", username_session)  # Nom d'utilisateur
            
            # Redirection basée sur le rôle
            if role == "ADMIN":
                page.go("/admin-dashboard")
            elif role == "AGENT":
                page.go("/agent-dashboard")
            elif role == "AUTRE":
                page.go("/visionneur-dashboard")
        else:
            message.value = "❌ Identifiants incorrects"
        
        page.update()  # Met à jour l'interface
        
        
    # construction du formulaire
    form = Container(
        content=Column(
            [
                Text("Se connecter ", size=30, weight="bold", color="#1f2937"),
                username,
                password,
                ElevatedButton("Se connecter",on_click=on_login,width=350, color="white", bgcolor="#2563eb",
                               style=ButtonStyle(shape=RoundedRectangleBorder(radius=6))),
                message
            ],
            spacing=20,
            tight=True
        ),
        width=400,
        alignment=Alignment(0,0),
        padding=30,
        border_radius=12,
        bgcolor="#ffffff",
        shadow=BoxShadow(blur_radius=20, color=Colors.BLACK12, offset=Offset(0, 6))
    )
    
    # contruction du background
    background=Container(
        image=DecorationImage(
            src="Flet_App/assets/background3.png",
            fit=ImageFit.COVER,
            opacity=0.3,
            filter_quality=FilterQuality.LOW
        ),
        content=Container(
            content=form,
            alignment=Alignment(0, 0),  # Centrer le formulaire
            padding=20
        ),
        expand=True,  # Permet à l'image de couvrir tout l'espace disponible
        alignment=Alignment(0, 0)  # Centrer l'image
        
    )


    # Construction de la vue
    return View(
        "/",  # Route racine
        controls=[
          background
        ]
    )