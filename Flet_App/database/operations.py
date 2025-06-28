import flet as ft
from flet import *
from datetime import datetime
from database.api import get_categories, create_operation

def Operations(page: Page):
    page.bgcolor="#f3f4f6"  # Couleur de fond gris clair
    token = page.session.get("token")

    # Style commun pour les champs
    field_style = {
        "border_color": "#2563eb",
        "border_radius": 10,
        "border_width": 1,
        "text_size": 14,
        "content_padding": 12,
    }
    text_style = {
    "color": "#1e293b",  # Couleur du texte (gris foncé)
    "cursor_color": "#2563eb",  # Couleur du curseur (bleu)
    "selection_color": "#93c5fd",  # Couleur de la sélection (bleu clair)
}

    # Titre avec icône
    title = Container(
        content=Row(
            controls=[
                Text("Ajouter une Opération", size=24, weight="bold", color="#2563eb"),
            ],
            spacing=10,
        ),
        padding=padding.only(bottom=20),
    )

    # Champ type (dépense ou recette)
    type_dropdown = Dropdown(
        label="Type d'opération",
        color="black", 
        label_style=TextStyle(
            color="#1e293b",  # Couleur du texte du label
            weight="bold",  # Met le label en gras
            size=16,  # Taille du texte du label
        ),
        options=[
            dropdown.Option("DEPENSE", "Dépense"),
            dropdown.Option("ENTREE", "Entree"),
        ],
        **field_style,
        prefix_icon=Icon(Icons.CATEGORY, color="#2563eb"),
        width=400
    )

    # Champ catégorie
    categories_dropdown = Dropdown(
        label="Catégorie",
        color="black", 
        label_style=TextStyle(
            color="#1e293b",  # Couleur du texte du label
            weight="bold",  # Met le label en gras
            size=16,  # Taille du texte du label
        ),
        options=[],
        **field_style,
        prefix_icon=Icon(Icons.LIST, color="#2563eb"),
        
        width=400
    )

    # Champ montant
    montant = TextField(
        label="Montant", 
        label_style=TextStyle(
            color="#1e293b",  # Couleur du texte du label
            weight="bold",  # Met le label en gras
            size=16,  # Taille du texte du label
        ),
        keyboard_type=KeyboardType.NUMBER,
        **field_style,
        **text_style,
        prefix_icon=Icon(Icons.ATTACH_MONEY, color="#2563eb"),
        suffix_text="$",
        width=400
        
    )

    # Champ description
    description = TextField(
        label="Description", 
        label_style=TextStyle(
            color="#1e293b",  # Couleur du texte du label
            weight="bold",  # Met le label en gras
            size=16,  # Taille du texte du label
        ),
        multiline=True,
        min_lines=3,
        max_lines=5,
        **field_style,
        **text_style,
        prefix_icon=Icon(Icons.DESCRIPTION, color="#2563eb"),
        width=400
    )

    # Champ date
    date_field = TextField(
        label="Date", 
        hint_text="AAAA-MM-JJ",
        label_style=TextStyle(
            color="#1e293b",  # Couleur du texte du label
            weight="bold",  # Met le label en gras
            size=16,  # Taille du texte du label
        ),
        **field_style,
        **text_style,
        prefix_icon=Icon(Icons.CALENDAR_TODAY, color="#2563eb"),
        value=datetime.now().strftime("%Y-%m-%d"),
        width=400
    )

    # Message de feedback
    message = Text("")

    # Bouton d'envoi
    submit_button = ElevatedButton(
        "Enregistrer",
        on_click=None,  # Ser défini plus tard
        icon=Icons.SAVE,
        style=ButtonStyle(
            padding=20,
            bgcolor="#2563eb",
            color="white",
            shape=RoundedRectangleBorder(radius=10),
        ),
        width=400,
        height=50,
    )

    def charger_categories():
        cats = get_categories(token)
        if cats:
            categories_dropdown.options = [
                dropdown.Option(str(c["id"]), f"{c['nom']} ({c['type']})")
                for c in cats
                if c.get('type') == type_dropdown.value or type_dropdown.value is None
            ]
        else:
            message.value = "⚠️ Impossible de charger les catégories"
        page.update()

    def on_type_change(e):
        charger_categories()

    type_dropdown.on_change = on_type_change

    def envoyer(e):
        # Validation des champs
        if not type_dropdown.value:
            message.value = "❗ Veuillez sélectionner un type d'opération"
            page.update()
            return
            
        if not categories_dropdown.value:
            message.value = "❗ Veuillez sélectionner une catégorie"
            page.update()
            return
            
        if not montant.value:
            message.value = "❗ Veuillez saisir un montant"
            page.update()
            return
            
        try:
            float(montant.value)
        except ValueError:
            message.value = "❗ Le montant doit être un nombre"
            page.update()
            return
            
        if not date_field.value:
            message.value = "❗ Veuillez saisir une date"
            page.update()
            return
            
        try:
            datetime.strptime(date_field.value, "%Y-%m-%d")
        except ValueError:
            message.value = "❗ Format de date invalide (AAAA-MM-JJ requis)"
            page.update()
            return

        data = {
            "type": type_dropdown.value,
            "categorie": categories_dropdown.value,
            "montant": montant.value,
            "description": description.value,
            "date": date_field.value
        }

        res = create_operation(token, data)

        if res.status_code == 201:
            message.value = "✅ Opération enregistrée avec succès."
            message.color = "green"
            # Réinitialisation des champs
            montant.value = ""
            description.value = ""
            categories_dropdown.value = None
            type_dropdown.value = None
        else:
            message.value = f"❌ Erreur lors de l'enregistrement ({res.status_code})"
            message.color = "red"

        page.update()

    # Assigner la fonction au bouton
    submit_button.on_click = envoyer

    # Charger les catégories au démarrage
    charger_categories()

    # Conteneur principal avec ombre et bordure arrondie
    form_container = Container(
        content=Column(
            controls=[
                title,
                type_dropdown,
                categories_dropdown,
                montant,
                description,
                date_field,
                submit_button, 
                message,
            ],
            spacing=15,
            scroll=ScrollMode.AUTO,
            expand=True,
        ),
        padding=padding.all(30),
        border_radius=15,
        bgcolor="white",
        width=450
    )

    # Centrer le formulaire dans la page
    return form_container