"""
Configuration globale du projet Django.
"""

from pathlib import Path

# Chemins de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent  # Racine du projet

# Sécurité (⚠️ À modifier en production !)
SECRET_KEY = 'django-insecure-f(&22@kuaw-7yk&_)3$wf8_2f3j-4jq*rcqh4r*mqyikq759_5'  # Clé secrète pour le chiffrement
DEBUG = True  # Mode débogage (désactiver en production)
ALLOWED_HOSTS = []  # Domaines autorisés (vide = tous en debug)

# Applications installées
INSTALLED_APPS = [
    # Apps Django par défaut
    'django.contrib.admin',       # Interface admin
    'django.contrib.auth',        # Système d'authentification
    'django.contrib.contenttypes',# Gestion des types de contenu
    'django.contrib.sessions',    # Gestion des sessions
    'django.contrib.messages',    # Gestion des messages
    'django.contrib.staticfiles', # Gestion des fichiers statics
    
    # Apps tierces
    'rest_framework',             # Framework REST
    'rest_framework.authtoken',   # Authentification par tokens
    'corsheaders',               # Gestion CORS (Cross-Origin Resource Sharing)
    
    # Apps personnalisées
    'management',                # Votre application métier
]

# Middlewares (traitement des requêtes/responses)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Sécurité de base
    'django.contrib.sessions.middleware.SessionMiddleware',  # Gestion sessions
    'django.middleware.common.CommonMiddleware',      # Traitement des requêtes
    'django.middleware.csrf.CsrfViewMiddleware',      # Protection CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Authentification
    'django.contrib.messages.middleware.MessageMiddleware',    # Messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protection clickjacking
    'corsheaders.middleware.CorsMiddleware',         # Gestion CORS
]

# Configuration CORS (⚠️ À restreindre en production !)
CORS_ALLOW_ALL_ORIGINS = True  # Autorise toutes les origines (développement seulement)

# Configuration des URLs
ROOT_URLCONF = 'backend.urls'  # Fichier racine des URLs

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Serveur WSGI
WSGI_APPLICATION = 'backend.wsgi.application'

# Base de données (SQLite par défaut)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Fichier de la base SQLite
    }
}

# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # Vérifie la similarité avec les infos utilisateur
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},           # Longueur minimale
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},          # Mots de passe courants
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},         # Pas entièrement numérique
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}


# Internationalisation
LANGUAGE_CODE = 'en-us'  # Langue par défaut
TIME_ZONE = 'UTC'        # Fuseau horaire
USE_I18N = True          # Activation de l'internationalisation
USE_TZ = True            # Utilisation des timezones

# Fichiers statiques (CSS, JS, images)
STATIC_URL = 'static/'   # URL de base pour les fichiers statics

# Clé primaire par défaut des modèles
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'