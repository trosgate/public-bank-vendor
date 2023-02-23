from .models import Ticket, AssignMember
from django.utils import timezone
from datetime import timedelta 
from dateutil.relativedelta import relativedelta



def ongoing_ticket(request):
    if request.user.user_type == 'vendor':
        total_started = Ticket.objects.filter(
            team = request.user.vendor.active_team_id,
            status='started'
        ).count()
        total_reopen = Ticket.objects.filter(
            team = request.user.vendor.active_team_id,
            status='reopen'
        ).count()
        return total_started + total_reopen
    
    elif request.user.user_type == 'custodian':
        total_started = Ticket.objects.filter(
            branch = request.user.branch,
            status='started'
        ).count()
        total_reopen = Ticket.objects.filter(
            branch = request.user.branch,
            status='reopen'
        ).count()
        return total_started + total_reopen


def user_time_worked_today(request):
    if request.user.user_type == 'vendor':
        tickets = AssignMember.objects.filter(
            team = request.user.vendor.active_team_id, 
            created_at__date__gte=timezone.now().replace(hour=0, minute=00),
            created_at__date__lte=timezone.now().replace(hour=23, minute=59),
            ticket__status='closed'
        )
        return sum(tracker.total_minutes for tracker in tickets)
    elif request.user.user_type == 'custodian':
        tickets = AssignMember.objects.filter(
            ticket__branch = request.user.branch, 
            created_at__date__gte=timezone.now().replace(hour=0, minute=00),
            created_at__date__lte=timezone.now().replace(hour=23, minute=59),
            ticket__status='closed'
        )
        return sum(tracker.total_minutes for tracker in tickets)


def user_time_worked_lastweek(request):
    if request.user.user_type == 'vendor':
        tickets = AssignMember.objects.filter(
            team = request.user.vendor.active_team_id, 
            created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
            created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1),
            ticket__status='closed'
        )
        return sum(tracker.total_minutes for tracker in tickets)
    
    elif request.user.user_type == 'custodian':
        tickets = AssignMember.objects.filter(
            ticket__branch = request.user.branch, 
            created_at__date__gte=timezone.now().today().replace(hour=00, minute=00) - timedelta(days=7),
            created_at__date__lte=timezone.now().today().replace(hour=23, minute=59) - timedelta(days=1),
            ticket__status='closed'
        )
        return sum(tracker.total_minutes for tracker in tickets)


def ticket_closed_for_month(request):
    if request.user.user_type == 'vendor':
        return Ticket.objects.filter(
            team = request.user.vendor.active_team_id, 
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year,
            status='closed'
        ).count()
    
    elif request.user.user_type == 'custodian':
        return Ticket.objects.filter(
            branch = request.user.branch,
            created_at__year=timezone.now().year,
            created_at__month=timezone.now().month,
            status='closed'
        ).count()



