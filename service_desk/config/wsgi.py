# WSGI config for config project.
#   It exposes the WSGI callable as a module-level variable named ``application``.
#   For more information on this file, https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/

import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()

