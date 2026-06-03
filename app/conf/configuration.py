import os
from django.core.management.utils import get_random_secret_key


def env_bool(name: str, default=False):
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "y", "t")


def env_int(name: str, default):
    value = os.getenv(name)
    if value is None or value == '':
        return default
    return int(value)


def env_str(name: str, default=None):
    value = os.getenv(name)
    if value is None or value == '':
        return default
    return value


SITE_NAME = env_str('DJANGO_SITE_NAME', default='ServiceDeskApp')
STATIC_ROOT = env_str('STATIC_ROOT', default='staticfiles')
MEDIA_ROOT = env_str('MEDIA_ROOT', default='media')
SECRET_KEY = env_str('DJANGO_SECRET_KEY', default=get_random_secret_key())
ALLOWED_HOSTS = env_str('ALLOWED_HOSTS', default='*').split(',')
CSRF_TRUSTED_ORIGINS = env_str('CSRF_TRUSTED_ORIGINS', default='http://localhost').split(',')
DEBUG = env_bool('DJANGO_DEBUG', default=False)
TIME_ZONE = env_str('TIME_ZONE', default='Europe/Zagreb')
LANGUAGE_CODE = env_str('LANGUAGE_CODE', default='en-us')  # Default lang if browser will not detect

USE_X_FORWARDED_HOST = env_bool('USE_X_FORWARDED_HOST', default=True)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', default=True)

LOG = {
    'MAX_SIZE': 1024 * 1024 * 15,  # 15MB
    'MAX_COUNT': 5,  # Per logger
    'LEVEL': env_str('LOG_LEVEL', default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
}

CACHE = {
    'ENABLED': env_bool('CACHE_ENABLED', default=False),
    'TTL': env_int('CACHE_TTL', default=600)
}

DATABASE = {  # PostgreSQL
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASS'),
    'HOST': env_str('DB_HOST', default='127.0.0.1'),
    'PORT': env_int('DB_PORT', default=5432),
    'CONN_MAX_AGE': env_int('DB_CONN_MAX_AGE', default=300)
}

SMTP_SERVER = {
    'USER': os.getenv('SMTP_USER'),
    'PASSWORD': os.getenv('SMTP_PASS'),
    'HOST': os.getenv('SMTP_HOST'),
    'PORT': env_int('SMTP_PORT', default=465),
    'USE_SSL': env_bool('SMTP_USE_SSL', default=True),
    'FROM': os.getenv('SMTP_FROM', default=os.getenv('SMTP_USER'))
}

REDIS = {
    'USER': os.getenv('REDIS_USER'),
    'PASSWORD': os.getenv('REDIS_PASS'),
    'HOST': env_str('REDIS_HOST', default='127.0.0.1'),
    'PORT': env_int('REDIS_PORT', default=6379),
    'DB': env_int('REDIS_DB', default=0),
    'SSL': env_bool('REDIS_SSL', default=False)
}
