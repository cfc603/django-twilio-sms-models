# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_twilio_sms', '0001_squashed_0005_auto_20160410_1948'),
    ]

    operations = [
        migrations.RenameField(
            model_name='phonenumber',
            old_name='twilio_number',
            new_name='unsubscribed',
        ),
    ]
