from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, RequestFactory, override_settings

from core import health


class CheckDatabaseTests(SimpleTestCase):
    @patch('core.health.connection')
    def test_returns_ok_when_query_succeeds(self, mock_conn):
        cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = cursor
        result = health.check_database()
        self.assertEqual(result['status'], 'ok')
        cursor.execute.assert_called_once_with('SELECT 1')

    @patch('core.health.connection')
    def test_returns_fail_when_query_raises(self, mock_conn):
        mock_conn.cursor.side_effect = Exception('connection refused')
        result = health.check_database()
        self.assertEqual(result['status'], 'fail')
        self.assertIn('connection refused', result['detail'])


class CheckRedisTests(SimpleTestCase):
    @patch('core.health.settings')
    def test_returns_disabled_when_cache_off(self, mock_settings):
        mock_settings.CACHE_ENABLED = False
        result = health.check_redis()
        self.assertEqual(result['status'], 'disabled')

    @patch('core.health.cache')
    @patch('core.health.settings')
    def test_returns_ok_when_cache_works(self, mock_settings, mock_cache):
        mock_settings.CACHE_ENABLED = True
        mock_cache.get.return_value = '1'
        result = health.check_redis()
        self.assertEqual(result['status'], 'ok')
        mock_cache.set.assert_called_once()

    @patch('core.health.cache')
    @patch('core.health.settings')
    def test_returns_fail_when_cache_raises(self, mock_settings, mock_cache):
        mock_settings.CACHE_ENABLED = True
        mock_cache.set.side_effect = Exception('redis down')
        result = health.check_redis()
        self.assertEqual(result['status'], 'fail')
        self.assertIn('redis down', result['detail'])

    @patch('core.health.cache')
    @patch('core.health.settings')
    def test_returns_fail_when_probe_value_mismatch(self, mock_settings, mock_cache):
        mock_settings.CACHE_ENABLED = True
        mock_cache.get.return_value = None
        result = health.check_redis()
        self.assertEqual(result['status'], 'fail')
        self.assertIn('mismatch', result['detail'])


class CheckSmtpTests(SimpleTestCase):
    @patch('core.health.smtplib')
    @patch('core.health.settings')
    def test_returns_disabled_when_no_host(self, mock_settings, mock_smtplib):
        mock_settings.EMAIL_HOST = ''
        result = health.check_smtp()
        self.assertEqual(result['status'], 'disabled')
        mock_smtplib.SMTP.assert_not_called()
        mock_smtplib.SMTP_SSL.assert_not_called()

    @patch('core.health.smtplib')
    @patch('core.health.settings')
    def test_uses_plain_smtp_without_ssl(self, mock_settings, mock_smtplib):
        mock_settings.EMAIL_HOST = 'mail.example.com'
        mock_settings.EMAIL_PORT = 587
        mock_settings.EMAIL_USE_SSL = False
        result = health.check_smtp()
        self.assertEqual(result['status'], 'ok')
        mock_smtplib.SMTP.assert_called_once_with('mail.example.com', 587, timeout=health.SMTP_TIMEOUT)
        mock_smtplib.SMTP_SSL.assert_not_called()

    @patch('core.health.smtplib')
    @patch('core.health.settings')
    def test_uses_smtp_ssl_with_ssl(self, mock_settings, mock_smtplib):
        mock_settings.EMAIL_HOST = 'mail.example.com'
        mock_settings.EMAIL_PORT = 465
        mock_settings.EMAIL_USE_SSL = True
        result = health.check_smtp()
        self.assertEqual(result['status'], 'ok')
        mock_smtplib.SMTP_SSL.assert_called_once_with('mail.example.com', 465, timeout=health.SMTP_TIMEOUT)
        mock_smtplib.SMTP.assert_not_called()

    @patch('core.health.smtplib')
    @patch('core.health.settings')
    def test_returns_fail_when_unreachable(self, mock_settings, mock_smtplib):
        mock_settings.EMAIL_HOST = 'mail.example.com'
        mock_settings.EMAIL_PORT = 587
        mock_settings.EMAIL_USE_SSL = False
        mock_smtplib.SMTP.side_effect = Exception('timed out')
        result = health.check_smtp()
        self.assertEqual(result['status'], 'fail')
        self.assertIn('timed out', result['detail'])


class RequireMonitoringTokenTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(MONITORING_TOKEN=None)
    def test_returns_404_when_token_not_configured(self):
        request = self.factory.get('/healthz')
        response = health.require_monitoring_token(request)
        self.assertEqual(response.status_code, 404)

    @override_settings(MONITORING_TOKEN='secret')
    def test_returns_403_when_header_missing(self):
        request = self.factory.get('/healthz')
        response = health.require_monitoring_token(request)
        self.assertEqual(response.status_code, 403)

    @override_settings(MONITORING_TOKEN='secret')
    def test_returns_none_when_token_valid(self):
        request = self.factory.get('/healthz', HTTP_AUTHORIZATION='Bearer secret')
        response = health.require_monitoring_token(request)
        self.assertIsNone(response)


@override_settings(MONITORING_TOKEN='secret')
class HealthzViewTests(SimpleTestCase):
    AUTH = {'HTTP_AUTHORIZATION': 'Bearer secret'}

    @patch('core.health.check_smtp')
    @patch('core.health.check_redis')
    @patch('core.health.check_database')
    def test_all_ok_returns_200_ok(self, mock_db, mock_redis, mock_smtp):
        mock_db.return_value = {'status': 'ok', 'detail': 'd'}
        mock_redis.return_value = {'status': 'ok', 'detail': 'r'}
        mock_smtp.return_value = {'status': 'ok', 'detail': 's'}
        response = self.client.get('/healthz', **self.AUTH)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('database', data['components'])
        self.assertIn('redis', data['components'])
        self.assertIn('smtp', data['components'])

    @patch('core.health.check_smtp')
    @patch('core.health.check_redis')
    @patch('core.health.check_database')
    def test_smtp_fail_returns_200_degraded(self, mock_db, mock_redis, mock_smtp):
        mock_db.return_value = {'status': 'ok', 'detail': 'd'}
        mock_redis.return_value = {'status': 'ok', 'detail': 'r'}
        mock_smtp.return_value = {'status': 'fail', 'detail': 'smtp down'}
        response = self.client.get('/healthz', **self.AUTH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'degraded')

    @patch('core.health.check_smtp')
    @patch('core.health.check_redis')
    @patch('core.health.check_database')
    def test_database_fail_returns_503_fail(self, mock_db, mock_redis, mock_smtp):
        mock_db.return_value = {'status': 'fail', 'detail': 'db down'}
        mock_redis.return_value = {'status': 'ok', 'detail': 'r'}
        mock_smtp.return_value = {'status': 'ok', 'detail': 's'}
        response = self.client.get('/healthz', **self.AUTH)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['status'], 'fail')

    @patch('core.health.check_smtp')
    @patch('core.health.check_redis')
    @patch('core.health.check_database')
    def test_redis_disabled_returns_200_ok(self, mock_db, mock_redis, mock_smtp):
        mock_db.return_value = {'status': 'ok', 'detail': 'd'}
        mock_redis.return_value = {'status': 'disabled', 'detail': 'Cache is disabled'}
        mock_smtp.return_value = {'status': 'ok', 'detail': 's'}
        response = self.client.get('/healthz', **self.AUTH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_bad_token_returns_403(self):
        response = self.client.get('/healthz', HTTP_AUTHORIZATION='Bearer wrong')
        self.assertEqual(response.status_code, 403)


@override_settings(MONITORING_TOKEN=None)
class HealthzViewDisabledTests(SimpleTestCase):
    def test_returns_404_when_token_not_configured(self):
        response = self.client.get('/healthz')
        self.assertEqual(response.status_code, 404)


class HealthLivenessViewTests(SimpleTestCase):
    def test_returns_200_ok_without_auth(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')
