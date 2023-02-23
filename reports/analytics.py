from datetime import timedelta
from django.utils import timezone
from tickets.models import Ticket


def today_vendor_ticket_count(team):
    ticket = Ticket.objects.filter(
        team=team, 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()
    return ticket


def today_vendor_unassign_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="unassigned", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()
    return ticket


def today_vendor_assigned_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="assigned", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()
    return ticket


def today_vendor_started_ticket(team):
    total_started = Ticket.objects.filter(
        team=team, 
        status="started", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()
    total_reopen = Ticket.objects.filter(
        team=team, 
        status="reopen", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()

    return total_started + total_reopen


def today_vendor_deffered_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="deffered", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()
    return ticket


def today_vendor_closed_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="closed", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59)
    ).count()
    return ticket


def weekly_vendor_ticket_count(team):
    ticket = Ticket.objects.filter(
        team=team, 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()
    return ticket


def weekly_vendor_unassign_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="unassigned", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()
    return ticket


def weekly_vendor_assigned_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="assigned", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()
    return ticket


def weekly_vendor_started_ticket(team):
    total_started = Ticket.objects.filter(
        team=team, 
        status="started", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()
    total_reopen = Ticket.objects.filter(
        team=team, 
        status="reopen", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()

    return total_started + total_reopen


def weekly_vendor_deffered_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="deffered", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()
    return ticket


def weekly_vendor_closed_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="closed", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1)
    ).count()
    return ticket


def dual_weekly_vendor_ticket_count(team):
    ticket = Ticket.objects.filter(
        team=team, 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()
    return ticket


def dual_weekly_vendor_unassign_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="unassigned", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()
    return ticket


def dual_weekly_vendor_assigned_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="assigned", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()
    return ticket


def dual_weekly_vendor_started_ticket(team):
    total_started = Ticket.objects.filter(
        team=team, 
        status="started", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()

    total_reopen = Ticket.objects.filter(
        team=team, 
        status="reopen", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()

    return total_started + total_reopen


def dual_weekly_vendor_deffered_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="deffered", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()
    return ticket


def dual_weekly_vendor_closed_ticket(team):
    ticket = Ticket.objects.filter(
        team=team, 
        status="closed", 
        created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=15),
        created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=8)
    ).count()
    return ticket

