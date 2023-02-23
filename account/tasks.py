from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from general_settings.backends import get_website_email
from celery import shared_task
from django.apps import apps
from account.tokens import account_activation_token
from general_settings.utilities import (
    website_name,
    get_protocol_with_domain_path,
    get_instagram_path, 
    get_facebook_path, 
    get_youtube_path, 
    get_twitter_path
)

#
#New user creation alert function
@shared_task(bind = True, max_retries=3)
def user_creation(self, pk):
    thisapp = apps.get_model('account', 'Customer')
    user = thisapp.objects.get(pk=pk)
    from_email = get_website_email()
    subject = f'User creation on {website_name()}'
    preview = f'Your profile was created'
    text_content = f'User creation on {website_name()}'
    message = f"You have just been added to our ATM support platform ({website_name()}) with temporal access. Please click button below and select 'Reset Password' option to initiate your login."
    html_content = render_to_string('account/tasks/user_creation.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'user': user,
        'preview': preview,
        'subject': subject,
        'message': message,
        'encode_id': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),        
    })
    sender = f"{website_name()}<{from_email}>"
    receiver = f"{user.get_full_name()}<{user.email}>"
    msg = EmailMultiAlternatives(subject, text_content, sender, [receiver])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


# Utility function for sending Test email using celery
@shared_task(bind = True, max_retries=3)
def send_test_mail(self, to_email):
    from_email = get_website_email()
    subject = f'Test Email on {website_name()}'
    text_content = f"Test Email on {website_name()}"
    html_content = render_to_string('account/tasks/test_email.html', {
        'website_email': from_email,
        'text_content': text_content,
        'website_name': website_name(),
    })
    sender = f"{website_name()}<{from_email}>"
    receiver = f"Testing email <{to_email}>"
    msg = EmailMultiAlternatives(subject, text_content, sender, [receiver], bcc=[sender])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

#
# Utility function for sending login token via mail to staff
@shared_task(bind = True, max_retries=3)
def two_factor_auth_mailer(self, pk, pass_code):
    thisapp = apps.get_model('account', 'Customer')
    user = thisapp.objects.get(pk=pk)    
    from_email = get_website_email()
    subject = f'User login activation on {website_name()}'
    text_content = f"Hello {user.get_full_name()}, You are about to log into your account. Please your code for login on {website_name()} is: { pass_code}"
    html_content = render_to_string('account/tasks/two_factor_auth.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'user': user.get_full_name(),
        'subject': subject,
        'pass_code': pass_code,
       
    })
    staff_user = f"{user.get_full_name()}<{user.email}>"

    msg = EmailMultiAlternatives(subject, text_content, from_email, [staff_user])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

#
# Utility function for sending new team member invite
@shared_task(bind = True, max_retries=3)
def invitation_to_team(self, user_pk, team_pk, moderator):
    customerapp = apps.get_model('account', 'Customer')
    teamapp = apps.get_model('vendors', 'Team')
    user = customerapp.objects.get(pk=user_pk)   
    team = teamapp.objects.get(pk=team_pk)   

    from_email = get_website_email()
    subject = f'Invitation to Team'
    preview = f'Team Invite from {team.title}'
    text_content = f'Invitation to {website_name()}'
    message = f"You have been invited by your company, {team.title}, to join their sterling virtual team on {website_name()}."
    html_content = render_to_string('account/tasks/invitation_to_team.html', {
        'website_email': from_email,
        'website_name': website_name(),
        'protocol_with_domain': get_protocol_with_domain_path(),
        'instagram_path': get_instagram_path(),
        'facebook_path': get_facebook_path(),
        'youtube_path': get_youtube_path(),
        'twitter_path': get_twitter_path(),
        'user': user,
        'preview': preview,
        'subject': subject,
        'message': message,
        'encode_id': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),        
    })
    sender = f"{website_name()}<{from_email}>"
    vendor_team = f"{user.get_full_name()}<{user.email}>"

    msg = EmailMultiAlternatives(subject, text_content, sender, [vendor_team], cc=[moderator])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()



