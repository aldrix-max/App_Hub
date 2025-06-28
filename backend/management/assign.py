# management/populate_fake_operations.py

import random
from datetime import datetime, timedelta
from management.models import Categorie, Transaction
from django.contrib.auth import get_user_model
from management.models import Agent

User = get_user_model()

def run():
    agent = Agent.objects.filter(role="AGENT").first()
    if not agent:
        print("❌ Aucun agent valide trouvé.")
        return

    agent = agent.user

    depense_categories = Categorie.objects.filter(type="DEPENSE")
    entree_categories = Categorie.objects.filter(type="ENTREE")

    descriptions_depenses = [
        "Paiement loyer", "Fournitures bureau", "Facture eau", "Internet mensuel",
        "Sécurité bâtiments", "Assurance locaux", "Matériel informatique", "Mobilier neuf",
        "Papeterie", "Nettoyage", "Transport collaborateurs", "Publicité locale",
        "Consultant IT", "Formation staff", "Dépenses diverses"
    ]

    descriptions_entrees = [
        "Subvention publique", "Vente service", "Dons privés", "Paiement incubés",
        "Remboursement", "Financement projet", "Crowdfunding", "Revenus location",
        "Partenariat privé", "Revenus atelier", "Paiement coaching", "Sponsor tech",
        "Revenus événement", "Revente matériel", "Autres recettes"
    ]

    for i in range(15):
        # Dépense
        Transaction.objects.create(
            utilisateur=agent,
            categorie=random.choice(depense_categories),
            montant=random.randint(10000, 150000),
            date=datetime.now() - timedelta(days=random.randint(1, 60)),
            description=descriptions_depenses[i]
        )

        # Entrée
        Transaction.objects.create(
            utilisateur=agent,
            categorie=random.choice(entree_categories),
            montant=random.randint(50000, 300000),
            date=datetime.now() - timedelta(days=random.randint(1, 60)),
            description=descriptions_entrees[i]
        )

    print("✅ 15 opérations de dépense et 15 opérations d'entrée ont été ajoutées avec succès.")
