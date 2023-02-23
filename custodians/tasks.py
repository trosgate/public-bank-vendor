from account.models import Customer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from general_settings.backends import get_website_email

from general_settings.utilities import (
    website_name,get_protocol_with_domain_path,get_instagram_path, 
    get_facebook_path,get_youtube_path,get_twitter_path
)
from celery import shared_task
from trosgate.celery import app
from django.utils import timezone
from datetime import timedelta
from django.apps import apps


@shared_task(bind = True)
def complaint_created_alert(self, pk, mailgroup):
    thisapp = apps.get_model('custodians', 'HelpDesk')
    complaint = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(branch__inventory=True)
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]

    from_email = get_website_email()
    subject = f'New case created for review or re-routing'
    preview = f'Case No. {complaint.reference} open'
    text_content = f'New case was created on {website_name()}'
    message = f"A new case was created on {website_name()}. Please review or re-route to appropriate branch"
    html_content = render_to_string('custodians/tasks/complaint_created.html', {
    # html_content = render_to_string('custodians/tasks/test.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'preview': preview,
        'subject': subject,
        'message': message,
        'complaint': complaint,
    })

    sender = f"{website_name()}<{from_email}>"

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task(bind = True)
def complaint_routing_alert(self, pk, mailgroup):
    thisapp = apps.get_model('custodians', 'HelpDesk')
    complaint = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(branch=complaint.support_branch)
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]

    from_email = get_website_email()
    subject = f'An open case re-routed to you'
    preview = f'Case No. {complaint.reference} Re-routed'
    text_content = f'New case was created on {website_name()}'
    message = f"An open case on {website_name()} was re-routed to your unit/branch with details below"
    html_content = render_to_string('custodians/tasks/complaint_routing.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'preview': preview,
        'subject': subject,
        'message': message,
        'complaint': complaint,
    })

    sender = f"{website_name()}<{from_email}>"

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task(bind = True)
def complaint_reply_alert(self, pk, mailgroup):
    thisapp = apps.get_model('custodians', 'HelpDeskMessage')
    complaint = thisapp.objects.get(pk=pk)

    if complaint.support.branch == complaint.helpdesk.request_branch:
        #Then this is a folllow up
        customer = Customer.objects.filter(branch=complaint.helpdesk.support_branch)
    else:
        customer = Customer.objects.filter(branch=complaint.helpdesk.request_branch)
        #Then this is a reply

    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]
    suport_user = f'{complaint.support.get_full_name()} <{complaint.support.email}>'

    from_email = get_website_email()
    subject = f'Reply to an open case'
    preview = f'Case No. {complaint.helpdesk.reference} Replied'
    text_content = f'New case was created on {website_name()}'
    message = f"{complaint.content}"
    html_content = render_to_string('custodians/tasks/complaint_reply.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'preview': preview,
        'subject': subject,
        'message': message,
        'complaint': complaint,
    })

    # sender = f"{website_name()}<{from_email}>"

    msg = EmailMultiAlternatives(subject, text_content, suport_user, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

