# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from django_twilio.client import twilio_client
from django_twilio.models import Caller
from twilio.rest.exceptions import TwilioRestException

from .signals import response_message, unsubscribe_signal
from .utils import AbsoluteURI


# Abstract Models
class CreatedUpdated(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Sid(CreatedUpdated):
    sid = models.CharField(max_length=34, primary_key=True)

    def __str__(self):
        return '{}'.format(self.sid)

    class Meta:
        abstract = True


# Message Model ForeignKeys
class Account(Sid):

    # account type choices
    TRIAL = 0
    FULL = 1

    ACCOUNT_TYPE_CHOICES = (
        (TRIAL, 'Trial'),
        (FULL, 'Full'),
    )

    # status choices
    ACTIVE = 0
    SUSPENDED = 1
    CLOSED = 2

    STATUS_CHOICES = (
        (ACTIVE, 'active'),
        (SUSPENDED, 'suspended'),
        (CLOSED, 'closed'),
    )

    friendly_name = models.CharField(max_length=64)
    account_type = models.PositiveSmallIntegerField(
        choices=ACCOUNT_TYPE_CHOICES
    )
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    owner_account_sid = models.ForeignKey('self', null=True)

    @classmethod
    def get_account_type_choice(cls, account_type_display):
        for choice in cls.ACCOUNT_TYPE_CHOICES:
            if account_type_display == choice[1]:
                return choice[0]

    @classmethod
    def get_status_choice(cls, status_display):
        for choice in cls.STATUS_CHOICES:
            if status_display == choice[1]:
                return choice[0]

    @classmethod
    def get_or_create(cls, account_sid=None, account=None):
        if not account_sid:
            account_sid = account.sid

        try:
            return cls.objects.get(sid=account_sid)
        except cls.DoesNotExist:
            account_obj = cls(sid=account_sid)
            account_obj.sync_twilio_account(account)
            return account_obj

    @property
    def twilio_account(self):
        return twilio_client.accounts.get(self.sid)

    def sync_twilio_account(self, account=None):
        if not account:
            account = self.twilio_account

        self.friendly_name = account.friendly_name
        self.account_type = self.get_account_type_choice(account.type)
        self.status = self.get_status_choice(account.status)
        if account.sid != account.owner_account_sid:
            self.owner_account_sid = Account.get_or_create(
                account.owner_account_sid
            )
        self.save()


@python_2_unicode_compatible
class ApiVersion(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return '{}'.format(self.date)

    @classmethod
    def get_or_create(cls, message_date):
        api_version, created = cls.objects.get_or_create(
            date=message_date
        )
        return api_version


@python_2_unicode_compatible
class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return '{}'.format(self.code)

    @classmethod
    def get_or_create(cls, message_price_unit):
        currency, created = cls.objects.get_or_create(code=message_price_unit)
        return currency


@python_2_unicode_compatible
class Error(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    message = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.code)

    @classmethod
    def get_or_create(cls, message_error_code, message_error_message):
        error, created = cls.objects.get_or_create(
            code=message_error_code,
            defaults={'message': message_error_message}
        )
        return error


class MessagingService(Sid):
    pass

    @classmethod
    def get_or_create(cls, messaging_service_sid):
        messaging_service, created = cls.objects.get_or_create(
            sid=messaging_service_sid
        )
        return messaging_service


@python_2_unicode_compatible
class PhoneNumber(CreatedUpdated):
    caller = models.OneToOneField(Caller)
    unsubscribed = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.caller.phone_number)

    @classmethod
    def get_or_create(cls, phone_number, unsubscribed=False):
        if isinstance(phone_number, cls):
            return phone_number

        caller, created = Caller.objects.get_or_create(
            phone_number=phone_number
        )
        phone_number_obj, create = cls.objects.get_or_create(
            caller=caller, defaults={'unsubscribed': unsubscribed}
        )

        return phone_number_obj

    @property
    def as_e164(self):
        return self.caller.phone_number.as_e164

    def subscribe(self):
        self.unsubscribed = False
        self.save()

    def unsubscribe(self):
        self.unsubscribed = True
        self.save()


class Message(Sid):

    # status choices
    ACCEPTED = 0
    QUEUED = 1
    SENDING = 2
    SENT = 3
    RECEIVING = 4
    RECEIVED = 5
    DELIVERED = 6
    UNDELIVERED = 7
    FAILED = 8
    UNKNOWN = 9

    STATUS_CHOICES = (
        (ACCEPTED, 'accepted'),
        (QUEUED, 'queued'),
        (SENDING, 'sending'),
        (SENT, 'sent'),
        (RECEIVING, 'receiving'),
        (RECEIVED, 'received'),
        (DELIVERED, 'delivered'),
        (UNDELIVERED, 'undelivered'),
        (FAILED, 'failed'),
    )

    # direction choices
    INBOUND = 0
    OUTBOUND_API = 1
    OUTBOUND_CALL = 2
    OUTBOUND_REPLY = 3

    DIRECTION_CHOICES = (
        (INBOUND, 'inbound'),
        (OUTBOUND_API, 'outbound-api'),
        (OUTBOUND_CALL, 'outbound-call'),
        (OUTBOUND_REPLY, 'outbound-reply'),
    )

    UNSUBSCRIBE_MESSAGES = [
        'STOP', 'STOPALL', 'UNSUBSCRIBE', 'CANCEL', 'END', 'QUIT'
    ]

    SUBSCRIBE_MESSAGES = ['START', 'YES']

    date_sent = models.DateTimeField(null=True)
    account = models.ForeignKey(Account)
    messaging_service = models.ForeignKey(MessagingService, null=True)
    from_phone_number = models.ForeignKey(PhoneNumber, related_name='to_phone')
    to_phone_number = models.ForeignKey(PhoneNumber, related_name='from_phone')
    body = models.CharField(max_length=160)
    num_media = models.PositiveSmallIntegerField()
    num_segments = models.PositiveSmallIntegerField()
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=QUEUED
    )
    error = models.ForeignKey(Error, null=True, related_name='error')
    direction = models.PositiveSmallIntegerField(choices=DIRECTION_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=5)
    currency = models.ForeignKey(Currency)
    api_version = models.ForeignKey(ApiVersion)

    @classmethod
    def get_direction_choice(cls, direction_display):
        for choice in cls.DIRECTION_CHOICES:
            if direction_display == choice[1]:
                return choice[0]

    @classmethod
    def get_status_choice(cls, status_display):
        for choice in cls.STATUS_CHOICES:
            if status_display == choice[1]:
                return choice[0]

    @classmethod
    def get_or_create(cls, message_sid=None, message=None):
        if not message_sid:
            message_sid = message.sid

        try:
            return (cls.objects.get(sid=message_sid), False)
        except cls.DoesNotExist:
            message_obj = cls(sid=message_sid)
            message_obj.sync_twilio_message(message)
            return (message_obj, True)

    @classmethod
    def send_message(cls, body, to, from_=settings.TWILIO_DEFAULT_CALLERID):
        to_phone_number = PhoneNumber.get_or_create(to)
        from_phone_number = PhoneNumber.get_or_create(from_)

        twilio_message = twilio_client.messages.create(
            body=body,
            to=to_phone_number.as_e164,
            from_=from_phone_number.as_e164,
            status_callback=cls.get_status_callback()
        )

        return cls.get_or_create(message=twilio_message)

    @property
    def twilio_message(self):
        max_retries = getattr(settings, 'DJANGO_TWILIO_SMS_MAX_RETRIES', 5)
        retry_sleep = getattr(settings, 'DJANGO_TWILIO_SMS_RETRY_SLEEP', .5)
        retries = 0
        while True:
            try:
                return twilio_client.messages.get(self.sid)
            except TwilioRestException:
                if retries < max_retries:
                    time.sleep(retry_sleep)
                    retries = retries + 1
                else:
                    raise

    @staticmethod
    def get_status_callback():
        absolute_uri = AbsoluteURI('django_twilio_sms', 'callback_view')
        return absolute_uri.get_absolute_uri()

    def check_for_subscription_message(self):
        if self.direction is self.INBOUND:
            body = self.body.upper().strip()

            if body in self.UNSUBSCRIBE_MESSAGES:
                self.from_phone_number.unsubscribe()

                unsubscribe_signal.send_robust(
                    sender=self.__class__, message=self, unsubscribed=True
                )

            elif body in self.SUBSCRIBE_MESSAGES:
                self.from_phone_number.subscribe()

                unsubscribe_signal.send_robust(
                    sender=self.__class__, message=self, unsubscribed=False
                )

    def send_response_message(self):
        if self.direction is self.INBOUND:
            if not self.from_phone_number.unsubscribed:
                action = Action.get_action(self.body)
                Message.send_message(
                    body=action.get_active_response().body,
                    to=self.from_phone_number,
                    from_=self.to_phone_number
                )
                response_message.send_robust(
                    sender=self.__class__, action=action, message=self
                )

    def sync_twilio_message(self, message=None):
        if not message:
            message = self.twilio_message

        self.date_sent = message.date_sent
        self.account = Account.get_or_create(message.account_sid)

        if message.messaging_service_sid:
            self.messaging_service = MessagingService.get_or_create(
                message.messaging_service_sid
            )

        self.num_media = message.num_media
        self.num_segments = message.num_segments

        if message.status:
            self.status = self.get_status_choice(message.status)
        else:
            self.status = self.UNKNOWN

        if message.error_code:
            self.error = Error.get_or_create(
                message.error_code, message.error_message
            )

        self.direction = self.get_direction_choice(message.direction)
        self.price = message.price or '0.0'
        self.currency = Currency.get_or_create(message.price_unit)
        self.api_version = ApiVersion.get_or_create(message.api_version)

        self.from_phone_number = PhoneNumber.get_or_create(message.from_)
        self.to_phone_number = PhoneNumber.get_or_create(message.to)

        self.body = message.body
        self.check_for_subscription_message()

        self.save()


@python_2_unicode_compatible
class Action(CreatedUpdated):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.name)

    @classmethod
    def get_action(cls, message_body):
        try:
            return cls.objects.get(
                name=message_body.strip().upper(), active=True
            )
        except cls.DoesNotExist:
            return cls.objects.get(name='UNKNOWN', active=True)

    def get_active_response(self):
        return self.response_set.filter(active=True)[0]

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(Action, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Response(CreatedUpdated):
    body = models.CharField(max_length=160)
    action = models.ForeignKey(Action)
    active = models.BooleanField(default=True)

    def __str__(self):
        return 'Response for {}'.format(self.action)

    def save(self, *args, **kwargs):
        if self.active:
            try:
                current = Response.objects.get(action=self.action, active=True)
                if self != current:
                    current.active = False
                    current.save()
            except Response.DoesNotExist:
                pass
        super(Response, self).save(*args, **kwargs)
