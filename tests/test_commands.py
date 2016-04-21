from django.conf import settings
from django.core.management import call_command
from django.test import override_settings, TestCase
from django.utils.six import StringIO

from model_mommy import mommy

from django_twilio_sms.models import Action, Response


class SyncResponsesCommandTest(TestCase):

    def setUp(self):
        super(SyncResponsesCommandTest, self).setUp()
        self.out = StringIO()

    @override_settings(DJANGO_TWILIO_SMS_RESPONSES={
            'STOP': 'Test stop message.',
            'START': 'Test start message.',
        })
    def test_handle_if_responses(self):
        action = mommy.make(Action, name='STOP')
        mommy.make(Response, body='old stop', action=action)
        call_command('sync_responses', stdout=self.out)

        self.assertEqual(2, Action.objects.all().count())
        self.assertEqual(2, Response.objects.all().count())
        self.assertIn('CREATED: STOP-Test stop message.', self.out.getvalue())
        self.assertIn(
            'CREATED: START-Test start message.', self.out.getvalue()
        )

    @override_settings(DJANGO_TWILIO_SMS_RESPONSES=None)
    def test_handle_if_not_responses_if_action_count_greater_zero(self):
        del settings.DJANGO_TWILIO_SMS_RESPONSES
        action = mommy.make(Action, name='STOP')
        mommy.make(Response, body='test stop', action=action)
        call_command('sync_responses', stdout=self.out)

        self.assertEqual(0, Action.objects.all().count())
        self.assertIn('No responses found in settings.', self.out.getvalue())
        self.assertIn(
            'All saved responses have been deleted.', self.out.getvalue()
        )

    @override_settings(DJANGO_TWILIO_SMS_RESPONSES=None)
    def test_handle_if_not_responses_if_action_count_equal_zero(self):
        del settings.DJANGO_TWILIO_SMS_RESPONSES
        call_command('sync_responses', stdout=self.out)

        self.assertIn('No responses found in settings.', self.out.getvalue())
        self.assertNotIn(
            'All saved responses have been deleted.', self.out.getvalue()
        )
