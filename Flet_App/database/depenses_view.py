import flet as ft
from database.api import *

def depenses_view(page: ft.Page, return_callback):
    """Vue des dépenses avec un bouton de retour"""

    token = page.session.get("token")
    if not token:
        page.go("/")
        return

    # --- Filtres ---
    # Champ de recherche pour filtrer les dépenses par description
    search_input = ft.TextField(
        label="🔍 Rechercher",
        color="black",
        width=200,
        on_change=lambda e: charger()  # Recharge la table à chaque changement
    )

    # Dropdown pour filtrer par catégorie de dépense
    categorie_filter = ft.Dropdown(
        label="📂 Filtrer",
        color="black",
        width=150,
        options=[],  # Rempli dynamiquement dans charger_categories()
        on_change=lambda e: charger()  # Recharge la table à chaque changement
    )

    # Message d'information (ex: nombre de résultats)
    message = ft.Text(color="black")

    # --- Tableau des dépenses ---
    datatable = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("DATE")),
            ft.DataColumn(label=ft.Text("CATEGORIE")),
            ft.DataColumn(label=ft.Text("MONTANT")),
            ft.DataColumn(label=ft.Text("DESCRIPTION")),
        ],
        rows=[],  # Rempli dynamiquement dans charger()
        border_radius=0,
        heading_row_height=50,
        heading_text_style=ft.TextStyle(color=ft.Colors.GREY_600, weight="bold", size=18),
        column_spacing=30,
        divider_thickness=0,
    )

    # --- Bouton de retour ---
    # Permet de revenir à la vue précédente (callback passé en paramètre)
    return_button = ft.IconButton(
        icon_color=ft.Colors.INDIGO_600,
        icon_size=20,
        icon=ft.Icons.ARROW_BACK,
        on_click=return_callback,
    )

    # --- Fonction pour charger les catégories de type "DEPENSE" ---
    def charger_categories():
        cats = get_categories(token)
        # On ajoute une option "Toutes" puis on filtre les catégories de type DEPENSE
        categorie_filter.options = [ft.dropdown.Option("", "Toutes")] + [
            ft.dropdown.Option(str(cat["id"]), cat["nom"]) 
            for cat in cats 
            if cat["type"] == "DEPENSE"
        ]
        page.update()

    # --- Fonction pour charger et afficher les dépenses selon les filtres ---
    def charger():
        # Appel API pour récupérer les dépenses filtrées
        data = get_depenses(token, search=search_input.value, categorie_name=categorie_filter.value)
        datatable.rows.clear()  # On vide le tableau avant de le remplir

        if not data:
            message.value = "❌ Aucune dépense trouvée."
        else:
            message.value = f"✅ {len(data)} dépense(s) trouvée(s)"
            for op in data:
                # Ajoute chaque dépense comme une ligne du tableau
                datatable.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(op["date"], color="black")),
                        ft.DataCell(ft.Text(op["categorie_nom"], color="black")),
                        ft.DataCell(ft.Text(f"{op['montant']}", color="black")),
                        ft.DataCell(ft.Text(op["description"], color="black")),
                    ]))
        page.update()

    # --- Initialisation de la vue ---
    charger_categories()  # Charge les catégories dans le filtre
    charger()             # Charge les dépenses dans le tableau

    # --- Construction de la vue Flet ---
    return ft.Column(
        controls=[
            ft.Row([
                return_button,  # Bouton retour
                ft.Text("Historique des dépenses", size=22, color="black", weight="bold"),
                ft.Container(width=100),  # Espaceur
                search_input, 
                categorie_filter
            ]),
            message,    # Message d'information
            datatable   # Tableau des dépenses
        ],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True
    )