# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse


class AbsoluteURI(object):

    def __init__(self, namespace, url_name):
        self.namespace = namespace
        self.url_name = url_name

    def get_absolute_uri(self):
        return '{scheme}://{host}{path}'.format(
            scheme=self.get_scheme(),
            host=self.get_host(),
            path=self.get_path()
        )

    def get_host(self):
        try:
            return settings.DJANGO_TWILIO_SMS_SITE_HOST
        except AttributeError:
            message = 'DJANGO_TWILIO_SMS_SITE_HOST must be set.'
            raise ImproperlyConfigured(message)

    def get_path(self):
        return reverse('{namespace}:{url_name}'.format(
            namespace=self.namespace, url_name=self.url_name
        ))

    def get_scheme(self):
        if settings.SECURE_SSL_REDIRECT:
            return 'https'
        else:
            return 'http'
