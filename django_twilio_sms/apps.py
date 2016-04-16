from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoTwilioSmsConfig(AppConfig):
    name = 'django_twilio_sms'
    verbose_name = _("Django Twilio SMS")
