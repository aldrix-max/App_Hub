from django.db import models
from django.contrib.auth.models import User

class Agent(models.Model):
    """
    Étend le modèle User de Django pour ajouter des champs spécifiques aux agents :
    - Rôle (admin, agent, etc.)
    - Service/département
    """
    ROLE_CHOICES = [  # Liste des rôles possibles
        ('ADMIN', 'Administrateur'),
        ('AGENT', 'Agent'),
        ('AUTRE', 'Autre'),
    ]

    user = models.OneToOneField(  # Lien 1-1 avec un utilisateur Django
        User, 
        on_delete=models.CASCADE,  # Supprime l'Agent si l'User est supprimé
        verbose_name="Utilisateur"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  # Rôle avec choix prédéfinis
    service = models.CharField(max_length=100, blank=True)  # Champ facultatif

    def __str__(self):
        """Représentation textuelle (ex: dans l'admin Django)"""
        return f"{self.user.username} ({self.get_role_display()})"

class Categorie(models.Model):
    """
    Catégories pour classer les transactions (ex: "Nourriture", "Loyer").
    Peut être une dépense ou une entrée.
    """
    TYPE_CHOICES = [
        ("DEPENSE", "Dépense"),
        ("ENTREE", "Entrée de fonds"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  # Type obligatoire
    nom = models.CharField(max_length=100)  # Nom de la catégorie

    def __str__(self):
        return f"{self.nom} ({self.type})"

class Transaction(models.Model):
    """
    Enregistrement d'une opération financière (dépense ou entrée).
    Liée à un utilisateur et une catégorie.
    """
    type = models.CharField(max_length=10, choices=Categorie.TYPE_CHOICES)  # DEPENSE/ENTREE
    montant = models.DecimalField(max_digits=10, decimal_places=2)  # Montant avec 2 décimales
    date = models.DateField()  # Date de la transaction
    description = models.TextField(blank=True)  # Détails optionnels
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)  # Lien à une catégorie
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)  # Lien à l'utilisateur

    class Meta:
        ordering = ['-date']  # Tri par date décroissante par défaut

class BudgetMensuel(models.Model):
    """
    Budget défini par un utilisateur pour un mois donné.
    - Un seul budget par utilisateur et par mois (contrainte unique_together).
    """
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    mois = models.CharField(max_length=7)  # Format "YYYY-MM"
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)  # Budget total

    class Meta:
        unique_together = ('utilisateur', 'mois')  # Évite les doublons