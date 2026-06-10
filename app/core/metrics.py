import hmac
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django_prometheus.exports import ExportToDjangoView

log = logging.getLogger('django_prometheus.exports')


def require_monitoring_token(request):
    """Guard monitoring endpoints with a bearer token.

    The token is read from settings.MONITORING_TOKEN (env MONITORING_TOKEN);
    requests must send `Authorization: Bearer <token>`. Returns an HttpResponse
    to short-circuit the view when auth fails, or None when the request is
    authorized. When no token is configured the endpoint is disabled (404) so
    monitoring data is never served unauthenticated by accident. Shared by
    /metrics and /healthz.
    """
    token = settings.MONITORING_TOKEN
    if not token:
        log.warning('MONITORING_TOKEN is not set; monitoring endpoints are disabled')
        return HttpResponse(status=404)

    header = request.META.get('HTTP_AUTHORIZATION', '')
    prefix = 'Bearer '
    provided = header[len(prefix):] if header.startswith(prefix) else ''
    if not provided or not hmac.compare_digest(provided, token):
        return HttpResponseForbidden()

    return None


def metrics_view(request):
    """Expose Prometheus metrics, gated behind a bearer token."""
    auth_error = require_monitoring_token(request)
    if auth_error:
        return auth_error
    return ExportToDjangoView(request)
