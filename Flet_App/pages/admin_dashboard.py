from flet import *
from database.operations import Operations  
from database.api import *
from components.stats_card import stat_card
from database.budget import *
from database.transactions import *
from database.pdf import *
from components.charts import *
import webbrowser
from datetime import datetime

def admindashboard(page: Page):
    # Configuration de base
    page.bgcolor = Colors.GREY_100
    token = page.session.get("token")
    role = page.session.get("role")
    
    # Debug: Afficher le rôle dans la console
    print(f"Rôle utilisateur: {role}")
    
    if not token or role != "ADMIN":
        page.go("/")
        return

    # Initialisation de l'index du menu
    if not hasattr(page, "admin_selected_index"):
        page.admin_selected_index = 0

    # --- Vue Accueil Admin ---
    def get_accueil_view():
        stats = get_global_stats(token)
        if not stats:
            return Column([
                Text("Tableau de bord Admin", size=24, weight="bold"),
                Text("⚠️ Impossible de charger les données", color="red", size=18),
                Text("Veuillez vérifier votre connexion et vos permissions", color="red")
            ])
        
        # Cartes de statistiques
        cards =Row([
            stat_card("Total Entrées", f"{stats.get('total_entrees',0):,.0f} $", 
                     icon=Icons.ARROW_CIRCLE_UP_ROUNDED, color=Colors.GREEN_600),
            stat_card("Total Dépenses", f"{stats.get('total_depenses',0):,.0f} $", 
                        icon=Icons.ARROW_CIRCLE_DOWN_ROUNDED, color=Colors.RED_600),
            stat_card("Nb Entrées", stats.get('count_entrees',0), 
                     icon=Icons.ADD_CHART, color=Colors.BLACK),
            stat_card("Nb Dépenses", stats.get('count_depenses',0), 
                     icon=Icons.REMOVE_CIRCLE, color=Colors.BLACK)
        ], width=page.width, wrap=True, spacing=10, alignment=MainAxisAlignment.SPACE_BETWEEN)

        # Tableau des dernières opérations
        table = DataTable(
            columns=[
                DataColumn(Text("Agent")),
                DataColumn(Text("Date")),
                DataColumn(Text("Type")),
                DataColumn(Text("Montant"), numeric=True),
                DataColumn(Text("Description"))
            ],
            rows=[
                DataRow(cells=[
                    DataCell(Text(op.get('agent_name', 'N/A'),color="black")),
                    DataCell(Text(op.get('date', ''),color="black")),
                    DataCell(Text(op.get('type', ''), 
                               color=Colors.GREEN if op.get('type') == "ENTREE" else Colors.RED)),
                    DataCell(Text(f"{op.get('montant',0):,.0f} $",color="black")),
                    DataCell(Text(op.get('description', '-'),color="black"))
                ]) for op in stats.get('dernieres_operations', [])
            ],
            border_radius=0,
            heading_row_height=50,
            heading_text_style=TextStyle(color=Colors.GREY_600,weight="bold", size=18),
            column_spacing=70,
            divider_thickness=0,
            data_row_max_height=40,
        )

        return Column([
            Column([
                    Text("Tableau de bord", size=30, weight="bold", color="black"),
                    Text("Vue d'ensemble de votre situation financière",color=Colors.GREY, size=16),],
                    alignment=MainAxisAlignment.START, spacing=10),
            cards,
            # Nouveau graphique global
            graphique_global_view(page),
            Container(
                    content=Column([
                        Text("Dernières transactions", size=22, color="black"),
                        table,], alignment=MainAxisAlignment.START,spacing=30),
                    bgcolor="white",
                    padding=30,
                    border_radius=10,
                    shadow=BoxShadow(blur_radius=10, color=Colors.GREY_300))
        ], spacing=20, expand=True, alignment=MainAxisAlignment.CENTER, scroll=ScrollMode.AUTO, horizontal_alignment=CrossAxisAlignment.STRETCH)

    # --- Vue Transactions Admin ---
    def get_transactions_view():
    # 1. Déclaration des contrôles avec valeurs par défaut
        search = TextField(
            label="Recherche (ID, description, agent...)",
            label_style=TextStyle(color="black"),
            expand=True,
            color="black",
            width=400,
            on_change=lambda e: load_data()
        )
        
        type_filter = Dropdown(
            label="Type",
            label_style=TextStyle(color="black"),
            options=[
                dropdown.Option("", "Tous"),
                dropdown.Option("DEPENSE", "Dépense"),
                dropdown.Option("ENTREE", "Entrée")
            ],
            value="",  # Valeur par défaut
            width=150,
            color="black",
            on_change=lambda e: load_data()
        )
        
        date_filter = TextField(
            label="Date (AAAA-MM ou AAAA-MM-JJ)",
            label_style=TextStyle(color="black"),
            color="black",
            width=200,
            on_change=lambda e: load_data()
        )

        # 2. Tableau avec largeur définie
        table = DataTable(
            columns=[
                DataColumn(Text("ID")),
                DataColumn(Text("Agent")),
                DataColumn(Text("Date")),
                DataColumn(Text("Type")),
                DataColumn(Text("Montant"), numeric=True),
                DataColumn(Text("Description"))
            ],
            rows=[],  # Rempli dynamiquement plus bas
            border_radius=0,  # Pas de bord arrondi
            heading_row_height=50,  # Hauteur de l'en-tête
            heading_text_style=TextStyle(color=Colors.GREY_600, weight="bold", size=18),
            column_spacing=70,  # Espacement entre colonnes
            divider_thickness=0,  # Pas de séparateur entre les lignes
        )

        # 3. Fonction de chargement améliorée avec debug
        def load_data():
            try:
                print("Chargement des données avec filtres...")
                filters = {
                    "search": search.value,
                    "type": type_filter.value if type_filter.value else None,
                    "date": date_filter.value if date_filter.value else None
                }
                print("Filtres appliqués:", filters)
                
                transactions = get_global_transactions(token, filters)
                print("Données reçues:", len(transactions), "transactions")
                
                if transactions:
                    table.rows = [
                        DataRow(
                            cells=[
                                DataCell(Text(str(t.get('id', 'N/A')), color="black")),
                                DataCell(Text(t.get('agent_name', 'N/A'), color="black")),
                                DataCell(Text(t.get('date', 'N/A'), color="black")),
                                DataCell(Text(
                                    "Entrée" if t.get('type') == "ENTREE" else "Dépense",
                                    color=Colors.GREEN if t.get('type') == "ENTREE" else Colors.RED
                                )),
                                DataCell(Text(f"{float(t.get('montant', 0)):,.2f} $", color="black")),
                                DataCell(Text(t.get('description', 'Aucune description'), color="black"))  # Toujours 6 cellules
                            ]
                        ) for t in transactions
                    ]
                else:
                    table.rows= [DataRow(
                        cells=[
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(
                                Text(
                                    "Aucune transaction trouvée",
                                    size=14,
                                    weight=FontWeight.BOLD,
                                    color=Colors.GREY_600,
                                    text_align=TextAlign.CENTER
                                )
                            )
                        ]
                    )]

                page.update()
                print("Tableau mis à jour")
                
            except Exception as e:
                print(f"ERREUR dans load_data: {str(e)}")
                table.rows =[ DataRow(
                        cells=[
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(Text("", size=12, color=Colors.GREY_600)),
                            DataCell(
                                Text(
                                    "Aucune transaction trouvée",
                                    size=14,
                                    weight=FontWeight.BOLD,
                                    color=Colors.GREY_600,
                                    text_align=TextAlign.CENTER
                                )
                            )
                        ]
                    )]  
                page.update()

        # 4. Chargement initial
        def initialize():
            try:
                print("Initialisation...")
                # Chargement des agents
                agents = get_all_agents(token)
                print(f"Agents reçus: {len(agents)}")
                # Premier chargement des données
                load_data()
                
            except Exception as e:
                print(f"ERREUR d'initialisation: {str(e)}")
                table.rows = [
                    DataRow(
                        cells=[DataCell(Text(f"Erreur d'initialisation: {str(e)}", col=6, color=Colors.RED))]
                    )
                ]
                page.update()

        # Lance l'initialisation
        initialize()

        # 5. Interface organisée
        return Column(
            controls=[
                # En-tête
                Column([
                    Text("Transactions", size=30, weight="bold", color="black"),
                    Text("Visualisez vos dépenses et vos entrées", color=Colors.GREY, size=16)
                ], alignment=MainAxisAlignment.START, spacing=10),
                
                # Section tableau
                Container(
                    content=Column([
                        Row([Text("Historique des transactions", size=25, color="black"),
                             Row([  search,type_filter,date_filter]),
                             ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                        
                        table,],
                        alignment=MainAxisAlignment.START,
                        horizontal_alignment=CrossAxisAlignment.STRETCH,
                        scroll=ScrollMode.AUTO, 
                        spacing= 30),
                    padding=20,
                    border_radius=10,
                    bgcolor=Colors.WHITE,
                    border=Border(right=BorderSide(2, Colors.BLACK), left=BorderSide(2, Colors.BLACK)),
                    expand=True
                ),],
            # Mise en page
            spacing=30,
            expand=True,
            horizontal_alignment=CrossAxisAlignment.STRETCH,
        )
    # --- Vue Budget Admin ---
    def get_budget_view():
        agent_select = Dropdown(
            label="Agent",
            color="black",
            label_style=TextStyle(color="black"),
            options=[dropdown.Option("", "Tous les agents")],
            width=200,
            on_change=lambda e: load_data()
        )
        
        mois_input = TextField(
            label="Mois (AAAA-MM)",
            color="black",
            label_style=TextStyle(color="black"),
            width=200,
            on_change=lambda e: load_data()
        )
        
        error_message = Text("", color=Colors.RED)
        budgets_container = Column(
            scroll=ScrollMode.AUTO,
            expand=True,
            spacing=10
        )

        def load_agents():
            try:
                agents = get_all_agents(token)
                agent_select.options = [dropdown.Option("", "Tous les agents")] + [
                    dropdown.Option(str(a['id']), a['name']) for a in agents
                ]
                page.update()
            except Exception as e:
                error_message.value = f"Erreur chargement agents: {str(e)}"
                page.update()

        def load_data():
            try:
                agent_id = agent_select.value if agent_select.value else None
                mois = mois_input.value if mois_input.value else None
                
                budgets = get_global_budgets(token, mois)
                budgets_container.controls = []  # Reset
                
                if not budgets:
                    budgets_container.controls.append(
                        Container(
                            content=Text("Aucun budget trouvé", color=Colors.GREY_600, size=16),
                            alignment=alignment.center,
                            padding=20
                        )
                    )
                    page.update()
                    return

                # Grouper par agent
                agents_data = {}
                for budget in budgets:
                    if agent_id and str(budget['agent_id']) != agent_id:
                        continue
                        
                    agent_key = f"{budget['agent_id']}_{budget['agent_name']}"
                    if agent_key not in agents_data:
                        agents_data[agent_key] = {
                            'name': budget['agent_name'],
                            'budgets': []
                        }
                    agents_data[agent_key]['budgets'].append(budget)

                # Créer l'UI
                for agent_key, agent_data in agents_data.items():
                    # En-tête agent
                    budgets_container.controls.append(
                        Container(
                            content=Text(agent_data['name'], size=18, weight="bold", color="white"),
                            padding=10,
                            bgcolor=Colors.BLUE_GREY_800,
                            border_radius=5
                        )
                    )

                    # Cartes budget
                    for budget in sorted(agent_data['budgets'], key=lambda x: x['mois'], reverse=True):
                        try:
                            # Conversion sécurisée des nombres
                            montant = float(budget.get('budget', 0))
                            depenses = float(budget.get('depenses', 0))
                            progression = (depenses / montant) if montant else 0

                            budgets_container.controls.append(
                                Container(
                                    content=Column([
                                        Row([
                                            Text(budget['mois'], weight="bold", size=16, color="black"),
                                            Row([
                                                Text(f"Budget: {montant:,.0f} $", color="black"),
                                                Text(f"Dépenses: {depenses:,.0f} $", 
                                                    color=Colors.RED_600 if depenses > montant else Colors.BLACK),
                                                Text(f"Solde: {montant - depenses:,.0f} $", color=Colors.GREEN_600),
                                            ], spacing=20)
                                        ], spacing=20, alignment=MainAxisAlignment.SPACE_BETWEEN),
                                        ProgressBar(
                                            value=progression,
                                            color=Colors.RED_600 if progression > 0.9 else 
                                                Colors.ORANGE if progression > 0.7 else 
                                                Colors.GREEN_600,
                                            height=10
                                        )
                                    ], spacing=10),
                                    padding=20,
                                    border=border.all(1, Colors.GREY_400),
                                    border_radius=5,
                                    margin=margin.only(bottom=10),
                                    bgcolor=Colors.WHITE
                                )
                            )
                        except Exception as e:
                            budgets_container.controls.append(
                                Text(f"Erreur format budget: {str(e)}", color=Colors.RED)
                            )

                page.update()
                
            except Exception as e:
                error_message.value = f"Erreur: {str(e)}"
                page.update()

        load_agents()
        load_data()  # Chargement initial

        return Container(
            content=Column([
                Column([
                    Text("Budgets des agents", size=24, weight="bold", color="black"),
                    Text("Visualisation des budgets mensuels", size=16, color=Colors.GREY_600),
                ], spacing=10),
                
                Row([
                    Text("Filtrer par agent et mois:", size=16, color="black"),
                    agent_select,
                    mois_input
                ], spacing=20),
                
                error_message,
                
                Container(
                    content=budgets_container,
                    expand=True,
                    padding=10,
                    border_radius=10,
                    bgcolor=Colors.GREY_100
                )
            ], spacing=20, expand=True),
            expand=True,
            padding=20
        )

    # --- Vue Rapports Admin ---
    def get_rapport_view():
        mois_input = TextField(
            label="Mois (AAAA-MM)", 
            width=200,
            color="black",
            label_style=TextStyle(color="black")
        )
        
        agent_select = Dropdown(
            label="Agent",
            width=200,
            color="black",
            label_style=TextStyle(color="black")
        )
        
        message = Text("", color=Colors.RED_600)
        
        def load_agents():
            try:
                agents = get_all_agents(token)
                agent_select.options = [dropdown.Option("", "Tous les agents")] + [
                    dropdown.Option(str(a['id']), a['name']) for a in agents
                ]
                page.update()
            except Exception as e:
                message.value = f"Erreur chargement agents: {str(e)}"
                message.color = Colors.RED_600
                page.update()
        
        def generer_rapport(e):
            if not mois_input.value:
                message.value = "Veuillez spécifier un mois"
                message.color = Colors.RED_600
                page.update()
                return
            
            mois = mois_input.value
            agent_id = agent_select.value if agent_select.value else None
            
            try:
                filepath = download_summary_pdf(token, mois, agent_id)
                if filepath:
                    message.value = f"Rapport généré avec succès: {filepath}"
                    message.color = Colors.GREEN_600
                else:
                    message.value = "Erreur lors de la génération du rapport"
                    message.color = Colors.RED_600
            except Exception as e:
                message.value = f"Erreur: {str(e)}"
                message.color = Colors.RED_600
            
            page.update()
        
        load_agents()
        
        return Column([
            Text("Génération de rapports", size=20, weight="bold", color="black"),
            Row([
                mois_input,
                agent_select
            ], spacing=20),
            ElevatedButton(
                "Générer PDF",
                on_click=generer_rapport,
                icon=Icons.PICTURE_AS_PDF,
                style=ButtonStyle(
                    bgcolor=Colors.BLUE_700,
                    padding={"left": 20, "right": 20, "top": 15, "bottom": 15}
                )
            ),
            message
        ], spacing=20)
    # --- Vue Management ---
    def get_management_view():
        def open_admin(e):
            webbrowser.open("http://localhost:8000/admin")
        
        return Column([
            Text("Administration complète", size=20, weight="bold"),
            ElevatedButton(
                "Ouvrir l'interface Django Admin",
                icon=Icons.OPEN_IN_NEW,
                on_click=open_admin,
                style=ButtonStyle(
                    padding={"left": 20, "right": 20, "top": 15, "bottom": 15},
                    bgcolor=Colors.BLUE_700
                )
            )
        ], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER)

    # --- Navigation ---
    views = {
        0: get_accueil_view,
        1: get_transactions_view,
        2: get_budget_view,
        3: get_rapport_view,
        4: get_management_view
    }
    # Fonction de navigation
    def navigate(e):
        page.admin_selected_index = e.control.selected_index
        content.content = views[page.admin_selected_index]()
        page.update()
        
    # Navigation Rail
    rail = NavigationRail(
        selected_index=page.admin_selected_index,
        on_change=navigate,
        destinations=[
            NavigationRailDestination(icon=Icons.DASHBOARD, label="Accueil"),
            NavigationRailDestination(icon=Icons.LIST_ALT, label="Transactions"),
            NavigationRailDestination(icon=Icons.ACCOUNT_BALANCE, label="Budgets"),
            NavigationRailDestination(icon=Icons.PICTURE_AS_PDF, label="Rapports"),
            NavigationRailDestination(icon=Icons.ADMIN_PANEL_SETTINGS, label="Management")
        ],
        label_type=NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        elevation=10,
        group_alignment=-0.9
    )

    content = Container(
        content=views[page.admin_selected_index](),
        expand=True,
        bgcolor="#f1f1f1",
        padding=Padding(90, 20, 90, 20),
        alignment=alignment.top_center,
    )

    return View(
        "/admin-dashboard",
        controls=[
            Row([
                rail,
                VerticalDivider(width=1),
                content
            ], expand=True)
        ]
    )