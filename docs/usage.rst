========
Usage
========

Setup Response Messages
-----------------------

Django-twilio-sms-models can handle automated responses easily::

    #project/settings.py
    DJANGO_TWILIO_RESPONSE_MESSAGE = True

    DJANGO_TWILIO_SMS_RESPONSES = {
        'HELP': 'A very helpful reply.',
        'UNKNOWN': ('Your message is not understood. Please text HELP for ''
            'available commands.'),
        ...
    }

::

    $ python manage.py sync_responses

All inbound messages will be compared (case-insensitive) against the keys in DJANGO_TWILIO_SMS_RESPONSES and the values will be used as the response for matches. The 'UNKNOWN' key, value pair is required.


Setup Receiver
--------------

Response messages are great, but it would be better if you could call certain functions upon receiving certain "Actions" specified in ``DJANGO_TWILIO_SMS_RESPONSES``.

For example, let's say we have a 'STOP' Action in ``DJANGO_TWILIO_SMS_RESPONSES``::

    # project/settings.py
    DJANGO_TWILIO_RESPONSE_MESSAGE = True

    DJANGO_TWILIO_SMS_RESPONSES = {
        'STOP': ('You request to STOP receiving message has been received, '
            'and will processed immediately.'),
        'UNKNOWN': 'Unhelpful unknown message.',
        ...
    }

Run the ``sync_responses`` command::

    $ python manage.py sync_responses

In your app, we will call it ``awesome_app``::

    # awesome_app/receivers.py
    from django.dispatch import receiver

    from django_twilio_sms.signals import response_message

    @receiver(response_message)
    def process_stop_action(sender, **kwargs):
        # do something here, you have access to the originating Message object
        # as well as the Action object in the kwargs.
        action = kwargs.get('action')
        message = kwargs.get('sender')
        if action.name == 'STOP':
            unsubscribe_user(phone=message.from_phone_number)

If you haven't previously setup your AppConfig::

    # awesome_app/apps.py
    from django.apps import AppConfig
    from django.utils.translation import ugettext_lazy as _


    class AwesomeAppConfig(AppConfig):
        name = 'awesome_app'
        verbose_name = _("Awesome Application")

        def ready(self):
            import awesome_app.receivers


    # awesome_app/__init__.py
    default_app_config = 'awesome_app.apps.AwesomeAppConfig'


Send a message
--------------

::

    from django.conf import settings

    from django_twilio_sms.models import Message


    message = send_message(
        body="Hey, I'm texting from Twilio!",
        to="+19999999999",
        from_=settings.TWILIO_DEFAULT_CALLERID, # this is the default
    )
