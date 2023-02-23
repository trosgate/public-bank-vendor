from . models import WebsiteSetting
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def website_name():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0].site_name
    except:
        return None


def get_protocol_only():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0].protocol
    except:
        return None


def get_protocol_with_domain_path():
    try:
        website_setting = WebsiteSetting.objects.get_or_create(pk=1)[0]
        return f'{website_setting.protocol}{website_setting.site_domain}'
    except:
        return f'http://127.0.0.1:8000'


def get_twitter_path():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0].twitter_url
    except:
        return None


def get_youtube_path():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0].youtube_url
    except:
        return None


def get_facebook_path():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0].facebook_url
    except:
        return None
    

def get_instagram_path():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0].instagram_url
    except:
        return None


def homepage_layout():
    try:
        return WebsiteSetting.objects.get_or_create(pk=1)[0]
    except:
        return None


def get_creation_time(ticket, vendor):
    day_starts = timezone.now().replace(hour=7, minute=30)
    day_ends = timezone.now().replace(hour=17, minute=00)
    instation_arrival = timezone.now() + timedelta(hours = vendor.instation_arrival)
    outstation_arrival = timezone.now() + timedelta(hours = vendor.outstation_arrival)

    if vendor.working_hours == False:
        return timezone.now()
    
    elif vendor.working_hours == True and ticket.terminal.branch.location == 'instation':

        if (day_starts <= instation_arrival <= day_ends):
            return timezone.now()
        else:
            return day_starts + timedelta(days=1)

    elif vendor.working_hours == True and ticket.terminal.branch.location == 'outstation':
        if (day_starts <= outstation_arrival <= day_ends):
            return timezone.now()
        else:
            return day_starts + timedelta(days=1)


def get_assign_time(ticket, vendor):
    day_assign_starts = timezone.now().replace(hour=7, minute=31)
    future_assign_starts = timezone.now().replace(hour=7, minute=35)
    day_assign_ends = timezone.now().replace(hour=17, minute=00)
    instation_arrival = timezone.now() + timedelta(hours = vendor.instation_arrival)
    outstation_arrival = timezone.now() + timedelta(hours = vendor.outstation_arrival)

    if vendor.working_hours == False:
        return timezone.now()
    
    elif vendor.working_hours == True and ticket.terminal.branch.location == 'instation':

        if (day_assign_starts <= instation_arrival <= day_assign_ends):
            return timezone.now()
        else:
            return future_assign_starts + timedelta(days=1)

    elif vendor.working_hours == True and ticket.terminal.branch.location == 'outstation':
        if (day_assign_starts <= outstation_arrival <= day_assign_ends):
            return timezone.now()
        else:
            return future_assign_starts + timedelta(days=1)


def get_arrival_time(ticket, vendor):
    if ticket.terminal.branch.location == 'instation':
        return timedelta(hours = vendor.instation_arrival)

    elif ticket.terminal.branch.location == 'outstation':
        return timedelta(hours = vendor.outstation_arrival)
