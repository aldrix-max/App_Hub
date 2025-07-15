import flet as ft
from flet import *
from database.api import get_budget_resume, ajouter_budget_mensuel
from datetime import datetime

def budget_resume_view(page: Page):
    # Récupère le token utilisateur et le mois courant (format YYYY-MM)
    token = page.session.get("token")
    mois = datetime.now().strftime("%Y-%m")

    # Appel API pour obtenir le résumé du budget du mois courant
    resume = get_budget_resume(token, mois) or {}

    # Extraction des données du résumé
    montant_total = resume.get("montant_total", 0)
    depenses_totales = resume.get("depenses_totales", 0)
    solde = resume.get("solde", 0)
    categories = resume.get("categories", [])

    # Calcul de la progression globale du budget (pour la ProgressBar)
    progress = depenses_totales / montant_total if montant_total else 0

    # --- Formulaire pour définir le budget mensuel ---
    montant_input = TextField(
        label="Définir le budget mensuel ($)",
        width=200,
        border_color=Colors.INDIGO_600,
        color=Colors.BLACK,
        value=str(montant_total) if montant_total else "",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    message = Text("", color=Colors.BLACK)

    # Fonction appelée lors du clic sur "Sauvegarder"
    def definir_budget(e):
        val = montant_input.value.strip()
        # Vérifie que la valeur saisie est un nombre valide
        if not val or not val.replace('.', '', 1).isdigit():
            message.value = "Veuillez entrer un montant valide."
        else:
            # Appel API pour ajouter ou mettre à jour le budget mensuel
            resp = ajouter_budget_mensuel(token, mois, val)
            if resp and resp.status_code in (200, 201):
                message.value = "Budget mis à jour !"
                page.go(page.route)  # Recharge la page pour voir la mise à jour
            else:
                message.value = "Erreur lors de la sauvegarde."
        page.update()

    # --- Alerte si le budget est atteint ou dépassé ---
    alerte = None
    if montant_total and depenses_totales >= montant_total:
        alerte = Text(
            "⚠️ Attention : Budget mensuel atteint ou dépassé !",
            color=Colors.RED_700,
            weight="bold"
        )

    # Construction de la vue principale
    return Column(
        controls=[
            # Titre principal et sous-titre
            Column([
                Text("Résumé du Budget Mensuel", 
                     size=24, 
                     weight="bold",
                     color="black"),
                Text("Gérer vos finances avec efficacité", 
                     size=16, 
                     color="black"),
            ]),
            
            # Ligne contenant les deux containers principaux
            Row([
                # Premier container : résumé et formulaire du budget global (40%)
                Container(
                    content=Column([
                        Text("Votre budget mensuel", size=22, color="black"),
                        # Formulaire de définition du budget
                        Row([
                            montant_input,
                            ElevatedButton("Sauvegarder", on_click=definir_budget,
                                           bgcolor=Colors.INDIGO_600, color="white",
                                           width=120, style=ButtonStyle(shape=RoundedRectangleBorder(radius=0)))
                        ], spacing=10),
                        message,
                        Divider(height=10),
                        # Affichage des totaux
                        Row([
                            Text("Total budgétisé", size=16, color="black"),
                            Text(f"€{montant_total:.2f}", weight="bold", color="black")
                        ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                        Row([
                            Text("Dépenses effectuées", size=16, color="black"),
                            Text(f"€{depenses_totales:.2f}", weight="bold", color=Colors.RED_600)
                        ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                        Row([
                            Text("Solde restant", size=16, color="black"),
                            Text(f"€{solde:.2f}", weight="bold", color=Colors.GREEN_600)
                        ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                        # Barre de progression du budget global
                        ProgressBar(value=progress, width=300,color=Colors.RED_600 if progress > 0.9 else 
                                                Colors.ORANGE if progress > 0.7 else 
                                                Colors.GREEN_600, height=5, bgcolor=Colors.INDIGO_600),
                        # Affiche l'alerte si besoin
                        alerte if alerte else Container(),
                    ],
                        alignment=MainAxisAlignment.START,
                        spacing=20,
                        horizontal_alignment=CrossAxisAlignment.STRETCH,
                    ),
                    padding=20,
                    bgcolor=Colors.WHITE,
                    border_radius=10,
                    width=page.width * 0.3 if page.width else None,  # 40% de la largeur
                ),
                # Deuxième container : tableau des catégories (60%)
                Container(
                    content=Column([
                        Text("Budgets par catégorie", size=22, color="black"),
                        DataTable(
                            columns=[
                                DataColumn(label=Text("CATÉGORIE")),
                                DataColumn(label=Text("DÉPENSES")),
                                DataColumn(label=Text("POURCENTAGE")),
                            ],
                            rows=[
                                DataRow(cells=[
                                    DataCell(Text(cat["nom"], color="black")),
                                    DataCell(Text(f"€{cat['montant']:.2f}", color="black")),
                                    DataCell(Text(f"{cat['pourcentage']:.1f}%", color="black")),
                                ]) for cat in categories
                            ],
                            border_radius=0,
                            heading_row_height=50,
                            heading_text_style=ft.TextStyle(color=ft.Colors.GREY_600, weight="bold", size=18),
                            column_spacing=70,
                            divider_thickness=0,
                        )
                    ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=30,
                        scroll=ScrollMode.AUTO,
                    ),
                    padding=20,
                    border_radius=10,
                    bgcolor=Colors.WHITE,
                    expand=True,  # Occupe le reste de l'espace (60%)
                )
            ],
                alignment=MainAxisAlignment.START,
                vertical_alignment=CrossAxisAlignment.STRETCH,
                spacing=20,
                expand=True
            )
        ],
        alignment=MainAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )