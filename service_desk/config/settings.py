from pathlib import Path

CUST_TYPE = 'customer'
OPER_TYPE = 'operator'
DEV_TYPE = 'developer'
SD_ENV_TYPE = 'service-desk'
SOFT_ENV_TYPE = 'software'
DEFAULT_ISSUE_TYPE_ID = 1
DEFAULT_PRIORITY_ID = 3
SD_INITIAL_STATUS = 15
SOFT_INITIAL_STATUS = 26
GROUP_TYPES = [
    ('customer', 'Customer'),
    ('operator', 'Operator'),
    ('developer', 'Developer')
]
ENV_TYPES = [
    ('service-desk', 'Service Desk'),
    ('software', 'Software')
]

BASE_DIR = Path(__file__).resolve().parent.parent  # Build paths inside the project like this: BASE_DIR / 'subdir'.
SECRET_KEY = 'django-insecure-z(g7^uxx3*)@ctru=wvchu5tezwzd3s@0m01rozf=-szc8%_!@'
ALLOWED_HOSTS = ['192.168.0.100', '192.168.0.101', '127.0.0.1']
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
#STATIC_URL = '/static/'  # Static files (CSS, JavaScript, Images) https://docs.djangoproject.com/en/3.2/howto/static-files/
#STATIC_ROOT = f'{BASE_DIR}'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'logged_out'
LANGUAGE_CODE = 'en-us'  # Internationalization https://docs.djangoproject.com/en/3.2/topics/i18n/
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEBUG = True
TIME_ZONE = 'Europe/Zagreb'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Default primary key field type https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS = [
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'tinymce'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware'
]

MIDDLEWARE_CLASSES = [
    'app.middleware.test'
]

STATICFILES_DIRS = [
    f'{BASE_DIR}/static'
]
#STATICFILES_DIRS = [BASE_DIR / 'static']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [f'{BASE_DIR}/static/site/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.user_tenant_type',
                'app.context_processors.get_user_icon',
                'app.context_processors.get_media'
            ],
        },
    },
]

DATABASES = {  # https://docs.djangoproject.com/en/3.2/ref/settings/#databases
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'service-desk',
        'USER': 'sd_admin',
        'PASSWORD': 'NdhsrlBcGYY8mK2sKoy6XSLQR3hFb75giZz',
        'HOST': '192.168.0.100',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [  # https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
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


TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table, paste, searchreplace, link, image, code, autoresize",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'toolbar1': 'formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | table | link image',
    'menubar': True,
    'selector': 'textarea'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {levelname} {request} {status_code} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'format-request': {
            'format': '{asctime} {levelname} "{request} {status_code}" {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'request': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/request.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
        },
        'template': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/template.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
        'server': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/server.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
        'security': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/security.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
        'sql': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': f'{BASE_DIR}/logs/sql.log',
            'maxBytes': 1024*1024*50,
            'backupCount': 15,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['template'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['server'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.security.*': {
            'handlers': ['security'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends.schema': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
