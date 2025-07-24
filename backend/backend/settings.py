"""
Configuration globale du projet Django.
"""

from pathlib import Path
import os

# Chemins de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent  # Racine du projet

# Sécurité (⚠️ À modifier en production !)
SECRET_KEY = os.getenv('SECRET_KEY', 'clé-par-défaut-à-changer')
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # Mode debug activé si la variable d'environnement est True
ALLOWED_HOSTS = ['*']  # Domaines autorisés (vide = tous en debug)

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
# Pour éviter l'erreur CSRF sur Render
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

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

# Configuration de la base de données pour PostgreSQL (Render fournit PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
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
STATIC_URL = '/static/'   # URL de base pour les fichiers statics
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Répertoire de collecte des fichiers statics


# Clé primaire par défaut des modèles
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'