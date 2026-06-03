import hmac
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django_prometheus.exports import ExportToDjangoView

log = logging.getLogger('django_prometheus.exports')


def metrics_view(request):
    """Expose Prometheus metrics, gated behind a bearer token.

    The token is read from settings.PROMETHEUS_METRICS_TOKEN (env
    PROMETHEUS_METRICS_TOKEN); requests must send `Authorization: Bearer <token>`.
    When no token is configured the endpoint is disabled (404) so metrics are
    never served unauthenticated by accident.
    """
    token = settings.PROMETHEUS_METRICS_TOKEN
    if not token:
        log.warning('PROMETHEUS_METRICS_TOKEN is not set; /metrics is disabled')
        return HttpResponse(status=404)

    header = request.META.get('HTTP_AUTHORIZATION', '')
    prefix = 'Bearer '
    provided = header[len(prefix):] if header.startswith(prefix) else ''
    if not provided or not hmac.compare_digest(provided, token):
        return HttpResponseForbidden()

    return ExportToDjangoView(request)
