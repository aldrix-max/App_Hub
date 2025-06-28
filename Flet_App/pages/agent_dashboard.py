from flet import *
from database.operations import Operations  
from database.api import *
from components.stats_card import stat_card
from database.depenses_view import depenses_view
from database.entrees_view import entree_view


# ==============================================
# DASHBOARD AGENT
# ==============================================
def agentdashboard(page: Page):
    token = page.session.get("token")
    if not token:
        page.go("/")
        return
    # Définition des vues pour chaque section
    def get_accueil_view():
        def affichage_accueil(token):
            stats = get_stats(token)
            print("DEBUG stats:", stats)
            if not stats:
                return Text("❌ Impossible de charger les statistiques.", color="red")

            cards = Row([
                stat_card("💰 Entrees", f"{stats['resume'].get('total_entrees',0)} FC", color="green", icon=Icons.TRENDING_UP),
                stat_card("💸 Dépenses", f"{stats['resume'].get('total_depenses',0)} FC", color="red", icon=Icons.TRENDING_DOWN),
                stat_card("Nb Entrees", stats['resume'].get('entrees',0), color="teal", icon=Icons.ADD_CHART),
                stat_card("Nb Dépenses", stats['resume'].get('depenses',0), color="orange", icon=Icons.REMOVE_CIRCLE)
            ],width=page.width, wrap=True, spacing=10,alignment=MainAxisAlignment.SPACE_BETWEEN)

            tableau = DataTable(
                columns=[
                    DataColumn(Text("Date")),
                    DataColumn(Text("Type")),
                    DataColumn(Text("Catégorie")),
                    DataColumn(Text("Montant")),
                    DataColumn(Text("Description")),
                    
                ],
                rows=[
                    DataRow(cells=[
                        DataCell(Text(op["date"])),
                        DataCell(Text(op["type"])),
                        DataCell(Text(op["categorie_nom"])),
                        DataCell(Text(f"{op['montant']} FC")),
                        DataCell(Text(op['description'])),
                    ]) for op in stats.get("dernieres")
                ]
            )

            return Column([
                Text("📊 Statistiques personnelles", size=22, weight="bold"),
                cards,
                Divider(),
                Text("📋 Dernières opérations enregistrées", size=22),
                tableau
            ], spacing=20,
                alignment=MainAxisAlignment.START,
             )
        return affichage_accueil(token)
        

    def get_depenses_view():
            return Container(
                content=Row([depenses_view(page),Operations(page)],
                            vertical_alignment=CrossAxisAlignment.STRETCH,),
                padding=Padding(20,0,0,0),
                alignment=alignment.center
            )
    def get_recettes_view():
            return Container(
                content=Row([entree_view(page),Operations(page)],
                            vertical_alignment=CrossAxisAlignment.STRETCH),
                padding=Padding(20,0,0,0),
                alignment=alignment.center
            )

    view_generators = {
        0: get_accueil_view,
        1: get_depenses_view,
        2: get_recettes_view,

    }
    def navigate(e):
        selected_index = e.control.selected_index
        content_container.content = view_generators.get(selected_index, get_accueil_view)()
        page.update()
        
    def build_sidebar():
        return Container(
            width=250,
            bgcolor=Colors.BLUE_GREY_900,
            padding=padding.symmetric(vertical=20, horizontal=10),
            content=Column(
                [
                    Row([Image(src="assets/logo.png", width=140, height=60, fit=ImageFit.CONTAIN)], alignment=MainAxisAlignment.CENTER),
                    Divider(color=Colors.WHITE24, height=30),
                    NavigationRail(
                        selected_index=0,
                        height=300,
                        on_change=navigate,
                        extended=True,
                        bgcolor= Colors.BLUE_GREY_900,
                        label_type=NavigationRailLabelType.ALL,
                        indicator_color="Blue",
                        indicator_shape=StadiumBorder(),
                        destinations=[
                            NavigationRailDestination(icon=Icon(Icons.DASHBOARD, color="white"), selected_icon=Icons.DASHBOARD, label_content=Text("Accueil", font_family="arial", size=16, color="white")),
                            NavigationRailDestination(icon=Icon(Icons.MONEY_OFF,color="white"), selected_icon=Icons.MONEY_OFF, label_content=Text("Dépenses", font_family="arial", size=16, color="white")),
                            NavigationRailDestination(icon=Icon(Icons.MONEY, color="white"), selected_icon=Icons.MONEY, label_content=Text("Entrée s", font_family="arial", size=16, color="white")),
                           
                        ],
                    ),
                    Container(expand=True),
                    Row(
                            [
                                Icon(Icons.LOGOUT, color=Colors.WHITE, ),
                                TextButton("Déconnexion", style=ButtonStyle(icon_color=Colors.WHITE, icon_size=15, text_style=TextStyle(size=15, color="white") ),on_click=lambda e: page.go("/login_page"),),
                            ],
                            alignment=MainAxisAlignment.END,
                            spacing=10
                        ),
                    
                        
                        ])
                    )
    
    content_container = Container(
        content=view_generators[0](),
        expand=True,
        padding=Padding(20,0,0,0),
        alignment=alignment.top_left,
    )
   

  

    return View(
        "/agent-dashboard",
        controls=[
            Row([
                build_sidebar(), content_container
            ], expand=True, alignment=MainAxisAlignment.START,
                spacing=0, run_spacing=0, vertical_alignment=CrossAxisAlignment.STRETCH),
                   
    ])