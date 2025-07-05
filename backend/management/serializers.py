from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from management.models import Agent

class LoginSerializer(serializers.Serializer):
    """Sérialiseur pour la connexion utilisateur"""
    
    username = serializers.CharField()  # Champ nom d'utilisateur
    password = serializers.CharField()  # Champ mot de passe

    def validate(self, data):
        """Valide les credentials et retourne le token"""
        # Authentification avec Django
        user = authenticate(**data)
        
        if user and user.is_active:  # Si utilisateur valide
            # Récupère ou crée un token
            token, _ = Token.objects.get_or_create(user=user)

            try:
                # Récupère le profil agent associé
                agent = Agent.objects.get(user=user)
                role = agent.role
            except Agent.DoesNotExist:
                role = "AUTRE"  # Valeur par défaut

            return {
                "token": token.key,  # Token d'authentification
                "username": user.username,
                "role": role
            }

        raise serializers.ValidationError("Identifiants invalides")

class CategorieSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories"""
    class Meta:
        model = Categorie
        fields = '__all__'  # Tous les champs du modèle

class TransactionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les transactions avec info de catégorie"""
    
    # Champ calculé pour le nom de catégorie
    categorie_nom = serializers.CharField(
        source='categorie.nom', 
        read_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'montant', 'date', 
            'description', 'categorie', 
            'categorie_nom', 'utilisateur'
        ]
        read_only_fields = ['utilisateur']  # Auto-défini

class BudgetMensuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetMensuel
        fields = ['id', 'utilisateur', 'mois', 'montant_total']
        read_only_fields = ['utilisateur']