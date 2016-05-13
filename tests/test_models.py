import datetime

from django.test import override_settings, TestCase

from django_twilio.models import Caller
from mock import Mock, patch, PropertyMock
from model_mommy import mommy
from twilio.rest.exceptions import TwilioRestException

from .mommy_recipes import caller_recipe, message_recipe, phone_number_recipe
from django_twilio_sms.models import (
    Account,
    Action,
    ApiVersion,
    Currency,
    Error,
    Message,
    MessagingService,
    PhoneNumber,
    Response
)


class CommonTestCase(TestCase):

    def string_test(self, model, test_value, **kwargs):
        obj = mommy.make('django_twilio_sms.'+model, **kwargs)
        self.assertEqual(test_value, obj.__str__())


class AccountModelTest(CommonTestCase):

    def mock_account(self, owner_account_sid='test'):
        return Mock(
            friendly_name='test',
            type='Full',
            status='active',
            sid='test',
            owner_account_sid=owner_account_sid,
        )

    def test_unicode(self):
        self.string_test('Account', 'abc', **{'sid': 'abc'})

    def test_get_account_type_choice_account_type_display_equal_choice(self):
        self.assertEqual(0, Account.get_account_type_choice('Trial'))

    def test_get_account_type_choice_account_type_display_not_equal_choice(
            self):
        self.assertEqual(None, Account.get_account_type_choice('test'))

    def test_get_status_choice_status_display_equal_choice(self):
        self.assertEqual(0, Account.get_status_choice('active'))

    def test_get_status_choice_status_display_not_equal_choice(self):
        self.assertEqual(None, Account.get_status_choice('test'))

    def test_get_or_create_if_not_account_sid_no_exception(self):
        account_1 = mommy.make(Account, sid='test')
        account_2 = Account.get_or_create(account=self.mock_account())
        self.assertEqual(1, Account.objects.all().count())
        self.assertEqual(account_1, account_2)

    def test_get_or_create_if_account_sid_no_exception(self):
        account_1 = mommy.make(Account, sid='test')
        account_2 = Account.get_or_create(account_sid='test')
        self.assertEqual(1, Account.objects.all().count())
        self.assertEqual(account_1, account_2)

    def test_get_or_create_if_not_account_sid_with_exception(self):
        Account.get_or_create(account=self.mock_account())
        self.assertEqual(1, Account.objects.all().count())
        self.assertEqual('test', Account.objects.first().sid)

    @patch(
        'django_twilio_sms.models.Account.twilio_account',
        new_callable=PropertyMock
        )
    def test_get_or_create_if_account_sid_with_exception(self, twilio_account):
        twilio_account.return_value = self.mock_account()
        Account.get_or_create(account_sid='test')
        self.assertEqual(1, Account.objects.all().count())
        self.assertEqual('test', Account.objects.first().sid)

    @patch(
        'django_twilio_sms.models.Account.twilio_account',
        new_callable=PropertyMock
        )
    def test_twilio_account(self, twilio_account):
        mock_account = self.mock_account()
        twilio_account.return_value = mock_account
        self.assertEqual(mock_account, Account.twilio_account)

    @patch(
        'django_twilio_sms.models.Account.twilio_account',
        new_callable=PropertyMock
        )
    def test_sync_twilio_account_if_not_account_sids_not_equal(
            self, twilio_account):
        twilio_account.return_value = self.mock_account()
        account = mommy.make(Account, sid='test')
        account.sync_twilio_account()
        self.assertEqual('test', account.friendly_name)
        self.assertEqual(Account.FULL, account.account_type)
        self.assertEqual(Account.ACTIVE, account.status)
        self.assertEqual(None, account.owner_account_sid)

    def test_sync_twilio_account_if_account_sids_not_equal(self):
        account = mommy.make(Account, sid='test')
        account.sync_twilio_account(self.mock_account())
        self.assertEqual('test', account.friendly_name)
        self.assertEqual(Account.FULL, account.account_type)
        self.assertEqual(Account.ACTIVE, account.status)
        self.assertEqual(None, account.owner_account_sid)

    def test_sync_twilio_account_if_account_sids_equal(self):
        owner_account = mommy.make(Account, sid='ownertest')
        account = mommy.make(Account, sid='test')
        account.sync_twilio_account(self.mock_account('ownertest'))
        self.assertEqual('test', account.friendly_name)
        self.assertEqual(Account.FULL, account.account_type)
        self.assertEqual(Account.ACTIVE, account.status)
        self.assertEqual(owner_account, account.owner_account_sid)


class ApiVersionModelTest(CommonTestCase):

    def test_unicode(self):
        api_version = mommy.make(ApiVersion)
        self.assertEqual(
            '{}'.format(api_version.date), api_version.__str__()
        )

    def test_get_or_create_created_false(self):
        api_version = mommy.make(ApiVersion)
        self.assertEqual(
            api_version, ApiVersion.get_or_create(api_version.date)
        )
        self.assertEqual(1, ApiVersion.objects.all().count())

    def test_get_or_create_created_true(self):
        date = datetime.date(2016, 1, 1)
        api_version = ApiVersion.get_or_create(date)
        self.assertEqual(date, api_version.date)
        self.assertEqual(1, ApiVersion.objects.all().count())


class CurrencyModelTest(CommonTestCase):

    def test_unicode(self):
        self.string_test('Currency', 'abc', **{'code': 'abc'})

    def test_get_or_create_created_false(self):
        currency = mommy.make(Currency)
        self.assertEqual(currency, Currency.get_or_create(currency.code))
        self.assertEqual(1, Currency.objects.all().count())

    def test_get_or_create_created_true(self):
        currency_code = 'USD'
        currency = Currency.get_or_create(currency_code)
        self.assertEqual(currency_code, currency.code)
        self.assertEqual(1, Currency.objects.all().count())


class ErrorModelTest(CommonTestCase):

    def test_unicode(self):
        self.string_test('Error', 'abc', **{'code': 'abc'})

    def test_get_or_create_created_false(self):
        error = mommy.make(Error)
        self.assertEqual(error, Error.get_or_create(error.code, error.message))
        self.assertEqual(1, Error.objects.all().count())

    def get_or_create_created_true(self):
        error_code = '10015'
        error_message = 'test'
        error = Error.get_or_create(error_code, error_message)
        self.assertEqual(error_code, error.code)
        self.assertEqual(error_message, error.message)
        self.assertEqual(1, Error.objects.all().count())


class MessageServiceModelTest(CommonTestCase):

    def test_unicode(self):
        self.string_test('MessagingService', 'abc', **{'sid': 'abc'})

    def test_get_or_create_created_false(self):
        messaging_service = mommy.make(MessagingService)
        self.assertEqual(
            messaging_service, MessagingService.get_or_create(
                messaging_service.sid
            )
        )
        self.assertEqual(1, MessagingService.objects.all().count())

    def test_get_or_create_created_true(self):
        sid = 'test'
        messaging_service = MessagingService.get_or_create(sid)
        self.assertEqual(sid, messaging_service.sid)
        self.assertEqual(1, MessagingService.objects.all().count())


class PhoneNumberModelTest(CommonTestCase):

    def test_unicode(self):
        caller = caller_recipe.make()
        self.string_test(
            'PhoneNumber', '+19999999991', **{'caller': caller}
        )

    def test_get_or_create_is_instance(self):
        phone_number = phone_number_recipe.make()
        self.assertEqual(phone_number, PhoneNumber.get_or_create(phone_number))

    def test_get_or_create_caller_created_false_phone_number_created_false(
            self):
        caller = caller_recipe.make()
        phone_number = phone_number_recipe.make(caller=caller)
        self.assertEqual(
            phone_number, PhoneNumber.get_or_create(caller.phone_number)
        )
        self.assertEqual(1, Caller.objects.all().count())
        self.assertEqual(1, PhoneNumber.objects.all().count())

    def test_get_or_create_caller_created_true_phone_number_created_true(self):
        number = '+19999999999'
        phone_number = PhoneNumber.get_or_create(number)
        self.assertEqual(number, phone_number.caller.phone_number)
        self.assertEqual(1, Caller.objects.all().count())
        self.assertEqual(1, PhoneNumber.objects.all().count())

    def test_as_164(self):
        phone_number = phone_number_recipe.make()
        self.assertEqual('+19999999991', phone_number.as_e164)

    def test_subscribe(self):
        phone_number = phone_number_recipe.make(unsubscribed=True)
        phone_number.subscribe()
        self.assertFalse(phone_number.unsubscribed)

    def test_unsubscribe(self):
        phone_number = phone_number_recipe.make(unsubscribed=False)
        phone_number.unsubscribe()
        self.assertTrue(phone_number.unsubscribed)


class MessageModelTest(CommonTestCase):

    def mock_message(
            self, messaging_service_sid=None, error=None, direction='inbound',
            status='accepted', price='-0.00750'):
        account = mommy.make(Account, sid='testaccount')

        if error:
            error_code = error.code
            error_message = error.message
        else:
            error_code = None
            error_message = None

        return Mock(
            sid='test',
            date_sent=datetime.date(2016, 1, 1),
            account_sid=account.sid,
            messaging_service_sid=messaging_service_sid,
            body='test',
            num_media=0,
            num_segments=1,
            status=status,
            error_code=error_code,
            error_message=error_message,
            direction=direction,
            price=price,
            price_unit='USD',
            api_version='2016-01-01',
            from_='+19999999991',
            to='+19999999992',
        )

    def test_unicode(self):
        self.string_test(
            'Message', '123', **{
                'sid': '123',
                'from_phone_number': phone_number_recipe.make(),
                'to_phone_number': phone_number_recipe.make(),
            }
        )

    def test_get_direction_choice_direction_display_equal_choice(self):
        self.assertEqual(
            Message.INBOUND, Message.get_direction_choice('inbound')
        )

    def test_get_direction_choice_direction_display_not_equal_choice(self):
        self.assertEqual(None, Message.get_direction_choice('test'))

    def test_get_status_choice_status_display_equal_choice(self):
        self.assertEqual(
            Message.ACCEPTED, Message.get_status_choice('accepted')
        )

    def test_get_status_choice_status_display_not_equal_choice(self):
        self.assertEqual(None, Message.get_status_choice('test'))

    def test_get_or_create_if_not_message_sid_no_exception(self):
        message_1 = message_recipe.make(sid='test')
        message_2, created = Message.get_or_create(message=Mock(sid='test'))
        self.assertFalse(created)
        self.assertEqual(message_1, message_2)
        self.assertEqual(1, Message.objects.all().count())

    def test_get_or_create_if_message_sid_no_exception(self):
        message_1 = message_recipe.make(sid='test')
        message_2, created = Message.get_or_create(message_sid='test')
        self.assertFalse(created)
        self.assertEqual(message_1, message_2)
        self.assertEqual(1, Message.objects.all().count())

    def test_get_or_create_if_not_message_sid_with_exception(self):
        message, created = Message.get_or_create(message=self.mock_message())
        self.assertTrue(created)
        self.assertEqual(message, Message.objects.first())
        self.assertEqual(1, Message.objects.all().count())

    @patch(
        'django_twilio_sms.models.Message.twilio_message',
        new_callable=PropertyMock
        )
    def test_get_or_create_if_message_sid_with_exception(self, twilio_message):
        twilio_message.return_value = self.mock_message()
        message, created = Message.get_or_create('test')
        self.assertTrue(created)
        self.assertEqual(message, Message.objects.first())
        self.assertEqual(1, Message.objects.all().count())

    @patch('django_twilio_sms.models.Message.get_status_callback')
    @patch('django_twilio_sms.models.twilio_client')
    def test_send_message(self, mock_client, mock_status_callback):
        mock_client.messages.create.return_value = self.mock_message()
        mock_status_callback.return_value = 'test'

        message, created = Message.send_message(
            body='test', to='+19999999992', from_='+19999999991'
        )

        self.assertIsInstance(message, Message)
        self.assertTrue(mock_status_callback.called)
        mock_client.messages.create.assert_called_with(
            body='test',
            to='+19999999992',
            from_='+19999999991',
            status_callback='test'
        )

    @patch('django_twilio_sms.models.twilio_client')
    def test_twilio_message_no_exception(self, mock_client):
        mock_message = self.mock_message()
        mock_client.messages.get.return_value = mock_message
        message = message_recipe.make(sid='test')
        self.assertEqual(mock_message, message.twilio_message)
        self.assertEqual(1, mock_client.messages.get.call_count)

    @override_settings(DJANGO_TWILIO_SMS_MAX_RETRIES=2)
    @override_settings(DJANGO_TWILIO_SMS_RETRY_SLEEP=.001)
    @patch('django_twilio_sms.models.twilio_client')
    def test_twilio_message_with_exception_less_than_five(self, mock_client):
        mock_client.messages.get.side_effect = TwilioRestException(
            status='test', method='test', uri='test', msg='test', code='test'
        )
        message = message_recipe.make(sid='test')
        with self.assertRaises(TwilioRestException):
            message.twilio_message
        self.assertEqual(3, mock_client.messages.get.call_count)

    @override_settings(DJANGO_TWILIO_SMS_SITE_HOST='www.test.com')
    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_get_status_callback(self):
        self.assertEqual(
            Message.get_status_callback(),
            'https://www.test.com/twilio-integration/webhooks/callback-view/'
        )

    @patch('django_twilio_sms.models.unsubscribe_signal')
    def test_check_for_subscription_message_if_direction_is_not_inbound(
            self, unsubscribe_signal):
        from_phone_number = phone_number_recipe.make(unsubscribed=False)
        message = message_recipe.make(
            body='STOP',
            from_phone_number=from_phone_number,
            direction=Message.OUTBOUND_API
        )
        message.check_for_subscription_message()
        self.assertFalse(message.from_phone_number.unsubscribed)
        unsubscribe_signal.send_robust.assert_not_called()

    @patch('django_twilio_sms.models.unsubscribe_signal')
    def test_check_for_subscription_message_if_body_in_unsubscribe(
            self, unsubscribe_signal):
        from_phone_number = phone_number_recipe.make(unsubscribed=False)
        message = message_recipe.make(
            body='STOP',
            from_phone_number=from_phone_number,
            direction=Message.INBOUND
        )
        message.check_for_subscription_message()
        self.assertTrue(message.from_phone_number.unsubscribed)
        unsubscribe_signal.send_robust.assert_called_once_with(
            sender=Message, message=message, unsubscribed=True
        )

    def test_check_for_subscription_message_if_body_in_subscribe(self):
        from_phone_number = phone_number_recipe.make(unsubscribed=True)
        message = message_recipe.make(
            body='START',
            from_phone_number=from_phone_number,
            direction=Message.INBOUND
        )
        message.check_for_subscription_message()
        self.assertFalse(message.from_phone_number.unsubscribed)

    @patch('django_twilio_sms.models.response_message')
    @patch('django_twilio_sms.models.Message.send_message')
    def test_send_response_message_if_direction_is_inbound_not_unsubscribed(
            self, send_message, response_message):
        action = mommy.make(Action, name='STOP')
        mommy.make(Response, body='test', action=action)
        to_phone_number = phone_number_recipe.make()
        from_phone_number = phone_number_recipe.make(unsubscribed=False)
        message = message_recipe.make(
            body='STOP',
            direction=Message.INBOUND,
            to_phone_number=to_phone_number,
            from_phone_number=from_phone_number
        )
        message.send_response_message()
        send_message.assert_called_with(
            body='test',
            to=from_phone_number,
            from_=to_phone_number
        )
        response_message.send_robust.assert_called_with(
            sender=Message, action=action, message=message
        )

    @patch('django_twilio_sms.models.response_message')
    @patch('django_twilio_sms.models.Message.send_message')
    def test_send_response_message_if_direction_is_inbound_is_unsubscribed(
            self, send_message, response_message):
        action = mommy.make(Action, name='STOP')
        mommy.make(Response, body='test', action=action)
        to_phone_number = phone_number_recipe.make()
        from_phone_number = phone_number_recipe.make(unsubscribed=True)
        message = message_recipe.make(
            body='STOP',
            direction=Message.INBOUND,
            to_phone_number=to_phone_number,
            from_phone_number=from_phone_number
        )
        message.send_response_message()
        send_message.assert_not_called()
        response_message.assert_not_called()

    @patch('django_twilio_sms.models.response_message')
    @patch('django_twilio_sms.models.Message.send_message')
    def test_send_response_message_if_direction_not_inbound(
            self, send_message, response_message):
        action = mommy.make(Action, name='STOP')
        mommy.make(Response, body='test', action=action)
        to_phone_number = phone_number_recipe.make()
        from_phone_number = phone_number_recipe.make()
        message = message_recipe.make(
            body='STOP',
            direction=Message.OUTBOUND_API,
            to_phone_number=to_phone_number,
            from_phone_number=from_phone_number
        )
        message.send_response_message()
        send_message.assert_not_called()
        response_message.assert_not_called()

    @patch('django_twilio_sms.models.Message.check_for_subscription_message')
    def test_sync_twilio_message_if_message(
            self, check_for_subscription_message):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message())
        self.assertEqual(datetime.date(2016, 1, 1), message.date_sent)
        self.assertEqual('testaccount', message.account.sid)
        self.assertEqual('test', message.body)
        self.assertEqual(0, message.num_media)
        self.assertEqual(1, message.num_segments)
        self.assertEqual(Message.ACCEPTED, message.status)
        self.assertEqual(Message.INBOUND, message.direction)
        self.assertEqual('-0.00750', message.price)
        self.assertEqual('USD', message.currency.code)
        self.assertEqual('2016-01-01', message.api_version.date)
        self.assertEqual(
            '+19999999991', message.from_phone_number.caller.phone_number
        )
        self.assertEqual(
            '+19999999992', message.to_phone_number.caller.phone_number
        )
        check_for_subscription_message.assert_called_once()

    @patch('django_twilio_sms.models.Message.check_for_subscription_message')
    @patch(
        'django_twilio_sms.models.Message.twilio_message',
        new_callable=PropertyMock
        )
    def test_sync_twilio_message_if_not_message(
            self, twilio_message, check_for_subscription_message):
        twilio_message.return_value = self.mock_message()
        message = message_recipe.make()
        message.sync_twilio_message()
        self.assertEqual(datetime.date(2016, 1, 1), message.date_sent)
        self.assertEqual('testaccount', message.account.sid)
        self.assertEqual('test', message.body)
        self.assertEqual(0, message.num_media)
        self.assertEqual(1, message.num_segments)
        self.assertEqual(Message.ACCEPTED, message.status)
        self.assertEqual(Message.INBOUND, message.direction)
        self.assertEqual('-0.00750', message.price)
        self.assertEqual('USD', message.currency.code)
        self.assertEqual('2016-01-01', message.api_version.date)
        self.assertEqual(
            '+19999999991', message.from_phone_number.caller.phone_number
        )
        self.assertEqual(
            '+19999999992', message.to_phone_number.caller.phone_number
        )
        check_for_subscription_message.assert_called_once()

    def test_sync_twilio_message_if_message_service_sid(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message(
            messaging_service_sid='test')
        )
        self.assertEqual(1, MessagingService.objects.all().count())
        self.assertEqual(
            message.messaging_service, MessagingService.objects.first()
        )

    def test_sync_twilio_message_if_not_message_service_sid(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message())
        self.assertEqual(0, MessagingService.objects.all().count())
        self.assertEqual(message.messaging_service, None)

    def test_sync_twilio_message_if_status(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message())
        self.assertEqual(0, message.status)

    def test_sync_twilio_message_if_not_status(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message(status=None))
        self.assertEqual(9, message.status)

    def test_sync_twilio_message_if_error_code(self):
        message = message_recipe.make()
        error = mommy.make(Error)
        message.sync_twilio_message(self.mock_message(error=error))
        self.assertEqual(error, message.error)

    def test_sync_twilio_message_if_not_error_code(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message())
        self.assertEqual(0, Error.objects.all().count())
        self.assertEqual(None, message.error)

    def test_sync_twilio_message_if_price(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message())
        self.assertEqual('-0.00750', message.price)

    def test_sync_twilio_message_if_not_price(self):
        message = message_recipe.make()
        message.sync_twilio_message(self.mock_message(price=None))
        self.assertEqual('0.0', message.price)


class ActionModelTest(CommonTestCase):

    def test_unicode(self):
        self.string_test('Action', 'ABC', **{'name': 'ABC'})

    def test_get_action_no_exception(self):
        action = mommy.make(Action, name='TEST')
        self.assertEqual(action, Action.get_action('test'))

    def test_get_action_with_exception(self):
        action = mommy.make(Action, name='UNKNOWN')
        self.assertEqual(action, Action.get_action('test'))

    def test_get_active_response(self):
        action = mommy.make(Action)
        responses = mommy.make(Response, active=False, _quantity=3)
        responses[2].active = True
        responses[2].action = action
        responses[2].save()
        self.assertEqual(responses[2], action.get_active_response())

    def test_save(self):
        action = Action(name='test')
        action.save()
        self.assertEqual('TEST', action.name)


class ResponseModelTest(CommonTestCase):

    def test_unicode(self):
        self.string_test('Response', 'Response for ABC', **{
                'action': mommy.make('django_twilio_sms.Action', name='ABC')
            })

    def test_if_active_no_exception_self_not_equal_current(self):
        action = mommy.make(Action)
        mommy.make(Response, action=action, active=True)
        response = mommy.make(Response, action=action, active=False)
        response.active = True
        response.save()
        responses = Response.objects.filter(action=action, active=True)
        self.assertEqual(
            1, responses.count()
        )
        self.assertEqual(response, responses[0])

    def test_if_active_no_exception_self_equal_current(self):
        response = mommy.make(Response, active=True)
        response.body = 'test'
        response.save()
        responses = Response.objects.filter(active=True)
        self.assertEqual(
            1, responses.count()
        )
        self.assertEqual(response, responses[0])

    def test_if_active_with_exception(self):
        actions = mommy.make(Action, _quantity=2)
        mommy.make(Response, action=actions[1], active=True)
        response = Response(body='test', action=actions[0], active=True)
        response.save()
        responses = Response.objects.filter(action=actions[0], active=True)
        self.assertEqual(
            1, responses.count()
        )
        self.assertEqual(response, responses[0])

    def test_if_not_active(self):
        action = mommy.make(Action)
        response = Response(body='test', action=action, active=False)
        response.save()
        self.assertEqual(1, Response.objects.all().count())
        self.assertEqual(response, Response.objects.first())
