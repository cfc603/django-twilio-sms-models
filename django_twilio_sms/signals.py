from django.dispatch import Signal


response_message = Signal(providing_args=['action', 'message'])
