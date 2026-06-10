import smtplib
from logging import getLogger
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from .metrics import require_monitoring_token

log = getLogger('core.health')

SMTP_TIMEOUT = 5
_REDIS_PROBE_KEY = 'healthz:probe'


def check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return {'status': 'ok', 'detail': 'Database connection successful'}
    except Exception as e:
        log.error(f'Healthz database check failed: {e}')
        return {'status': 'fail', 'detail': str(e)}


def check_redis():
    if not settings.CACHE_ENABLED:
        return {'status': 'disabled', 'detail': 'Cache is disabled'}
    try:
        cache.set(_REDIS_PROBE_KEY, '1', 10)
        if cache.get(_REDIS_PROBE_KEY) != '1':
            return {'status': 'fail', 'detail': 'Redis probe value mismatch'}
        return {'status': 'ok', 'detail': 'Redis connection successful'}
    except Exception as e:
        log.error(f'Healthz redis check failed: {e}')
        return {'status': 'fail', 'detail': str(e)}


def check_smtp():
    host = getattr(settings, 'EMAIL_HOST', '')
    if not host:
        return {'status': 'disabled', 'detail': 'SMTP is not configured'}
    try:
        smtp_cls = smtplib.SMTP_SSL if getattr(settings, 'EMAIL_USE_SSL', False) else smtplib.SMTP
        server = smtp_cls(host, settings.EMAIL_PORT, timeout=SMTP_TIMEOUT)
        server.ehlo()
        server.quit()
        return {'status': 'ok', 'detail': 'SMTP connection successful'}
    except Exception as e:
        log.error(f'Healthz smtp check failed: {e}')
        return {'status': 'fail', 'detail': str(e)}


@never_cache
@csrf_exempt
def healthz(request):
    """Lightweight health check for monitoring (Nagios). Guarded by a Bearer token."""
    auth_error = require_monitoring_token(request)
    if auth_error:
        return auth_error

    components = {
        'database': check_database(),
        'redis': check_redis(),
        'smtp': check_smtp(),
    }

    critical_failed = any(
        components[name]['status'] == 'fail' for name in ('database', 'redis')
    )
    smtp_failed = components['smtp']['status'] == 'fail'

    if critical_failed:
        status, http_status = 'fail', 503
    elif smtp_failed:
        status, http_status = 'degraded', 200
    else:
        status, http_status = 'ok', 200

    return JsonResponse({'status': status, 'components': components}, status=http_status)


@never_cache
def health(request):
    """Liveness probe (no auth): returns 200 'ok' while the process is up."""
    return HttpResponse('ok')
