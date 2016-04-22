=============================
django-twilio-sms-models
=============================

.. image:: https://badge.fury.io/py/django-twilio-sms-models.png
    :target: https://badge.fury.io/py/django-twilio-sms-models

.. image:: https://travis-ci.org/cfc603/django-twilio-sms-models.png?branch=master
    :target: https://travis-ci.org/cfc603/django-twilio-sms-models

.. image:: https://codecov.io/github/cfc603/django-twilio-sms-models/coverage.svg?branch=master
    :target: https://codecov.io/github/cfc603/django-twilio-sms-models?branch=master

Django models for Twilio's Programmable SMS

Documentation
-------------

The full documentation is at https://django-twilio-sms-models.readthedocs.org.

Quickstart
----------

Install django-twilio-sms-models::

    $ pip install django-twilio-sms-models

Follow django-twilio install instructions:

http://django-twilio.readthedocs.org/en/latest/install.html

Add 'django-twilio-sms' to your `INSTALLED_APPS`::

    # project/settings.py
    INSTALLED_APPS = (
        ...
        'django_twilio_sms',
    )

Set 'DJANGO_TWILIO_SMS_SITE_HOST' setting:

This is used to build an absolute URI for the callback url. Can also be used 
with ngrok on your development machine.

::

    # project/settings.py
    DJANGO_TWILIO_SMS_SITE_HOST = 'www.example.com'

Include django-twilio-sms URLconf in your project `urls.py`::

    url(r'^twilio-integration/', include('django_twilio_sms.urls', namespace='django_twilio_sms')),

Sync the database::

    $ python manage.py migrate

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
