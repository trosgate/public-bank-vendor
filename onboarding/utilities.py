# Import from django

from django.conf import settings
#
# Import from python

from random import choice
from string import ascii_letters, digits

#
# This will estimate subscription expiry by 30 days interval
from datetime import timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_mail(value):
    try:
        validate_email(value)
    except ValidationError as e:
        print(str(e))
        raise
    else:
        return value


# Try to get the value from the settings module
SIZE = getattr(settings, "MAXIMUM_INVITE_SIZE", 12)

GENERATED_CHARS = ascii_letters + digits

def create_random_code(chars=GENERATED_CHARS):
    """
    Creates a random string with the predetermined size
    """
    return "".join([choice(chars) for _ in range(SIZE)])
    

def get_application_expiry(duration):
    return (timezone.now() + timedelta(days = duration))
