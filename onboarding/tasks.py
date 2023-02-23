from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from general_settings.backends import get_website_email
from celery import shared_task
from django.apps import apps
from account.models import Customer
from general_settings.utilities import (
    website_name,
    get_protocol_with_domain_path,
    get_instagram_path, 
    get_facebook_path, 
    get_youtube_path, 
    get_twitter_path
)

#
@shared_task(bind = True, max_retries=5)
def send_invitation_link(self, reference):
    thisapp = apps.get_model('onboarding', 'Invitation')
    invitation = thisapp.objects.get(reference=reference)
    contentapp = apps.get_model('general_settings', 'WebsiteSetting')
    contentmodel = contentapp.objects.get_or_create(pk=1)[0]
    
    customer = Customer.objects.filter(is_stakeholder=True)
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]

    from_email = get_website_email()
    subject = f'Invitation to Tender on {website_name()}'
    preview = f'Access Key: {invitation.token}'
    text_content = f'Invitation to Tender on {website_name()}'
    message = f"{contentmodel.invite_message}"
    html_content = render_to_string('onboarding/tasks/invitation.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'invitation': invitation,
        'preview': preview,
        'subject': subject,
        'message': message,
    })
    sender = f"{website_name()}<{from_email}>"
    receiver = f"{invitation.receiver.name}<{invitation.receiver.email}>"
    msg = EmailMultiAlternatives(subject, text_content, sender, [receiver], bcc=team_list)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

#
@shared_task(bind = True, max_retries=5)
def pending_approval(self, pk):
    thisapp = apps.get_model('onboarding', 'Grading')
    grading = thisapp.objects.get(pk=pk)
    
    receivers = Customer.objects.filter(user_type='head')
    team_list = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(receivers, receivers)]

    from_email = get_website_email()
    subject = f'Application Pending Approval On {website_name()}'
    preview = f'Application Ref:{grading.application.reference} Pending Approval'
    text_content = f'Invitation to Tender on {website_name()}'
    message = f"Application with above reference has gotten to your table for review and approval. This mail comes as a notice"
    html_content = render_to_string('onboarding/tasks/pending_approval.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'grading': grading,
        'preview': preview,
        'subject': subject,
        'message': message,
    })

    sender = f"{grading.created_by.get_full_name()}<{grading.created_by.email}>"
    msg = EmailMultiAlternatives(subject, text_content, sender, team_list)
    msg.attach_alternative(html_content, 'text/html')
    msg.send() 

#
@shared_task(bind = True, max_retries=5)
def approved_and_profiled(self, application_pk, vendor_pk):
    thisapp = apps.get_model('onboarding', 'Application')
    application = thisapp.objects.get(pk=application_pk)

    vendorapp = apps.get_model('general_settings', 'VendorCompany')
    vendor = vendorapp.objects.get(pk=vendor_pk)
    vendor_support = f"{vendor.registered_name}<{vendor.email}>"
    
    receivers = Customer.objects.filter(is_stakeholder=True, is_active=True)
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(receivers, receivers)]

    from_email = get_website_email()
    subject = f'Application Approved Successfully'
    preview = f'Application Ref:{application.reference} Approved'
    text_content = f'Application approved on {website_name()}'
    message = f"Congratulations! We at {website_name()} are glad to inform you that your Application with above reference has been approved. In the coming days, you will be briefed with how to get started. Thank you"
    html_content = render_to_string('onboarding/tasks/application_approved.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'vendor': vendor,
        'application': application,
        'preview': preview,
        'subject': subject,
        'message': message,
    })

    sender = f"{website_name()}<{from_email}>"
    msg = EmailMultiAlternatives(subject, text_content, sender, [vendor_support], bcc=team_list)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

