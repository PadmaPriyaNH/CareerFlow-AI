import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
# normalize: remove empty entries
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]
# allow Django test client host and CI runner
if 'test' in sys.argv or os.getenv('CI', '').lower() in ('1','true'):
    ALLOWED_HOSTS.append('testserver')

# Application Definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # MFA / Two-Factor
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'two_factor',
    
    # Local Apps
    'accounts',
    'interviews',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Prefer DATABASE_URL (12-factor) otherwise fall back to local sqlite
import dj_database_url
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
        }
    }

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Security and CSRF (set proper hosts in production)
CSRF_TRUSTED_ORIGINS = [
    *(f"http://{h}" for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h),
    *(f"https://{h}" for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h),
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = os.getenv('DEBUG', 'True') != 'True'
CSRF_COOKIE_SECURE = os.getenv('DEBUG', 'True') != 'True'

# Production security hardening (enabled automatically when DEBUG=False)
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Use WhiteNoise compressed manifest storage for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' if not DEBUG else 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Require a secure SECRET_KEY in production
if not DEBUG and (not SECRET_KEY or SECRET_KEY.startswith('django-insecure')):
    raise RuntimeError('SECRET_KEY must be set to a secure value in production')

# Media Files (Resumes)
USE_AZURE_STORAGE = os.getenv('USE_AZURE_STORAGE', 'False').lower() in ('1', 'true', 'yes')
if USE_AZURE_STORAGE:
    # Optional Azure Blob Storage backend for MEDIA
    INSTALLED_APPS.append('storages')
    AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME', '')
    AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY', '')
    AZURE_CONTAINER = os.getenv('AZURE_CONTAINER', 'media')
    AZURE_CUSTOM_DOMAIN = os.getenv('AZURE_CUSTOM_DOMAIN', f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net") if os.getenv('AZURE_ACCOUNT_NAME') else ''

    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
    MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/" if AZURE_CUSTOM_DOMAIN else f"/{AZURE_CONTAINER}/"
    # MEDIA_ROOT not used with Azure backend
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
# Use two_factor default URL names without explicit namespace
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# AI Configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')

# LangChain configuration (adjust if using external providers)
AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama')
AI_MODEL = os.getenv('AI_MODEL', OLLAMA_MODEL)