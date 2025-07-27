import flet as ft
from flet import *
from datetime import datetime
from database.api import get_categories, create_operation

def Operations(page: Page):
    # Définit la couleur de fond de la page
    page.bgcolor = "#f3f4f6"  # Gris clair

    # Récupère le token de session pour l'utilisateur connecté
    token = page.session.get("token")

    # Styles réutilisables pour les champs de formulaire
    field_style = {
        "border_color": "#2563eb",
        "border_radius": 10,
        "border_width": 1,
        "text_size": 14,
        "content_padding": 12,
    }
    text_style = {
        "color": "#1e293b",           # Couleur du texte (gris foncé)
        "cursor_color": "#2563eb",    # Couleur du curseur (bleu)
        "selection_color": "#93c5fd", # Couleur de la sélection (bleu clair)
    }

    # Titre du formulaire avec icône
    title = Container(
        content=Row(
            controls=[
                Text("Ajouter une Opération", size=16, weight="bold", color="#2563eb"),
            ],
            spacing=10,
        ),
        padding=padding.only(bottom=20),
    )

    # Dropdown pour choisir le type d'opération (dépense ou entrée)
    type_dropdown = Dropdown(
        label="Type d'opération",
        color="black",
        label_style=TextStyle(
            color="#1e293b",
            weight="bold",
            size=16,
        ),
        options=[
            dropdown.Option("DEPENSE", "Dépense"),
            dropdown.Option("ENTREE", "Entree"),
        ],
        **field_style,
        prefix_icon=Icon(Icons.CATEGORY, color="#2563eb"),
        width=300
    )

    # Dropdown pour choisir la catégorie (rempli dynamiquement)
    categories_dropdown = Dropdown(
        label="Catégorie",
        color="black",
        label_style=TextStyle(
            color="#1e293b",
            weight="bold",
            size=16,
        ),
        options=[],  # Rempli selon le type sélectionné
        **field_style,
        prefix_icon=Icon(Icons.LIST, color="#2563eb"),
        width=300
    )

    # Champ pour saisir le montant de l'opération
    montant = TextField(
        label="Montant",
        label_style=TextStyle(
            color="#1e293b",
            weight="bold",
            size=16,
        ),
        keyboard_type=KeyboardType.NUMBER,
        **field_style,
        **text_style,
        prefix_icon=Icon(Icons.ATTACH_MONEY, color="#2563eb"),
        suffix_text="$",
        width=300
    )

    # Champ pour saisir une description de l'opération
    description = TextField(
        label="Description",
        label_style=TextStyle(
            color="#1e293b",
            weight="bold",
            size=16,
        ),
        multiline=True,
        min_lines=3,
        max_lines=5,
        **field_style,
        **text_style,
        prefix_icon=Icon(Icons.DESCRIPTION, color="#2563eb"),
        width=300
    )

    # Champ pour saisir la date de l'opération (format AAAA-MM-JJ)
    date_field = TextField(
        label="Date",
        hint_text="AAAA-MM-JJ",
        label_style=TextStyle(
            color="#1e293b",
            weight="bold",
            size=16,
        ),
        **field_style,
        **text_style,
        prefix_icon=Icon(Icons.CALENDAR_TODAY, color="#2563eb"),
        value=datetime.now().strftime("%Y-%m-%d"),  # Date du jour par défaut
        width=300
    )

    # Message de feedback pour l'utilisateur (succès ou erreur)
    message = Text("")

    # Bouton pour soumettre le formulaire
    submit_button = ElevatedButton(
        "Enregistrer",
        on_click=None,  # Sera défini plus tard
        icon=Icons.SAVE,
        style=ButtonStyle(
            padding=20,
            bgcolor="#2563eb",
            color="white",
            shape=RoundedRectangleBorder(radius=10),
        ),
        width=300,
        height=50,
    )

    # Fonction pour charger les catégories selon le type sélectionné
    def charger_categories():
        cats = get_categories(token)
        print(cats)
        if cats:
            # Filtre les catégories selon le type sélectionné (ou toutes si aucun type)
            categories_dropdown.options = [
                dropdown.Option(str(c["id"]), f"{c['nom']} ({c['type']})")
                for c in cats
                if c.get('type') == type_dropdown.value or type_dropdown.value is None
            ]
        else:
            message.value = "⚠️ Impossible de charger les catégories"
        page.update()

    # Met à jour les catégories quand on change le type d'opération
    def on_type_change(e):
        charger_categories()

    type_dropdown.on_change = on_type_change

    # Fonction appelée lors de la soumission du formulaire
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

        # Vérifie que le montant est bien un nombre
        try:
            float(montant.value)
        except ValueError:
            message.value = "❗ Le montant doit être un nombre"
            page.update()
            return

        # Vérifie que la date est renseignée
        if not date_field.value:
            message.value = "❗ Veuillez saisir une date"
            page.update()
            return

        # Vérifie que la date est au bon format (AAAA-MM-JJ)
        try:
            datetime.strptime(date_field.value, "%Y-%m-%d")
        except ValueError:
            message.value = "❗ Format de date invalide (AAAA-MM-JJ requis)"
            page.update()
            return

        # Prépare les données à envoyer à l'API
        data = {
            "type": type_dropdown.value,              # Type d'opération (DEPENSE ou ENTREE)
            "categorie": categories_dropdown.value,   # ID de la catégorie sélectionnée
            "montant": montant.value,                 # Montant saisi
            "description": description.value,         # Description saisie
            "date": date_field.value                  # Date saisie
        }

        # Appelle l'API pour créer l'opération
        res = create_operation(token, data)

        if res.status_code == 201:
            # Succès : affiche un message et réinitialise les champs
            message.value = "✅ Opération enregistrée avec succès."
            message.color = "green"
            montant.value = ""
            description.value = ""
            categories_dropdown.value = None
            type_dropdown.value = None
        else:
            # Erreur lors de l'enregistrement
            message.value = f"❌ Erreur lors de l'enregistrement ({res.status_code})"
            message.color = "red"

        page.update()

    # Associe la fonction d'envoi au bouton
    submit_button.on_click = envoyer

    # Charge les catégories au démarrage
    charger_categories()

    # Conteneur principal du formulaire avec style
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
        ),
        padding=padding.all(10),
        border_radius=10,
        bgcolor="white",
        width=350
    )

    # Retourne le formulaire centré dans la page
    return form_container