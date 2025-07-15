from flet import *
from database.operations import Operations  
from database.api import *
from components.stats_card import stat_card
from database.depenses_view import depenses_view
from database.entrees_view import entree_view
from database.budget import *
from database.transactions import *
from database.pdf import *
from components.charts import *
from datetime import datetime

def agentdashboard(page: Page):
    # Configuration de base de la page
    page.bgcolor = Colors.GREY_100  # Fond gris clair pour l'interface
    
    # Vérification de l'authentification
    token = page.session.get("token")
    if not token:
        page.go("/")  # Redirection si non authentifié
        return

    # Initialisation de l'index du menu
    if not hasattr(page, "agent_selected_index"):
        page.agent_selected_index = 0

    # Vue Accueil - Tableau de bord
    def get_accueil_view():
        def affichage_accueil(token):
            stats = get_stats(token)
            if not stats:
                return Text("❌ Impossible de charger les statistiques.", color="red")

            # Cartes de statistiques
            cards = Row([
                stat_card("Entrees", f"{stats['resume'].get('total_entrees',0)} $", icon=Icons.ARROW_CIRCLE_UP_ROUNDED, color=Colors.GREEN_600),
                stat_card("Dépenses", f"{stats['resume'].get('total_depenses',0)} $", icon=Icons.ARROW_CIRCLE_DOWN_ROUNDED, color=Colors.RED_600),
                stat_card("Nb Entrees", stats['resume'].get('entrees',0), icon=Icons.ADD_CHART, color=Colors.INDIGO_600),
                stat_card("Nb Dépenses", stats['resume'].get('depenses',0), icon=Icons.REMOVE_CIRCLE, color=Colors.INDIGO_600)
            ], width=page.width, wrap=True, spacing=10, alignment=MainAxisAlignment.SPACE_BETWEEN)

            # Tableau des dernières opérations
            tableau = DataTable(
                columns=[
                    DataColumn(Text("DATE"), numeric=True),
                    DataColumn(Text("TYPE")),
                    DataColumn(Text("CATEGORIE")),
                    DataColumn(Text("MONTANT"), numeric=True),
                    DataColumn(Text("DESCRIPTION")),
                ],
                rows=[
                    DataRow(
                        cells=[
                            DataCell(Text(op["date"],color="black")),
                            DataCell(Text(op["type"], color="black")),
                            DataCell(Text(op["categorie_nom"], color="black")),
                            DataCell(Text(f"{op['montant']} $", color="black"),),
                            DataCell(Text(op['description'], color="black")),
                        ],
                        color=Colors.WHITE if idx % 2 == 0 else Colors.GREY_100,
                    ) for idx, op in enumerate(stats.get("dernieres", []))
                ],
                border_radius=0,
                heading_row_height=50,
                heading_text_style=TextStyle(color=Colors.GREY_600,weight="bold", size=18),
                column_spacing=70,
                divider_thickness=0,
                data_row_max_height=40,
            )

            # Graphique d'évolution
            try:
                graph_content = graphique_evolution_view(page)
            except Exception as ex:
                print("Erreur graphique:", ex)
                graph_content = Text("Erreur lors du chargement du graphique.", color="red")

            return Column([
                Column([
                    Text("Tableau de bord", size=30, weight="bold", color="black"),
                    Text("Vue d'ensemble de votre situation financière",color=Colors.GREY, size=16),],
                    alignment=MainAxisAlignment.START, spacing=10),
                cards,
                graph_content,
                Container(
                    content=Column([
                        Text("Dernières transactions", size=22, color="black"),
                        tableau,], alignment=MainAxisAlignment.START,spacing=30),
                    bgcolor="white",
                    padding=30,
                    border_radius=10,
                    shadow=BoxShadow(blur_radius=10, color=Colors.GREY_300))
            ], spacing=20, expand=True, alignment=MainAxisAlignment.CENTER, scroll=ScrollMode.AUTO, horizontal_alignment=CrossAxisAlignment.STRETCH)
        return affichage_accueil(token)

    # Vue Transactions - Corrigée
    def get_transactions_view():
    # Crée les instances des vues
        transactions = transactions_view(page)
        operations = Operations(page)
        
        # Affiche la vue des transactions et le formulaire d'opération côte à côte
        return Column(
            [
                # Titre et sous-titre
                Column([
                    Text("Transactions", size=30, weight="bold", color="black"),
                    Text("Gérez vos dépenses et vos entrées", color=Colors.GREY, size=16)
                ], alignment=MainAxisAlignment.START, spacing=10),
                
                # Conteneur principal avec les deux vues côte à côte
                Row(
                    [
                        
                        # Formulaire d'opérations - Prend 30% de l'espace
                        Container(
                            content=operations,
                            width=page.width * 0.2,
                            padding=10,
                            border_radius=10,
                            bgcolor="white",
                            shadow=BoxShadow(blur_radius=2, color=Colors.GREY_300)
                        ),
                        # Transactions (tableau) - Prend 70% de l'espace avec scroll
                        Container(
                            content=Column([transactions], scroll=ScrollMode.AUTO),
                            expand=True,
                            width=page.width * 0.8,
                            padding=20,
                            border_radius=10,
                            bgcolor="white",
                            shadow=BoxShadow(blur_radius=2, color=Colors.GREY_300)
                        ),
                        
                    ],
                    spacing=20,  # Espace entre les éléments
                    vertical_alignment=CrossAxisAlignment.STRETCH,  # Alignement en haut
                    expand=True  # Prend toute la hauteur disponible
                )
            ],
            expand=True,  # Prend toute la hauteur disponible
            spacing=20  # Espace entre les éléments de la colonne
        )
    # Vue budget
    def get_budget_view():
        return Container(
            content=budget_resume_view(page),
            padding=Padding(20, 0, 0, 0),
            alignment=alignment.center
        )
    # vue de rapport
    def get_rapport_view():
        return Container(
            content=rapport_view(page),
            padding=Padding(20, 0, 0, 0),
            alignment=alignment.center
        )

    # Dictionnaire des vues
    view_generators = {
        0: get_accueil_view,
        1: get_transactions_view,
        2: get_budget_view,
        3: get_rapport_view,
    }

    # Gestion de la navigation
    def navigate(e, index=None):
        if index is not None:
            page.agent_selected_index = index
        else:
            page.agent_selected_index = e.control.selected_index
        content_container.content = view_generators.get(page.agent_selected_index, get_accueil_view)()
        page.update()

    # Barre de navigation
    def build_appbar():
        return Container(
            content=Row(
                controls=[
                    Icon(Icons.WALLET, color="white", size=30),
                    Container(width=200),
                    Row([
                        TextButton("Tableau de bord", on_click=lambda e: navigate(e, 0), style=ButtonStyle(color="white")),
                        TextButton("Transactions", on_click=lambda e: navigate(e, 1), style=ButtonStyle(color="white")),
                        TextButton("Budgétisation", on_click=lambda e: navigate(e, 2), style=ButtonStyle(color="white")),
                        TextButton("rapport",on_click=lambda e: navigate(e, 3) ,style=ButtonStyle(color="white")),
                        Container(width=400),
                        ElevatedButton(
                            "Déconnexion",
                            icon=Icons.LOGOUT,
                            on_click=lambda e: page.go("/login_page"),bgcolor="white", color=Colors.INDIGO_600,style=ButtonStyle(shape=RoundedRectangleBorder(radius=0)))
                    ], spacing=40)
                ],
                alignment=MainAxisAlignment.START
            ),
            bgcolor=Colors.INDIGO_600,
            padding=padding.symmetric(horizontal=20, vertical=15),
            height=60
        )

    # Conteneur principal
    content_container = Container(
        content=view_generators[page.agent_selected_index](),
        expand=True,
        bgcolor="#f1f1f1",
        padding=Padding(180, 20, 180, 20),
        alignment=alignment.top_center,
    )

    # Structure finale
    return View(
        "/agent-dashboard",
        controls=[
            Column([
                build_appbar(),
                content_container
            ], expand=True, alignment=MainAxisAlignment.START,
                spacing=0, run_spacing=0, horizontal_alignment=CrossAxisAlignment.STRETCH),
        ]
    )