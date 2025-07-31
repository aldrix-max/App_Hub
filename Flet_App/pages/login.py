# Importation de la fonction login_user depuis api.py
from database.api import login_user
# Importation de Flet pour l'interface utilisateur
from flet import *

def login_view(page: Page):
    # Crée une vue de connexion Flet avec gestion d'authentification.
    # Composants UI
    
    page.title = "Connexion"  # Titre de la page
    page.theme_mode = ThemeMode.DARK # Mode de thème clair
    page.padding= 0  # Pas de marge autour de la page
    
    
    username = TextField(label="Nom complet",label_style=TextStyle(italic=True, color="#2563eb"),border_radius=8,width=350, filled=True, bgcolor="white", border_color="#2563eb",
                            color="black")
    password = TextField(label="Mot de passe",label_style=TextStyle(italic=True, color="#2563eb"), password=True,width=350, can_reveal_password=True,shift_enter=True,
                             border_radius=8, filled=True, bgcolor="white", border_color="#2563eb",color="black")
    message = Text("", size=16, color="black")  # Pour afficher les messages d'erreur/succès

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
            [   Column([
                Image(src="logo.png", width=350, height=250, fit=ImageFit.CONTAIN),
                Text("Connectez-vous pour accéder à l'application", size=16, weight="bold", color="#1f2937")
            ], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER),
                Row([Text("nom d'utilisateur par defaut: admin", size=12, color="#6b7280"),
                      Text(" mot de passe: admin123", size=12, color="#6b7280")], alignment=MainAxisAlignment.SPACE_BETWEEN),
                username,
                password,
                ElevatedButton("Se connecter",on_click=on_login,width=350, color="white", bgcolor="#2563eb",
                               style=ButtonStyle(shape=RoundedRectangleBorder(radius=2))),
                message
            ],
            spacing=20,
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.STRETCH
        ),
        width=400,
        height= 800,
        alignment=Alignment(0,0),
        padding=20,
        border_radius=12,
        bgcolor="#ffffff",
        shadow=BoxShadow(blur_radius=20, color=Colors.BLACK12, offset=Offset(0, 6))
    )
    
    # contruction du background
    background=Container(
        image=DecorationImage(
            src="background2.png",
            fit=ImageFit.COVER,
            opacity=0.5,
            filter_quality=FilterQuality.LOW
        ),
        content=Container(
            content=form,
            alignment=Alignment(0, 0),  # Centrer le formulaire
            padding=50
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