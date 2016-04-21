from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.six import iteritems

from django_twilio_sms.models import Action, Response


class Command(BaseCommand):
    help = "Sync responses from settings.DJANGO_TWILIO_SMS_RESPONSES"

    def handle(self, *args, **options):
        if hasattr(settings, 'DJANGO_TWILIO_SMS_RESPONSES'):
            for action in Action.objects.all():
                action.delete()

            for action, response in iteritems(
                    settings.DJANGO_TWILIO_SMS_RESPONSES):
                action = Action.objects.create(name=action)
                response = Response.objects.create(
                    body=response, action=action
                )

                self.stdout.write('CREATED: {}-{}'.format(
                    action.name, response.body
                ))
        else:
            self.stdout.write('No responses found in settings.')

            if Action.objects.all().count() > 0:
                for action in Action.objects.all():
                    action.delete()
                self.stdout.write('All saved responses have been deleted.')
