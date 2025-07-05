import flet as ft
from flet import *
from database.api import get_evolution_data
import matplotlib
matplotlib.use('Agg')  # Utilise le backend non interactif pour générer des images
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import traceback

def graphique_evolution_view(page: ft.Page):
    # Récupère le token de session pour l'utilisateur connecté
    token = page.session.get("token")
    if not token:
        # Si l'utilisateur n'est pas authentifié, affiche un message d'erreur
        return Text("Non authentifié", color="red")

    # --- Filtres pour le graphique ---
    # Dropdown pour choisir l'année
    annee_dropdown = Dropdown(
        label="Année",
        color="black",
        label_style=TextStyle(color="black", weight="bold", size=16),
        prefix_icon=Icon(Icons.DATE_RANGE, color=Colors.INDIGO_600),
        # Options pour les années 2025 à 2100
        options=[dropdown.Option(str(y)) for y in range(2025, 2100)],
        value="2025",
        width=200
    )
    # RadioGroup pour basculer entre Dépenses et Entrées
    type_radio = RadioGroup(
        content=Row([
            Radio(value="DEPENSE", label="Dépenses", label_style=TextStyle(color=Colors.GREY, size=16), active_color=Colors.INDIGO_600),
            Radio(value="ENTREE", label="Entrées", label_style=TextStyle(color=Colors.GREY, size=16), active_color=Colors.INDIGO_600),
        ]),
        value="DEPENSE"
    )

    # Container qui affichera le graphique ou un loader
    chart_container = Container(
        content=ProgressRing(),  # Loader circulaire pendant le chargement
        height=400,
        alignment=alignment.center
    )

    # Fonction qui génère et affiche le graphique selon les filtres
    def update_chart(e=None):
        try:
            annee = annee_dropdown.value
            type_op = type_radio.value
            # Appel API pour récupérer les données d'évolution
            data = get_evolution_data(token, type_op, annee) or {}

            # Préparation des données pour barres empilées
            months = sorted(data.keys())  # Liste des mois (ex: ['2025-01', '2025-02', ...])
            categories = set()
            for month in months:
                categories.update(data[month].keys())
            categories = sorted(categories)  # Liste des catégories (ex: ['Nourriture', 'Loyer', ...])

            # Pour chaque catégorie, liste des montants par mois
            values_per_cat = {cat: [data[month].get(cat, 0) for month in months] for cat in categories}

            # --- Génération du graphique matplotlib ---
            plt.style.use('ggplot')
            fig, ax = plt.subplots(figsize=(12, 6))
            bottom = [0] * len(months)  # Pour empiler les barres
            color_map = plt.cm.get_cmap('tab20', len(categories))  # Palette de couleurs

            bars = []
            for idx, cat in enumerate(categories):
                vals = values_per_cat[cat]
                # Trace la barre pour chaque catégorie, empilée sur les précédentes
                bar = ax.bar(
                    months, vals, bottom=bottom, label=cat,
                    color=color_map(idx)
                )
                # Affiche le montant sur chaque segment de barre
                ax.bar_label(
                    bar,
                    labels=[f"{v:.0f}" if v > 0 else "" for v in vals],
                    label_type="center",
                    fontsize=9,
                    color="black"
                )
                bars.append(bar)
                # Met à jour la base pour la prochaine catégorie (empilement)
                bottom = [b + v for b, v in zip(bottom, vals)]

            # Mise en forme du graphique
            ax.set_title(f"{'Dépenses' if type_op=='DEPENSE' else 'Entrées'} par Catégorie et Mois ({annee})")
            ax.set_xlabel("Mois")
            ax.set_ylabel("Montant")
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            # Convertit le graphique en image base64 pour l'afficher dans Flet
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png', bbox_inches='tight')
            plt.close()
            img_buf.seek(0)
            chart_base64 = base64.b64encode(img_buf.getvalue()).decode()
            chart_container.content = Image(
                src_base64=chart_base64,
                width=800,
                height=600,
                fit=ImageFit.CONTAIN
            )
            page.update()
        except Exception as e:
            # En cas d'erreur, affiche le message dans le container
            print("Erreur graphique:", e)
            print(traceback.format_exc())
            chart_container.content = Text(f"Erreur: {str(e)}", color="red")
            page.update()

    # Relie les filtres à la fonction de mise à jour du graphique
    annee_dropdown.on_change = update_chart
    type_radio.on_change = update_chart

    # Appel initial pour afficher le graphique dès l'ouverture de la page
    update_chart()

    # Barre de filtres en haut du graphique
    filtres_bar = Row([
        Text("Évolution Mensuelle des depenses et entrées", color= "black",size=22),
        Row([annee_dropdown, type_radio])
    ], spacing=30, alignment=MainAxisAlignment.SPACE_BETWEEN)

    # Structure finale de la page : filtres + graphique dans une carte
    return Container(
        content=Column([
            filtres_bar,
            chart_container], alignment=MainAxisAlignment.START,
                       horizontal_alignment=CrossAxisAlignment.STRETCH,
                       spacing=20),
            padding=30,
            bgcolor="white",
            border_radius= 10,
            shadow=BoxShadow(blur_radius=10, color=Colors.GREY_300)
        
            )
