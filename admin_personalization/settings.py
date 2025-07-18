import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r3n#v7ukjkf=b^b*foys@gk)owmw@dvv1eg841j0fflqsk-5%$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'admin_theme_manager',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'graphene_django',
    'corsheaders', # Added for CORS
    'rest_framework.authtoken', # <--- THIS LINE IS CRUCIAL

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Added for CORS, placed high
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'admin_personalization.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'admin_theme_manager/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'admin_theme_manager.context_processors.active_theme', # Changed to active_theme
            ],
        },
    },
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static", # Add this line for project-wide static
    BASE_DIR / "admin_theme_manager" / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


WSGI_APPLICATION = 'admin_personalization.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC' # Keep this as UTC to avoid tzdata issues

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
GRAPHENE = {
    'SCHEMA': 'admin_theme_manager.schema.schema'
}
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC' # Ensure Celery also uses UTC

# --- CORS HEADERS CONFIGURATION ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Example for a frontend React/Vue in dev
    "http://127.0.0.1:3000",
    # "https://votre-domaine-frontend.com", # Your production domain
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication', # <--- Ceci est en premier
        'rest_framework.authentication.TokenAuthentication',   # <--- THIS LINE IS ALSO CRUCIAL
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # You might want to set this to IsAuthenticated if you want all DRF views
        # to require authentication by default, or keep your IsSuperUser for specific views.
        # 'rest_framework.permissions.IsAuthenticated',
    ]
}
