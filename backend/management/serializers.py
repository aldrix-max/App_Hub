from rest_framework import serializers
from .models import Categorie, Transaction, Budget
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from management.models import Agent

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)

            try:
                agent = Agent.objects.get(user=user)
                role = agent.role
            except Agent.DoesNotExist:
                role = "AUTRE"

            return {
                "token": token.key,
                "username": user.username,
                "role": role
            }

        raise serializers.ValidationError("Nom d’utilisateur ou mot de passe invalide.")

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'montant', 'date', 'description', 'categorie', 'categorie_nom', 'utilisateur']
        read_only_fields = ['utilisateur']


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['utilisateur']
