import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from management.models import Categorie

def creer_categories_incubateur():
    # Catégories de dépenses
    categories_depenses = [
        {"nom": "Loyer des locaux", "type": "DEPENSE"},
        {"nom": "Services publics (électricité, eau, internet)", "type": "DEPENSE"},
        {"nom": "Salaires du personnel", "type": "DEPENSE"},
        {"nom": "Matériel informatique", "type": "DEPENSE"},
        {"nom": "Logiciels et abonnements", "type": "DEPENSE"},
        {"nom": "Marketing et communication", "type": "DEPENSE"},
        {"nom": "Événements et ateliers", "type": "DEPENSE"},
        {"nom": "Frais juridiques et comptables", "type": "DEPENSE"},
        {"nom": "Assurances", "type": "DEPENSE"},
        {"nom": "Frais de déplacement", "type": "DEPENSE"},
        {"nom": "Fournitures de bureau", "type": "DEPENSE"},
        {"nom": "Maintenance et réparations", "type": "DEPENSE"},
        {"nom": "Frais bancaires", "type": "DEPENSE"},
        {"nom": "Divers", "type": "DEPENSE"},
    ]

    # Catégories de recettes
    categories_recettes = [
        {"nom": "Cotisations des startups", "type": "ENTREE"},
        {"nom": "Subventions publiques", "type": "ENTREE"},
        {"nom": "Sponsoring et partenariats", "type": "ENTREE"},
        {"nom": "Vente de services", "type": "ENTREE"},
        {"nom": "Dons", "type": "ENTREE"},
        {"nom": "Revenue des événements", "type": "ENTREE"},
        {"nom": "Investissements externes", "type": "ENTREE"},
        {"nom": "Autres revenus", "type": "ENTREE"},
    ]

    # Création des catégories
    for cat_data in categories_depenses + categories_recettes:
        categorie, created = Categorie.objects.get_or_create(
            nom=cat_data["nom"],
            defaults={"type": cat_data["type"]}
        )
        if created:
            print(f"Catégorie créée: {categorie}")
        else:
            print(f"Catégorie existante: {categorie}")

if __name__ == "__main__":
    print("Début de la création des catégories pour l'incubateur...")
    creer_categories_incubateur()
    print("Opération terminée.")