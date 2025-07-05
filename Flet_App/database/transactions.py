import flet as ft
from database.api import get_transactions, get_categories
from database.depenses_view import *
from database.entrees_view import *

def transactions_view(page: ft.Page):
    token = page.session.get("token")
    if not token:
        page.go("/")
        return

    # --- Déclaration de la fonction show_main_view en premier ---
    def show_main_view(e=None):
        main_cont.controls.clear()
        main_cont.controls.extend([
            ft.Row([
                ft.Text("Historique des transactions", size=22, weight="bold", color="black"),
                ft.Container(width=150),
                ft.ElevatedButton(
                    "Voir dépenses", 
                    bgcolor=ft.Colors.RED_100, 
                    color="white", 
                    on_click=depenses,
                    width=150,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)))
                ,
                ft.ElevatedButton(
                    "Voir entrées", 
                    bgcolor=ft.Colors.GREEN_100, 
                    color="white", 
                    on_click=entrees,
                    width=150,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)))
            ]),
            table
        ])
        page.update()

    # --- Tableau principal des transactions ---
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("TYPE")),
            ft.DataColumn(ft.Text("MONTANT"), numeric=True),
            ft.DataColumn(ft.Text("DESCRIPTION")),
        ],
        rows=[],
        border_radius=0,
        heading_row_height=50,
        heading_text_style=ft.TextStyle(color=ft.Colors.GREY_600, weight="bold", size=18),
        column_spacing=70,
        divider_thickness=0,
       
    )

    message = ft.Text("", color=ft.Colors.GREY_600)

    # Chargement des données initiales
    data = get_transactions(token)
    if not data:
        message.value = "Aucune transaction trouvée"
    else:
        message.value = f"{len(data)} transactions trouvées"
        for tr in data:
            amount_color = ft.Colors.RED_600 if tr.get("type") == "DEPENSE" else ft.Colors.GREEN_600
            table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(tr.get("date", ""), color="black")),
                    ft.DataCell(ft.Text(tr.get("type", ""), color="black")),
                    ft.DataCell(ft.Text(f"{tr.get('montant', 0)} $", color=amount_color)),
                    ft.DataCell(ft.Text(tr.get("description", "-"), color="black")),
                ]))
    page.update()

    # Création des vues dépenses et entrées (après la définition de show_main_view)
    depenses_cont = depenses_view(page, show_main_view)
    entrees_cont = entree_view(page, show_main_view)

    # Fonctions de navigation
    def depenses(e):
        main_cont.controls.clear()
        main_cont.controls.append(depenses_cont)
        page.update()
        
    def entrees(e):
        main_cont.controls.clear()
        main_cont.controls.append(entrees_cont)
        page.update()

    # Conteneur principal
    main_cont = ft.Column(
        controls=[
            ft.Row([
                ft.Text("Historique des transactions", size=22, weight="bold", color="black"),
                ft.Container(width=150),
                ft.ElevatedButton("Voir dépenses", bgcolor=ft.Colors.RED_100, color="white", on_click=depenses,
                                   width=150,style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0))),
                ft.ElevatedButton("Voir entrées", bgcolor=ft.Colors.GREEN_100, color="white", on_click=entrees,
                                   width=150,style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)))
            ]),
            table
        ],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
        spacing=20
    )
    return main_cont