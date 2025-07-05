import flet as ft
from flet import *
from database.api import get_budget_resume
from datetime import datetime

def budget_resume_view(page: Page):
    token = page.session.get("token")
    mois = datetime.now().strftime("%Y-%m")
    resume = get_budget_resume(token, mois) or {}

    montant_total = resume.get("montant_total", 0)
    depenses_totales = resume.get("depenses_totales", 0)
    solde = resume.get("solde", 0)
    categories = resume.get("categories", [])

    # ProgressBar globale
    progress = depenses_totales / montant_total if montant_total else 0

    return Container(
        content=Column([
            Text("Votre budget mensuel", size=22, weight="bold"),
            Row([
                Text("Total budgétisé"),
                Text(f"€{montant_total:.2f}", weight="bold")
            ], alignment=MainAxisAlignment.SPACE_BETWEEN),
            Row([
                Text("Dépenses effectuées"),
                Text(f"€{depenses_totales:.2f}", weight="bold", color=Colors.RED_600)
            ], alignment=MainAxisAlignment.SPACE_BETWEEN),
            Row([
                Text("Solde restant"),
                Text(f"€{solde:.2f}", weight="bold", color=Colors.GREEN_600)
            ], alignment=MainAxisAlignment.SPACE_BETWEEN),
            ProgressBar(value=progress, width=300, color=Colors.INDIGO_600),
            Divider(),
            Text("Budgets par catégorie", size=18, weight="bold"),
            DataTable(
                columns=[
                    DataColumn(label=Text("Catégorie")),
                    DataColumn(label=Text("Dépenses")),
                    DataColumn(label=Text("Pourcentage")),
                    DataColumn(label=Text("Progression")),
                ],
                rows=[
                    DataRow(cells=[
                        DataCell(Text(cat["nom"])),
                        DataCell(Text(f"€{cat['montant']:.2f}")),
                        DataCell(Text(f"{cat['pourcentage']:.1f}%")),
                        DataCell(
                            ProgressBar(
                                value=cat["pourcentage"] / 100 if montant_total else 0,
                                width=120,
                                color=Colors.BLUE_400
                            )
                        ),
                    ]) for cat in categories
                ]
            )
        ], spacing=12),
        padding=20,
        bgcolor="white",
        border_radius=10,
        width=400
    )