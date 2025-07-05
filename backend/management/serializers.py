from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from management.models import Agent


class LoginSerializer(serializers.Serializer):
    """
    Sérialiseur pour la connexion :
    - Valide les identifiants
    - Retourne un token JWT + infos utilisateur
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Vérifie les credentials et retourne le token + rôle"""
        user = authenticate(**data)
        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            try:
                role = Agent.objects.get(user=user).role  # Récupère le rôle
            except Agent.DoesNotExist:
                role = "AUTRE"
            return {"token": token.key, "username": user.username, "role": role}
        raise serializers.ValidationError("Identifiants invalides")

class CategorieSerializer(serializers.ModelSerializer):
    """Convertit les catégories en JSON (tous les champs)"""
    class Meta:
        model = Categorie
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    """
    Sérialise les transactions avec des champs supplémentaires :
    - categorie_nom : Nom lisible de la catégorie
    - utilisateur en lecture seule (auto-défini)
    """
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'montant', 'date', 'description', 'categorie', 'categorie_nom', 'utilisateur']
        read_only_fields = ['utilisateur']  # Empêche la modification via l'API

class BudgetMensuelSerializer(serializers.ModelSerializer):
    """Sérialise les budgets mensuels (utilisateur en lecture seule)"""
    class Meta:
        model = BudgetMensuel
        fields = ['id', 'utilisateur', 'mois', 'montant_total']
        read_only_fields = ['utilisateur']