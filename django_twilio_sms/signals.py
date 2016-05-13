from django.dispatch import Signal


response_message = Signal(providing_args=['action', 'message'])


unsubscribe_signal = Signal(providing_args=['message', 'unsubscribed'])
