import flet as ft
from database.api import *

def entree_view(page: ft.Page):
    token = page.session.get("token")
    if not token:
        page.go("/")
        return

    # Filtres
    search_input = ft.TextField(label="🔍 Rechercher une entrée", width=300, on_change=lambda e: charger())
    categorie_filter = ft.Dropdown(label="📂 Filtrer par catégorie", width=250, options=[], on_change=lambda e: charger())
    message = ft.Text()

    # Table
    datatable = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Date")),
            ft.DataColumn(label=ft.Text("Catégorie")),
            ft.DataColumn(label=ft.Text("Montant")),
            ft.DataColumn(label=ft.Text("Description")),
        ],
        rows=[]
    )

    # 🔃 Charger catégories dans le filtre
    def charger_categories():
        cats = get_categories(token)
        categorie_filter.options = [ft.dropdown.Option("", "Toutes")] + [
            ft.dropdown.Option(str(cat["id"]), cat["nom"]) for cat in cats if cat["type"] == "ENTREE"
        ]
        page.update()

    # 📥 Charger les entrees dans le tableau
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
                        ft.DataCell(ft.Text(op["date"])),
                        ft.DataCell(ft.Text(op["categorie_nom"])),
                        ft.DataCell(ft.Text(f"{op['montant']} FC")),
                        ft.DataCell(ft.Text(op["description"])),
                    ])
                )
                
        page.update()

    # Initialisation
    charger_categories()
    charger()

    return ft.Column(
        
        controls=[
            ft.Text("📊 Entrées enregistrées", size=30, weight="bold"),
            ft.Divider(),
            ft.Row([search_input, categorie_filter]),
            message,
            datatable
        ],
        scroll=ft.ScrollMode.AUTO,
        width=800
    )
