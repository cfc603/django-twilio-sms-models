from django.core.urlresolvers import reverse
from django.test import override_settings, TestCase

from mock import patch, Mock

from .mommy_recipes import message_recipe
from django_twilio_sms.views import message_view, voice_view


@override_settings(DJANGO_TWILIO_FORGERY_PROTECTION=False)
class CallbackViewTest(TestCase):

    @patch('django_twilio_sms.views.message_view')
    def test_if_twilio_request_type_is_message(self, mock_message_view):
        response = self.client.post(
            reverse('django_twilio_sms:callback_view')
        )
        self.assertTrue(mock_message_view.called)
        self.assertIn('<Response />', str(response.content))


@override_settings(DJANGO_TWILIO_FORGERY_PROTECTION=False)
class InboundViewTest(TestCase):

    @override_settings(DJANGO_TWILIO_SMS_RESPONSE_MESSAGE=False)
    @patch('django_twilio_sms.views.message_view')
    def test_if_twilio_request_type_is_message(self, mock_message_view):
        mock = Mock()
        mock_message_view.return_value = mock
        response = self.client.post(
            reverse('django_twilio_sms:inbound_view'), {'MessageSid': 'test'}
        )
        self.assertTrue(mock_message_view.called)
        self.assertFalse(mock.send_response_message.called)
        self.assertIn('<Response />', str(response.content))

    @override_settings(DJANGO_TWILIO_SMS_RESPONSE_MESSAGE=True)
    @patch('django_twilio_sms.views.message_view')
    def test_if_twilio_request_type_is_message_if_response_message(self,
            mock_message_view):
        mock = Mock()
        mock_message_view.return_value = mock
        response = self.client.post(
            reverse('django_twilio_sms:inbound_view'), {'MessageSid': 'test'}
        )
        self.assertTrue(mock_message_view.called)
        self.assertTrue(mock.send_response_message.called)
        self.assertIn('<Response />', str(response.content))

    @override_settings(DJANGO_TWILIO_SMS_RESPONSE_MESSAGE=False)
    @override_settings(DJANGO_TWILIO_RESPONSE_MESSAGE=True)
    @patch('django_twilio_sms.views.message_view')
    def test_if_twilio_request_type_is_message_if_old_response_message(self,
            mock_message_view):
        mock = Mock()
        mock_message_view.return_value = mock
        response = self.client.post(
            reverse('django_twilio_sms:inbound_view'), {'MessageSid': 'test'}
        )
        self.assertTrue(mock_message_view.called)
        self.assertTrue(mock.send_response_message.called)
        self.assertIn('<Response />', str(response.content))

    def test_if_not_twilio_request_type_is_message(self):
        response = self.client.post(
            reverse('django_twilio_sms:inbound_view')
        )
        self.assertIn('<Response><Reject /></Response>', str(response.content))


class MessageViewTest(TestCase):

    @patch('django_twilio_sms.views.Message')
    def test_if_created(self, mock_message):
        mock_message.get_or_create.return_value = (mock_message, True)
        message_view(Mock(messagesid='test'))
        self.assertTrue(mock_message.get_or_create.called)
        self.assertFalse(mock_message.sync_twilio_message.called)
        mock_message.get_or_create.assert_called_with('test')

    @patch('django_twilio_sms.views.Message')
    def test_if_not_created(self, mock_message):
        mock_message.get_or_create.return_value = (mock_message, False)
        message_view(Mock(messagesid='test'))
        self.assertTrue(mock_message.get_or_create.called)
        self.assertTrue(mock_message.sync_twilio_message.called)
        mock_message.get_or_create.assert_called_with('test')

    @patch('django_twilio_sms.views.Message')
    def test_returns_message_object(self, mock_message):
        message = message_recipe.make()
        mock_message.get_or_create.return_value = (message, True)
        self.assertEqual(message, message_view(Mock(messagesid='test')))


class VoiceViewTest(TestCase):

    def test_return_response(self):
        mock_response = Mock()
        response = voice_view(mock_response)
        self.assertTrue(mock_response.reject.called)
        self.assertEqual(mock_response, response)
