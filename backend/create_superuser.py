import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = "alves"
password = "alves2007"


if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
    print("Superutilisateur créé !")
else:
    print("Le superutilisateur existe déjà.")