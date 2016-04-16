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
