from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings, TestCase

from mock import patch

from django_twilio_sms.utils import AbsoluteURI


class AbsoluteURITest(TestCase):

    def test_init(self):
        namespace = 'test namespace'
        url_name = 'test url name'
        absolute_uri = AbsoluteURI(namespace, url_name)
        self.assertEqual(namespace, absolute_uri.namespace)
        self.assertEqual(url_name, absolute_uri.url_name)

    @override_settings(DJANGO_TWILIO_SMS_SITE_HOST='www.test.com')
    @override_settings(SECURE_SSL_REDIRECT=True)
    @patch('django_twilio_sms.utils.reverse')
    def test_get_absolute_uri(self, mock_reverse):
        mock_reverse.return_value = '/test/'
        absolute_uri = AbsoluteURI('test', 'test')
        self.assertEqual(
            'https://www.test.com/test/', absolute_uri.get_absolute_uri()
        )

    @override_settings(DJANGO_TWILIO_SMS_SITE_HOST='www.test.com')
    def test_get_host_no_exception(self):
        absolute_uri = AbsoluteURI('test', 'test')
        self.assertEqual('www.test.com', absolute_uri.get_host())

    @override_settings(DJANGO_TWILIO_SMS_SITE_HOST=None)
    def test_get_host_exception(self):
        del settings.DJANGO_TWILIO_SMS_SITE_HOST
        absolute_uri = AbsoluteURI('test', 'test')
        with self.assertRaises(ImproperlyConfigured):
            absolute_uri.get_host()

    @patch('django_twilio_sms.utils.reverse')
    def test_get_path(self, mock_reverse):
        absolute_uri = AbsoluteURI('test namespace', 'test url name')
        absolute_uri.get_path()
        mock_reverse.assert_called_with('test namespace:test url name')

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_get_scheme_if_secure_ssl_redirect(self):
        absolute_uri = AbsoluteURI('test', 'test')
        self.assertEqual('https', absolute_uri.get_scheme())

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_get_scheme_if_not_secure_ssl_redirect(self):
        absolute_uri = AbsoluteURI('test', 'test')
        self.assertEqual('http', absolute_uri.get_scheme())
