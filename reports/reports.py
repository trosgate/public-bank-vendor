from django.db.models import Avg, F
from datetime import timedelta
from django.utils import timezone
from vendors.models import Team
from tickets.models import Ticket, AssignMember


def average_response(vendor, start_date, end_date):
    ticket = AssignMember.objects.filter(
        vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        ticket__status='closed'
    ).annotate(
        total_arrival_time=(F("arrival_confirm") - F("ticket__arrival_time")),
        total_before_start=(F("ticket__created_at") - F("created_at"))
    ).aggregate(
        arrival=(Avg("total_arrival_time")),
        unassigned=(Avg("total_before_start")),
    )
    return ticket


def vendor_time_worked(vendor, start_date, end_date):
    tickets = AssignMember.objects.filter(
        vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        ticket__status='closed'
    )
    return sum(tracker.total_minutes for tracker in tickets)


def unassigned_ticket_count(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        status='unassigned'
    ).count()
    return ticket


def assigned_ticket_count(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        status='assigned'
    ).count()
    return ticket


def started_ticket_count(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        status='started'
    ).count()
    return ticket


def deffered_ticket_count(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        status='deffered'
    ).count()
    return ticket


def reopen_ticket_count(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        status='reopen'
    ).count()
    return ticket


def closed_ticket_count(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        status='closed'
    ).count()
    return ticket


def total_ticket(vendor, start_date, end_date):
    ticket = Ticket.objects.filter(
        terminal__vendor = vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).count()
    return ticket




















































