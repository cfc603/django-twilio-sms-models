from django_twilio.models import Caller
from model_mommy.recipe import Recipe, seq

from django_twilio_sms.models import Message, PhoneNumber


caller_recipe = Recipe(Caller, phone_number=seq('+1999999999'))
phone_number_recipe = Recipe(PhoneNumber, caller=caller_recipe.make)
message_recipe = Recipe(
    Message,
    from_phone_number=phone_number_recipe.make,
    to_phone_number=phone_number_recipe.make
)
