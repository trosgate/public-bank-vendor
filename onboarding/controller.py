from .models import Invitation, Application
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.utils import timezone


def one_month():
    return (timezone.now() + relativedelta(months = 1))

def max_number_of_invited_links(tender):
    num_of_invites = Invitation.objects.filter(tender=tender).count()
    return tender.number_of_links >= num_of_invites

def has_atleast_one_applicant(tender):
    num_of_invites = Application.objects.filter(invitation__tender=tender).count()
    return num_of_invites > 0

def invite_link_has_expired(tender):
    return tender.duration > timezone.now()

