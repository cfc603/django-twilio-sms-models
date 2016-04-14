# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [(b'django_twilio_sms', '0001_initial'), (b'django_twilio_sms', '0002_auto_20160402_1521'), (b'django_twilio_sms', '0003_auto_20160403_1914'), (b'django_twilio_sms', '0004_auto_20160410_1925'), (b'django_twilio_sms', '0005_auto_20160410_1948')]

    dependencies = [
        ('django_twilio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('sid', models.CharField(max_length=34, serialize=False, primary_key=True)),
                ('friendly_name', models.CharField(max_length=64)),
                ('account_type', models.PositiveSmallIntegerField(choices=[(0, b'Trial'), (1, b'Full')])),
                ('status', models.PositiveSmallIntegerField(choices=[(0, b'active'), (1, b'suspended'), (2, b'closed')])),
                ('owner_account_sid', models.ForeignKey(to='django_twilio_sms.Account', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApiVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('code', models.CharField(max_length=3, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('code', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('message', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('sid', models.CharField(max_length=34, serialize=False, primary_key=True)),
                ('date_sent', models.DateTimeField()),
                ('body', models.CharField(max_length=160)),
                ('num_media', models.PositiveSmallIntegerField()),
                ('num_segments', models.PositiveSmallIntegerField()),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(0, b'accepted'), (1, b'queued'), (2, b'sending'), (3, b'sent'), (4, b'receiving'), (6, b'delivered'), (7, b'undelivered'), (8, b'failed')])),
                ('direction', models.PositiveSmallIntegerField(choices=[(0, b'inbound'), (1, b'outbound-api'), (2, b'outbound-call'), (3, b'outbound-reply')])),
                ('price', models.DecimalField(max_digits=6, decimal_places=5)),
                ('account', models.ForeignKey(to='django_twilio_sms.Account')),
                ('api_version', models.ForeignKey(to='django_twilio_sms.ApiVersion')),
                ('currency', models.ForeignKey(to='django_twilio_sms.Currency')),
                ('error', models.ForeignKey(related_name='error', to='django_twilio_sms.Error', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MessagingService',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('sid', models.CharField(max_length=34, serialize=False, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('twilio_number', models.BooleanField(default=False)),
                ('caller', models.OneToOneField(to='django_twilio.Caller')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='message',
            name='from_phone_number',
            field=models.ForeignKey(related_name='to_phone', to='django_twilio_sms.PhoneNumber'),
        ),
        migrations.AddField(
            model_name='message',
            name='messaging_service',
            field=models.ForeignKey(to='django_twilio_sms.MessagingService', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='to_phone_number',
            field=models.ForeignKey(related_name='from_phone', to='django_twilio_sms.PhoneNumber'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date_sent',
            field=models.DateTimeField(null=True),
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('body', models.CharField(max_length=160)),
                ('active', models.BooleanField(default=True)),
                ('action', models.ForeignKey(to='django_twilio_sms.Action')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, b'accepted'), (1, b'queued'), (2, b'sending'), (3, b'sent'), (4, b'receiving'), (5, b'received'), (6, b'delivered'), (7, b'undelivered'), (8, b'failed')]),
        ),
        migrations.AlterField(
            model_name='action',
            name='name',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
