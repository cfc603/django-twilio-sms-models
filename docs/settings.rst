========
Settings
========

As this package relies on ``django-twilio`` be sure to checkout its settings as well at http://django-twilio.readthedocs.org/en/latest/settings.html


DJANGO_TWILIO_SMS_SITE_HOST (required)
--------------------------------------

``DJANGO_TWILIO_SMS_SITE_HOST`` is used in building the callback url sent with outbound messages which twilio will use to update the status of your message.

::

    # project/settings.py
    DJANGO_TWILIO_SMS_SITE_HOST = 'www.example.com'

Can also be used on your development machine with ``ngrok``::

    # project/settings.py
    DJANGO_TWILIO_SMS_SITE_HOST = 'unique-code.ngrok.io'

A secure url will be built when ``settings.SECURE_SSL_REDIRECT = True``.


DJANGO_TWILIO_SMS_MAX_RETRIES (optional)
----------------------------------------

Defaults to ``5``.

Used in conjuction with ``DJANGO_TWILIO_SMS_RETRY_SLEEP`` on ``djanago_twilio_sms.models.Message.twilio_message()``.


DJANGO_TWILIO_SMS_RESPONSES (optional)
--------------------------------------

The key, value pairs in ``DJANGO_TWILIO_SMS_RESPONSES`` are used for replies to inbound messages. The key is compared agains the inbound message and if matched, the value is sent as the reply.

::

    # project/settings.py
    DJANGO_TWILIO_SMS_RESPONSES = {
        'HELP': 'A very helpful message.',
        'UNKNOWN': 'Your messages can not be understood.',
    }

The 'UNKNOWN' key, value pair is required.

Run the sync_responses commands ``$ python manage.py sync_responses``.


DJANGO_TWILIO_SMS_RESPONSE_MESSAGE (optional)
---------------------------------------------

Set to ``True`` to enable responses to incoming messages. Will need to set responses through ``DJANGO_TWILIO_SMS_RESPONSES`` or through the admin interface.


DJANGO_TWILIO_SMS_RETRY_SLEEP (optional)
----------------------------------------

Defaults to ``.5``.

Used in conjuction with ``DJANGO_TWILIO_SMS_MAX_RETRIES`` on ``djanago_twilio_sms.models.Message.twilio_message()``.
