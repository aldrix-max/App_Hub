import flet as ft
from database.api import get_transactions, get_categories
from database.depenses_view import *
from database.entrees_view import *

def transactions_view(page: ft.Page):
    """
    Vue principale pour afficher l'historique des transactions
    avec possibilité de basculer entre toutes les transactions,
    les dépenses uniquement ou les entrées uniquement.
    """
    
    # Récupération du token de session pour l'authentification
    token = page.session.get("token")
    if not token:
        # Si pas de token, redirection vers la page d'accueil
        page.go("/")
        return

    # --- Fonction pour afficher la vue principale ---
    def show_main_view(e=None):
        """
        Réinitialise et affiche la vue principale avec :
        - Le titre et les boutons de navigation
        - Le tableau des transactions
        """
        main_cont.controls.clear()  # Vide le conteneur
        # Reconstruction de l'interface
        main_cont.controls.extend([
            ft.Row([
                ft.Text("Historique des transactions", size=22, weight="bold", color="black"),
                ft.Container(width=150),  # Espacement entre le titre et les boutons
                # Bouton pour voir les dépenses (rouge)
                ft.ElevatedButton(
                    "Voir dépenses", 
                    bgcolor=ft.Colors.RED_100, 
                    color="white", 
                    on_click=depenses,
                    width=150,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)))  # Style sans bord arrondi
                ,
                # Bouton pour voir les entrées (vert)
                ft.ElevatedButton(
                    "Voir entrées", 
                    bgcolor=ft.Colors.GREEN_100, 
                    color="white", 
                    on_click=entrees,
                    width=150,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)))
            ]),
            table  # Ajout du tableau des transactions
        ])
        page.update()  # Mise à jour de l'interface

    # --- Configuration du tableau des transactions ---
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("DATE")),
            ft.DataColumn(ft.Text("TYPE")),
            ft.DataColumn(ft.Text("MONTANT"), numeric=True),  # Colonne numérique alignée à droite
            ft.DataColumn(ft.Text("DESCRIPTION")),
        ],
        rows=[],  # Rempli dynamiquement plus bas
        border_radius=0,  # Pas de bord arrondi
        heading_row_height=50,  # Hauteur de l'en-tête
        heading_text_style=ft.TextStyle(color=ft.Colors.GREY_600, weight="bold", size=18),
        column_spacing=70,  # Espacement entre colonnes
        divider_thickness=0,  # Pas de séparateur entre les lignes
    )

    # Message d'information (nombre de transactions)
    message = ft.Text("", color=ft.Colors.GREY_600)

    # --- Chargement des données initiales ---
    data = get_transactions(token)  # Récupère les transactions depuis l'API
    if not data:
        message.value = "Aucune transaction trouvée"
    else:
        message.value = f"{len(data)} transactions trouvées"
        # Remplissage du tableau avec les données
        for tr in data:
            # Choix de la couleur selon le type (rouge pour dépense, vert pour entrée)
            amount_color = ft.Colors.RED_600 if tr.get("type") == "DEPENSE" else ft.Colors.GREEN_600
            table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(tr.get("date", ""), color="black")),
                    ft.DataCell(ft.Text(tr.get("type", ""), color="black")),
                    ft.DataCell(ft.Text(f"{tr.get('montant', 0)} $", color=amount_color)),
                    ft.DataCell(ft.Text(tr.get("description", "-"), color="black")),
                ]))
    page.update()

    # --- Initialisation des vues spécialisées ---
    # Création des vues pour les dépenses et entrées (passage de la fonction de retour)
    depenses_cont = depenses_view(page, show_main_view)  # Vue des dépenses
    entrees_cont = entree_view(page, show_main_view)    # Vue des entrées

    # --- Fonctions de navigation ---
    def depenses(e):
        """Affiche uniquement les dépenses"""
        main_cont.controls.clear()
        main_cont.controls.append(depenses_cont)  # Ajoute la vue des dépenses
        page.update()
        
    def entrees(e):
        """Affiche uniquement les entrées"""
        main_cont.controls.clear()
        main_cont.controls.append(entrees_cont)  # Ajoute la vue des entrées
        page.update()

    # --- Conteneur principal ---
    main_cont = ft.Column(
        controls=[
            # Ligne avec titre et boutons
            ft.Row([
                ft.Text("Historique des transactions", size=22, weight="bold", color="black"),
                ft.Container(width=150),  # Espacement
                ft.ElevatedButton("Voir dépenses", bgcolor=ft.Colors.RED_100, color="white", on_click=depenses,
                                   width=150, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0))),
                ft.ElevatedButton("Voir entrées", bgcolor=ft.Colors.GREEN_100, color="white", on_click=entrees,
                                   width=150, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=0)))
            ]),
            table  # Tableau des transactions
        ],
        scroll=ft.ScrollMode.AUTO,  # Défilement automatique si contenu trop long
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # Étirement horizontal
        expand=True,  # Prend tout l'espace disponible
        spacing=20  # Espacement entre éléments
    )
    
    return main_cont  # Retourne l'interface complète