# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from django_twilio.decorators import twilio_view
from django_twilio.request import decompose
from twilio import twiml

from .models import Message


@twilio_view
def callback_view(request):
    response = twiml.Response()
    twilio_request = decompose(request)

    message_view(twilio_request)

    return response


@twilio_view
def inbound_view(request):
    response = twiml.Response()
    twilio_request = decompose(request)

    if twilio_request.type == 'message':
        message_obj = message_view(twilio_request)
        if (getattr(settings, 'DJANGO_TWILIO_SMS_RESPONSE_MESSAGE', False) or
                getattr(settings, 'DJANGO_TWILIO_RESPONSE_MESSAGE', False)):
            message_obj.send_response_message()
    else:
        response = voice_view(response)

    return response


def message_view(twilio_request):
    message_obj, created = Message.get_or_create(twilio_request.messagesid)
    if not created:
        message_obj.sync_twilio_message()

    return message_obj


def voice_view(response):
    response.reject()
    return response
