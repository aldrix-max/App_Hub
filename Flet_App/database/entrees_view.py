import flet as ft
from database.api import *

def entree_view(page: ft.Page, return_callback):
    """Vue des entrées (recettes) avec un bouton de retour et des filtres."""

    # Récupère le token utilisateur depuis la session
    token = page.session.get("token")
    if not token:
        page.go("/")
        return

    # --- Filtres ---
    # Champ de recherche pour filtrer les entrées par description
    search_input = ft.TextField(
        label="🔍 Rechercher",
        color="black",
        border_color="black",
        width=200,
        on_change=lambda e: charger()  # Recharge la table à chaque changement
    )

    # Dropdown pour filtrer par catégorie d'entrée
    categorie_filter = ft.Dropdown(
        label="📂 Filtrer",
        width=150,
        options=[],  # Rempli dynamiquement dans charger_categories()
        on_change=lambda e: charger()  # Recharge la table à chaque changement
    )

    # Message d'information (ex: nombre de résultats)
    message = ft.Text()

    # --- Tableau des entrées ---
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

    # --- Fonction pour charger les catégories de type "ENTREE" ---
    def charger_categories():
        cats = get_categories(token)
        # On ajoute une option "Toutes" puis on filtre les catégories de type ENTREE
        categorie_filter.options = [ft.dropdown.Option("", "Toutes")] + [
            ft.dropdown.Option(str(cat["id"]), cat["nom"]) 
            for cat in cats 
            if cat["type"] == "ENTREE"
        ]
        page.update()

    # --- Fonction pour charger et afficher les entrées selon les filtres ---
    def charger():
        # Appel API pour récupérer les entrées filtrées
        data = get_entrees(token, search=search_input.value, categorie_name=categorie_filter.value)
        datatable.rows.clear()  # On vide le tableau avant de le remplir

        if not data:
            message.value = "❌ Aucune entrée trouvée."
        else:
            message.value = f"✅ {len(data)} entrée(s) trouvée(s)"
            for op in data:
                # Ajoute chaque entrée comme une ligne du tableau
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
    charger()             # Charge les entrées dans le tableau

    # --- Construction de la vue Flet ---
    return ft.Column(
        controls=[
            ft.Row([
                return_button,  # Bouton retour
                ft.Text("Historique des entrées", size=22, color="black", weight="bold"),
                ft.Container(width=100),  # Espaceur
                search_input, 
                categorie_filter
            ]),
            message,    # Message d'information
            datatable   # Tableau des entrées
        ],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        width=800
    )