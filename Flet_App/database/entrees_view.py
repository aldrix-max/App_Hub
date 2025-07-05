import flet as ft
from database.api import *

def entree_view(page: ft.Page, return_callback):
    """Vue des entrées avec un bouton de retour"""
    
    token = page.session.get("token")
    if not token:
        page.go("/")
        return

    # --- Filtres ---
    search_input = ft.TextField(
        label="🔍 Rechercher",
        color="black",
        border_color="black",
        width=200,
        on_change=lambda e: charger()
    )

    categorie_filter = ft.Dropdown(
        label="📂 Filtrer",
        width=150,
        options=[],
        on_change=lambda e: charger()
    )

    message = ft.Text()

    # --- Tableau ---
    datatable = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("DATE")),
            ft.DataColumn(label=ft.Text("CATEGORIE")),
            ft.DataColumn(label=ft.Text("MONTANT")),
            ft.DataColumn(label=ft.Text("DESCRIPTION")),
        ],
        rows=[],
        border_radius=0,
        heading_row_height=50,
        heading_text_style=ft.TextStyle(color=ft.Colors.GREY_600,weight="bold", size=18),
        column_spacing=30,
        divider_thickness=0,
    )

    # Bouton de retour
    return_button = ft.IconButton(
        icon_color=ft.Colors.INDIGO_600,
        icon_size=20,
        icon=ft.Icons.ARROW_BACK,
        on_click=return_callback,
    )

    def charger_categories():
        cats = get_categories(token)
        categorie_filter.options = [ft.dropdown.Option("", "Toutes")] + [
            ft.dropdown.Option(str(cat["id"]), cat["nom"]) 
            for cat in cats 
            if cat["type"] == "ENTREE"
        ]
        page.update()

    def charger():
        data = get_entrees(token, search=search_input.value, categorie_name=categorie_filter.value)
        datatable.rows.clear()
        
        if not data:
            message.value = "❌ Aucune entrée trouvée."
        else:
            message.value = f"✅ {len(data)} entrée(s) trouvée(s)"
            for op in data:
                datatable.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(op["date"], color="black")),
                        ft.DataCell(ft.Text(op["categorie_nom"], color="black")),
                        ft.DataCell(ft.Text(f"{op['montant']}", color="black")),
                        ft.DataCell(ft.Text(op["description"], color="black")),
                    ]))
        page.update()

    # Initialisation
    charger_categories()
    charger()

    return ft.Column(
        controls=[
            ft.Row([
                return_button,
                ft.Text("Historique des entrées", size=22, color="black", weight="bold"),
                ft.Container(width=100),
                search_input, 
                categorie_filter
            ]),
            message,
            datatable
        ],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        width=800
    )