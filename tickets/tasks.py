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
from django.db.models import Q
from django.db import transaction as db_transaction


@shared_task(bind = True)
def ticket_opened_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'Ticket')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(vendor_company=ticket.terminal.vendor)
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]

    from_email = get_website_email()
    subject = f'New ticket opened'
    preview = f'Ticket {ticket.reference} was created'
    text_content = f'User creation on {website_name()}'
    message = f"A new ticket with reference {ticket.reference} was created on {website_name()}. Below are the details"
    html_content = render_to_string('tickets/tasks/ticket_open.html', {
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
        'ticket': ticket,
    })

    sender = f"{website_name()}<{from_email}>"

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task(bind = True)
def ticket_assign_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'AssignMember')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(vendor_company=ticket.vendor).distinct()
    team_list = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]
    from_email = get_website_email()
    sender = f"{website_name()}<{from_email}>"

    subject = f'New job assigned to You'
    preview = f'Ticket No. {ticket.ticket.reference} Assigned'
    text_content = f'New job assigned to you on {website_name()}'
    message = f"A new job with details below was assigned to you by your company, {ticket.vendor.name}"
    html_content = render_to_string('tickets/tasks/ticket_assigned.html', {
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
        'ticket': ticket
    })

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

@shared_task(bind = True)
def ticket_ongoing_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'AssignMember')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(vendor_company=ticket.vendor).distinct()
    team_list = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]
    from_email = get_website_email()
    sender = f"{website_name()}<{from_email}>"

    subject = f'The assigned job now started'
    preview = f'Ticket No. {ticket.ticket.reference} started'
    text_content = f'New job assigned to you on {website_name()}'
    message = f"You are receiving this mail as a confirmation that, Engr. {ticket.assignee.get_full_name()} or his colleague is available on site to start work."
    html_content = render_to_string('tickets/tasks/ticket_started.html', {
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
        'ticket': ticket
    })

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

@shared_task(bind = True)
def ticket_deferred_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'Ticket')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(branch=ticket.branch).distinct()
    branches = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]
     
    from_email = get_website_email()
    sender = f"{website_name()}<{from_email}>"

    subject = f'You have paused ticket'
    preview = f'Ticket No. {ticket.reference} Paused'
    text_content = f'Ticket paused on {website_name()}'
    message = f"You are receiving this mail because your branch paused this ticket with reason(s) below"
    html_content = render_to_string('tickets/tasks/ticket_deferred.html', {
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
        'ticket': ticket,
    })

    msg = EmailMultiAlternatives(subject, text_content, sender, branches, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

@shared_task(bind = True)
def ticket_reopen_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'Ticket')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(branch=ticket.branch).distinct()
    branches = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]
     
    from_email = get_website_email()
    sender = f"{website_name()}<{from_email}>"

    subject = f'You have reopen ticket'
    preview = f'Ticket # {ticket.reference} Reopened'
    text_content = f'Ticket reopened on {website_name()}'
    message = f"This mail serves to notify you that an earlier paused ticket ({ticket.reference}) was reopen by your branch. If you did not perform this action, please contact administrator."
    html_content = render_to_string('tickets/tasks/ticket_reopen.html', {
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
        'ticket': ticket,
    })

    msg = EmailMultiAlternatives(subject, text_content, sender, branches, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

@shared_task(bind = True)
def ticket_closed_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'Ticket')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(vendor_company=ticket.terminal.vendor).distinct()
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]

    from_email = get_website_email()
    sender = f"{website_name()}<{from_email}>"

    subject = f'Ticket No. [{ticket.reference}] now closed'
    preview = f'Ticket {ticket.reference} closed'
    text_content = f'Ticket closed on {website_name()}'
    message = f"This ticket has been closed. To accomodate the feedback of your assigned engineer, please review below:"
    html_content = render_to_string('tickets/tasks/ticket_closed.html', {
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
        'ticket': ticket,
    })

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

@shared_task(bind = True)
def ticket_remark_alert(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'Ticket')
    ticket = thisapp.objects.get(pk=pk)

    customer = Customer.objects.filter(vendor_company=ticket.terminal.vendor).distinct()
    team_list = [f'{name.get_full_name()} <{mail.email}>' for name, mail in zip(customer, customer)]

    from_email = get_website_email()
    sender = f"{website_name()}<{from_email}>"

    subject = f'New Feedback received on recently closed job'
    preview = f'Ticket {ticket.reference} received a feedback'
    text_content = f'Ticket remark received on {website_name()}'
    message = f"This ticket has received feedback from the assigned engineers.Kindly review to improve service"
    html_content = render_to_string('tickets/tasks/ticket_remark.html', {
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
        'ticket': ticket,
    })

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    

@shared_task(bind = True)
def ticket_recalled(self, pk, mailgroup):
    thisapp = apps.get_model('tickets', 'Ticket')
    ticket = thisapp.objects.get(pk=pk)
    customer = Customer.objects.filter(vendor_company=ticket.terminal.vendor).distinct()
    team_list = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]
            
    from_email = get_website_email()
    subject = f'Recent ticket recalled'
    preview = f'Ticket # {ticket.reference} was recalled'
    text_content = f'Ticket recalled on on {website_name()}'
    message = f"The ticket with reference {ticket.reference} was recalled. As such, your team can ignore"
    html_content = render_to_string('tickets/tasks/ticket_recalled.html', {
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
        'reference': ticket.reference,
        'user': ticket.created_by.get_full_name(),
    })

    sender = f"{website_name()}<{from_email}>"

    msg = EmailMultiAlternatives(subject, text_content, sender, team_list, cc=mailgroup)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
   
    ticket.delete()


@app.task(name='send_unassigned_ticket_reminder')
def send_unassigned_ticket_reminder(*args, **kwargs):
    try:
        from_email = get_website_email()
        thisapp = apps.get_model('tickets', 'Ticket')
        tickets = thisapp.objects.filter(status='unassigned')
        for ticket in tickets:
            future_time = (ticket.created_at - timedelta(minutes=20))
            if ticket.created_at > future_time:
                customer = Customer.objects.filter(vendor_company__name=ticket.team.title).exclude(pk=ticket.team.created_by.pk)
                team_members = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]
                moderator = f'{ticket.team.created_by.get_full_name()}<{ticket.team.created_by.email}>'
                subject = f'[Reminder] Ticket No.- {ticket.reference} not Assigned'
                preview = f'Ticket {ticket.reference} not Assigned'
                text_content = f'Unassigned ticket reminder on {website_name()}'
                message = f"A ticket with details below has not been assigned to any of your team. This mail comes as a reminder"
                html_content = render_to_string('tickets/tasks/unassign_ticket.html', {
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
                    'title': ticket.title,
                    'created_at': ticket.created_at,
                    'branch': ticket.branch.name,
                    'terminal': ticket.terminal.name,

                })

                sender = f"{website_name()}<{from_email}>"

                msg = EmailMultiAlternatives(subject, text_content, sender, [moderator], cc=team_members)
                msg.attach_alternative(html_content, 'text/html')
                msg.send()

    except Exception as e:
        print(str(e))


@app.task(name='ongoing_ticket_paused_by_end_of_working_hours')
def ongoing_ticket_paused_by_end_of_working_hours(*args, **kwargs):
    try:
        ticket_model = apps.get_model('tickets', 'Ticket')
        assign_model = apps.get_model('tickets', 'AssignMember')
        started_tickets = ticket_model.objects.filter(status ='started', paused_by_system=False)
        
        #Tickets with status 'started' but are not yet flagged by system
        for ticket in started_tickets:
            ticket.status = 'deffered'
            ticket.paused_by_system = True
            ticket.save()

            assign = assign_model.objects.filter(ticket=ticket.pk).first()
            time_worked = timezone.now() - assign.arrival_confirm
            minutes = (time_worked.seconds/60)
            assign.completion_time = None            
            assign.total_minutes += minutes
            assign.deffered_count += 1
            assign.save()

        reopen_tickets = ticket_model.objects.filter(status ='reopen', paused_by_system=False)
        #Tickets with status 'reopen' but are not yet flagged by system
        for ticket in reopen_tickets:
            ticket.status = 'deffered'
            ticket.paused_by_system = True
            ticket.save()

            assign = assign_model.objects.filter(ticket=ticket.pk).first()
            time_worked = timezone.now() - assign.arrival_confirm
            minutes = (time_worked.seconds/60)
            assign.completion_time = None            
            assign.total_minutes += minutes
            assign.deffered_count += 1
            assign.save()

    except Exception as e:
        print(str(e))


@app.task(name='reopen_ticket_at_start_of_working_hours')
def reopen_ticket_at_start_of_working_hours(*args, **kwargs):
    try:
        ticket_model = apps.get_model('tickets', 'Ticket')
        assign_model = apps.get_model('tickets', 'AssignMember')
        
        # All Tickets flagged by system at night shall be reopened
        reopen_tickets = assign_model.objects.filter(ticket__status ='deffered', ticket__paused_by_system=True)
        for assign in reopen_tickets:
            assign.arrival_confirm = timezone.now()
            assign.save()
                                
        ticket_model.objects.filter(
            status ='deffered', paused_by_system=True
        ).update(status='reopen', paused_by_system=False)

    except Exception as e:
        print(str(e))

