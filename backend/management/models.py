from django.db import models
from django.contrib.auth.models import User

# Modèle Agent : étend le modèle User de Django avec des champs supplémentaires
class Agent(models.Model):
    """
    Associe des informations supplémentaires à un utilisateur (User),
    comme son rôle ou son service.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('AGENT', 'Agent'),
        ('AUTRE', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur", default="")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rôle de l'agent")
    service = models.CharField(max_length=100, blank=True, verbose_name="Service ou département")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"  # Représentation lisible

    class Meta:
        verbose_name = "Agent"  # Nom singulier dans l'admin
        verbose_name_plural = "Agents"  # Nom pluriel dans l'admin
        ordering = ['role', 'user']  # Tri par rôle puis par utilisateur

# Modèle Categorie : catégorise les opérations financières
class Categorie(models.Model):
    TYPE_CHOICES = [
        ("DEPENSE", "Dépense"),
        ("ENTREE", "Entrée de fonds"),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="DEPENSE")
    nom = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return f"{self.nom} ({self.type})"


class Transaction(models.Model):
    type = models.CharField(max_length=10, choices=Categorie.TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.type} - {self.montant} FC - {self.date}"


class Budget(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    mois = models.DateField(help_text="Utiliser le 1er jour du mois, ex: 2025-06-01")
    montant_max = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('utilisateur', 'mois')
        verbose_name = "Budget Mensuel"
        verbose_name_plural = "Budgets Mensuels"

    def __str__(self):
        return f"{self.utilisateur.username} - {self.mois.strftime('%B %Y')} - {self.montant_max} FC"