from pathlib import Path
from . import configuration as conf

CUST_TYPE = 'customer'
OPER_TYPE = 'operator'
DEV_TYPE = 'developer'
SD_ENV_TYPE = 'service-desk'
SOFT_ENV_TYPE = 'software'
DEFAULT_ISSUE_TYPE_ID = 1
DEFAULT_PRIORITY_ID = 3
SD_INITIAL_STATUS = 15
SOFT_INITIAL_STATUS = 26
ROLES = [
    ('customer', 'Customer'),
    ('operator', 'Operator'),
    ('developer', 'Developer')
]
ENV_TYPES = [
    ('service-desk', 'Service Desk'),
    ('software', 'Software')
]
ALLOW_FILE_EXTENSIONS = [
    '.pdf', '.txt', '.doc', '.docx', '.odt', '.rtf', '.html', '.pptx',  # documents
    '.csv', '.xlsx', '.ods', '.tsv',  # sheets
    '.jpg', '.jpeg', '.png', '.svg', '.webp', '.ico', '.bmp', '.tiff', '.jfif'  # img
    '.mp3',  # music
    '.mp4', '.mkv', '.avi', '.webm', '.gif', '.gifv'  # video
    '.zip', '.rar', '.7zip', '.tar', '.gz',  # zip
    'java', '.py', '.c', '.cpp', '.js', '.gs', '.groovy', '.sh'  # code ,
]
FILE_EXTENSIONS = {
    'pdf': ['pdf'],
    'doc': ['txt', 'doc', 'docx', 'odt', 'rtf', 'html', 'pptx'],
    'sheet': ['csv', 'xlsx', 'ods', 'tsv'],
    'img': ['jpg', 'jpeg', 'png', 'svg', 'webp', '.ico', 'bmp', 'tiff', 'jfif'],
    'music': ['mp3'],
    'video': ['mp4', 'mkv', 'avi', 'webm', 'gif', 'gifv'],
    'zip': ['zip', 'rar', '7zip', 'tar', 'gz'],
    'code': ['java', 'py', 'c', 'cpp', 'js', 'gs', 'groovy', 'sh']
}

BASE_DIR = Path(__file__).resolve().parent.parent  # Build paths inside the project like this: BASE_DIR / 'subdir'.
LOG_DIR = BASE_DIR / 'logs'
SECRET_KEY = conf.SECRET_KEY
ALLOWED_HOSTS = conf.ALLOWED_HOSTS
ROOT_URLCONF = 'conf.urls'
WSGI_APPLICATION = 'conf.wsgi.application'
# STATIC_URL = '/static/'  # Static files (CSS, JavaScript, Images) https://docs.djangoproject.com/en/3.2/howto/static-files/
# STATIC_ROOT = f'{BASE_DIR}'
STATIC_URL = '/static/'
STATIC_ROOT = conf.STATIC_ROOT
MEDIA_URL = '/media/'
MEDIA_ROOT = conf.MEDIA_ROOT
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'logged_out'
LANGUAGE_CODE = conf.LANGUAGE_CODE  # Internationalization https://docs.djangoproject.com/en/3.2/topics/i18n/
SITE_NAME = conf.SITE_NAME
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEBUG = conf.DEBUG
TIME_ZONE = conf.TIME_ZONE
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Default primary key field type https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
AUTH_USER_MODEL = 'core.User'
CACHE_ENABLED = conf.CACHE['ENABLED']
USE_X_FORWARDED_HOST = conf.USE_X_FORWARDED_HOST
SECURE_SSL_REDIRECT = conf.SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE = conf.SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE = conf.CSRF_COOKIE_SECURE
CSRF_TRUSTED_ORIGINS = conf.CSRF_TRUSTED_ORIGINS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
MONITORING_TOKEN = conf.MONITORING_TOKEN

# Email: use SMTP when a host is configured, otherwise fall back to console
if conf.SMTP_SERVER['HOST']:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = conf.SMTP_SERVER['HOST']
    EMAIL_PORT = conf.SMTP_SERVER['PORT']
    EMAIL_HOST_USER = conf.SMTP_SERVER['USER']
    EMAIL_HOST_PASSWORD = conf.SMTP_SERVER['PASSWORD']
    EMAIL_USE_SSL = conf.SMTP_SERVER['USE_SSL']
    EMAIL_USE_TLS = not conf.SMTP_SERVER['USE_SSL']
    DEFAULT_FROM_EMAIL = conf.SMTP_SERVER['FROM']
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
INSTALLED_APPS = [
    'core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'tinymce',
    'django_extensions',
    'django_prometheus'
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # must stay first to time the whole request
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware'  # must stay last to time the whole request
]

STATICFILES_DIRS = [
    f'{BASE_DIR}/static'
]

LOCALE_PATH = [
    f'{BASE_DIR}/locale'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [f'{BASE_DIR}/staticfiles/site/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.context_tenant_session',
                'core.context_processors.get_user_icon',
                'core.context_processors.get_media',
                'core.context_processors.get_tenants',
            ]
        },
    },
]

DATABASES = {  # https://docs.djangoproject.com/en/3.2/ref/settings/#databases
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': conf.DATABASE['NAME'],
        'USER': conf.DATABASE['USER'],
        'PASSWORD': conf.DATABASE['PASSWORD'],
        'HOST': conf.DATABASE['HOST'],
        'PORT': conf.DATABASE['PORT'],
        'CONN_MAX_AGE': conf.DATABASE['CONN_MAX_AGE'],
        'CONN_HEALTH_CHECKS': True
    }
}

REDIS_PROTOCOL = 'rediss' if bool(conf.REDIS['SSL']) else 'redis'

if CACHE_ENABLED:  # Falls back to the in-memory LocMemCache when disabled
    CACHES = {
        'default': {
            'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',  # django-redis subclass + Prometheus cache metrics
            'LOCATION': f"{REDIS_PROTOCOL}://{conf.REDIS['HOST']}:{conf.REDIS['PORT']}/{conf.REDIS['DB']}",
            'KEY_PREFIX': 'service-desk',
            'OPTIONS': {
                'PASSWORD': conf.REDIS['PASSWORD'],
                'CONNECTION_POOL_KWARGS': {
                    'username': conf.REDIS['USER'],
                },
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5
            }
        }
    }

    CACHE_MIDDLEWARE_ALIAS = 'default'  # which cache alias to use
    CACHE_MIDDLEWARE_SECONDS = conf.CACHE['TTL']  # number of seconds to cache a page for (TTL)
    CACHE_MIDDLEWARE_KEY_PREFIX = ''  # should be used if the cache is shared across multiple sites that use the same Django instance


AUTH_PASSWORD_VALIDATORS = [  # https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
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
            'format': '{asctime} [{name}] {levelname} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'request': {
            'format': "{asctime} [{name}] {levelname} {request.user.username} {request.method} {status_code} {message}",
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'sql': {
            'format': "{asctime} [{name}] {levelname} {alias} {sql} {params} [{duration}]",
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {
        'debug_mode': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'app': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': LOG_DIR / 'app.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
        },
        'request': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'request',
            'filename': LOG_DIR / 'request.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
        },
        'request.server': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': LOG_DIR / 'request.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
        },
        'security': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
        },
        'server': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': LOG_DIR / 'server.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
        },
        'template': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': LOG_DIR / 'template.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
        },
        'sql': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'sql',
            'filename': LOG_DIR / 'sql.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
            'filters': ['debug_mode']
        },
        'prometheus': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': LOG_DIR / 'prometheus.log',
            'maxBytes': conf.LOG['MAX_SIZE'],
            'backupCount': conf.LOG['MAX_COUNT'],
            'filters': ['debug_mode']
        }
    },
    'loggers': {
        'core': {
            'handlers': ['app'],  # custom
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'core.utils.util_manager': {
            'handlers': ['app'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'core.models': {
            'handlers': ['app'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.security': {  # security
            'handlers': ['security'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.security.csrf': {
            'handlers': ['security'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'core.receivers': {
            'handlers': ['security'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.db': {  # database
            'handlers': ['sql'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['sql'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.db.backends.schema': {
            'handlers': ['sql'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.db.models': {
            'handlers': ['sql'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.request': {  # request
            'handlers': ['request'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.server': {  # basically this is get/post requests
            'handlers': ['request.server'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.template': {  # template
            'handlers': ['template'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django_prometheus': {   # prometheus
            'handlers': ['prometheus'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django_prometheus.exports': {
            'handlers': ['prometheus'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.utils.autoreload': {  # server
            'handlers': ['server'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.utils': {
            'handlers': ['server'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'django.dispatch': {
            'handlers': ['server'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'asyncio': {
            'handlers': ['server'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        },
        'concurrent.futures': {
            'handlers': ['server'],
            'level': conf.LOG['LEVEL'],
            'propagate': True,
        }
    }
}
