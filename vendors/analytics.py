from django.db.models import Avg, F, Q, Count, Sum, Aggregate, Max
from datetime import timedelta
from django.utils import timezone
from .models import Team
from tickets.models import Ticket, AssignMember
from django.db.models import F, Q, Value, When, Case
from decimal import Decimal



def today_vendor_ticket_count(team):
    ticket = Ticket.objects.filter(
        team=team, 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),
    ).count()
    return ticket



def unassigned_ticket_count(team):
    return Ticket.objects.filter(
        team=team,
        status='unassigned'
    ).count()


def assigned_ticket_count(team, engineer):
    return AssignMember.objects.filter(
        team=team,
        assignee = engineer,
        ticket__status='assigned'
    ).count()


def ongoing_ticket_count(team, engineer):
    started = AssignMember.objects.filter(
        team=team,assignee = engineer,
        ticket__status='started'
    ).count()
    reopen = AssignMember.objects.filter(
        team=team, assignee = engineer,
        ticket__status='reopen'
    ).count()
    return int(started + reopen)


def deffered_ticket_count(team, engineer):
    return AssignMember.objects.filter(
        team=team,
        assignee = engineer,
        ticket__status='deffered'
    ).count()


def mytoday_ticket_count(team, engineer):
    return AssignMember.objects.filter(
        team=team,
        assignee = engineer,
        ticket__created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        ticket__created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),        
    ).count()


def mytoday_assigned_count(team, engineer):
    return AssignMember.objects.filter(
        team=team,
        assignee = engineer,
        ticket__created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        ticket__created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),
        ticket__status='assigned'        
    ).count()


def mytoday_ongoing_count(team, engineer):
    started = AssignMember.objects.filter(
        team=team,assignee = engineer,
        ticket__created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        ticket__created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),
        ticket__status='started'
    ).count()
    reopen = AssignMember.objects.filter(
        team=team, assignee = engineer,
        ticket__created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        ticket__created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),
        ticket__status='reopen'
    ).count()
    return int(started + reopen)


def mytoday_paused_count(team, engineer):
    return AssignMember.objects.filter(
        team=team,
        assignee = engineer,
        ticket__created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        ticket__created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),
        ticket__status='deffered'        
    ).count()


def mytoday_closed_count(team, engineer):
    return AssignMember.objects.filter(
        team=team,
        assignee = engineer,
        ticket__created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        ticket__created_at__date__lte=timezone.now().today().replace(hour=23, minute=59),
        ticket__status='closed'        
    ).count()



