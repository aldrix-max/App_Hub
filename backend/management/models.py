from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Agent(models.Model):
    """
    Étend le modèle User de Django pour ajouter des champs spécifiques aux agents.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('AGENT', 'Agent'),
        ('AUTRE', 'Autre'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        related_name="agent_profile"  # Ajout d'un related_name
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    service = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

class Categorie(models.Model):
    """
    Catégories pour classer les transactions.
    """
    TYPE_CHOICES = [
        ("DEPENSE", "Dépense"),
        ("ENTREE", "Entrée de fonds"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100, unique=True)  # Nom unique

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['type', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"

class Transaction(models.Model):
    """
    Enregistrement d'une opération financière.
    """
    TYPE_CHOICES = Categorie.TYPE_CHOICES

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # Valeur minimale
    )
    date = models.DateField()
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,  # Empêche la suppression si des transactions existent
        related_name="transactions"
    )
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Empêche la suppression si des transactions existent
        related_name="transactions"
    )
    created_at = models.DateTimeField(auto_now=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de modification

    class Meta:
        ordering = ['-date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.montant}€ ({self.date})"

class BudgetMensuel(models.Model):
    """
    Budget défini par un utilisateur pour un mois donné.
    """
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets"
    )
    mois = models.CharField(max_length=7)  # Format "YYYY-MM"
    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    class Meta:
        unique_together = ('utilisateur', 'mois')
        verbose_name = "Budget Mensuel"
        verbose_name_plural = "Budgets Mensuels"
        ordering = ['-mois']

    def __str__(self):
        return f"Budget {self.mois} - {self.utilisateur.username}"