# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from django_twilio_sms import views


urlpatterns = [
    url(
        r'^webhooks/callback-view/$', views.callback_view, name='callback_view'
    ),
    url(r'^webhooks/inbound-view/$', views.inbound_view, name='inbound_view'),
]
