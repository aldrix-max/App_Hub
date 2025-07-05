from django.db import models
from django.contrib.auth.models import User

# Modèle Agent : étend le modèle User de Django avec des champs supplémentaires
class Agent(models.Model):
    """
    Associe des informations supplémentaires à un utilisateur (User),
    comme son rôle ou son service.
    """
    # Définition des choix possibles pour le rôle
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('AGENT', 'Agent'),
        ('AUTRE', 'Autre'),
    ]

    # Relation un-à-un avec le modèle User de Django
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  # Si l'User est supprimé, l'Agent aussi
        verbose_name="Utilisateur", 
        default=""
    )
    
    # Champ pour stocker le rôle avec choix prédéfinis
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        verbose_name="Rôle de l'agent"
    )
    
    # Champ facultatif pour le service/département
    service = models.CharField(
        max_length=100, 
        blank=True,  # Peut être vide
        verbose_name="Service ou département"
    )

    def __str__(self):
        """Représentation lisible de l'objet (ex: dans l'admin)"""
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        """Métadonnées pour l'administration"""
        verbose_name = "Agent"  # Nom singulier dans l'admin
        verbose_name_plural = "Agents"  # Nom pluriel dans l'admin
        ordering = ['role', 'user']  # Tri par défaut

class Categorie(models.Model):
    """Catégorise les opérations financières (Dépenses/Entrées)"""
    
    # Types possibles de catégories
    TYPE_CHOICES = [
        ("DEPENSE", "Dépense"),
        ("ENTREE", "Entrée de fonds"),
    ]

    # Type de la catégorie (dépense ou entrée)
    type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default="DEPENSE"
    )
    
    # Nom de la catégorie
    nom = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return f"{self.nom} ({self.type})"

class Transaction(models.Model):
    """Enregistrement d'une opération financière"""
    
    # Type (dépense ou entrée)
    type = models.CharField(
        max_length=10, 
        choices=Categorie.TYPE_CHOICES
    )
    
    # Montant avec précision décimale
    montant = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    
    date = models.DateField()  # Date de la transaction
    description = models.TextField(blank=True)  # Champ optionnel
    
    # Lien vers la catégorie
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.CASCADE  # Si catégorie supprimée, transaction aussi
    )
    
    # Utilisateur associé
    utilisateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE  # Si user supprimé, transactions aussi
    )

    class Meta:
        ordering = ['-date']  # Tri par date décroissante
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.type} - {self.montant} FC - {self.date}"
#=====================================
# DEFINITION DU BUDGET
#=====================================
class BudgetMensuel(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    mois = models.CharField(max_length=7)  # "YYYY-MM"
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('utilisateur', 'mois')
        verbose_name = "Budget Mensuel"
        verbose_name_plural = "Budgets Mensuels"

    def __str__(self):
        return f"{self.utilisateur.username} - {self.mois} : {self.montant_total} FCFA"