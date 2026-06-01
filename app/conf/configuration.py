import os
from django.core.management.utils import get_random_secret_key


def env_bool(name: str, default=False):
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "y", "t")


SITE_NAME = os.getenv('DJANGO_SITE_NAME', default='ServiceDeskApp')
STATIC_ROOT = os.getenv('STATIC_ROOT', default='staticfiles')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', default='media')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', default=get_random_secret_key())
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default='*').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', default='http://localhost').split(',')
DEBUG = env_bool('DJANGO_DEBUG', default=False)
TIME_ZONE = os.getenv('TIME_ZONE', default='Europe/Zagreb')
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', default='en-us')  # Default lang if browser will not detect

USE_X_FORWARDED_HOST = env_bool('USE_X_FORWARDED_HOST', default=True)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', default=True)

LOG = {
    'MAX_SIZE': 1024 * 1024 * 15,  # 15MB
    'MAX_COUNT': 5,  # Per logger
    'LEVEL': os.getenv('LOG_LEVEL', default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
}

CACHE = {
    'ENABLED': env_bool('CACHE_ENABLED', default=False),
    'TTL': int(os.getenv('CACHE_TTL', default=600))
}

DATABASE = {  # PostgreSQL
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASS'),
    'HOST': os.getenv('DB_HOST', default='127.0.0.1'),
    'PORT': os.getenv('DB_PORT', default=5432),
    'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', default=300))
}

SMTP_SERVER = {
    'USER': os.getenv('SMTP_USER'),
    'PASSWORD': os.getenv('SMTP_PASS'),
    'HOST': os.getenv('SMTP_HOST'),
    'PORT': int(os.getenv('SMTP_PORT', default=465)),
    'USE_SSL': env_bool('SMTP_USE_SSL', default=True),
    'FROM': os.getenv('SMTP_FROM', default=os.getenv('SMTP_USER'))
}

REDIS = {
    'USER': os.getenv('REDIS_USER'),
    'PASSWORD': os.getenv('REDIS_PASS'),
    'HOST': os.getenv('REDIS_HOST', default='127.0.0.1'),
    'PORT': os.getenv('REDIS_PORT', default=6379),
    'DB': os.getenv('REDIS_DB', default=0),
    'SSL': env_bool('REDIS_SSL', default=False)
}
