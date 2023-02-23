from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from .forms import TicketForm, AssignForm, SLAExceptionsForm
from account.decorators import user_is_moderator, user_is_vendor, user_is_custodian
from django.contrib.auth.decorators import login_required
from account.models import Customer
from django.http import HttpResponse, JsonResponse
from .models import Ticket, AssignMember
from general_settings.models import Category, Checklist, Terminals, Branch, SLAExceptions, VendorCompany
from vendors.models import Team
from django.db.models import Q
from django.contrib import messages
from django.db import transaction as db_transaction
from datetime import timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from .tasks import (
    ticket_recalled, 
    ticket_opened_alert, 
    ticket_reopen_alert, 
    ticket_closed_alert,
    ticket_remark_alert,
    ticket_ongoing_alert
)
from future.utilities import(
    get_open_ticket_feature,
    get_started_ticket_feature,
    get_reopen_ticket_feature,
    get_closed_ticket_feature,
    get_remarks_feature
)
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from general_settings.models import MailingGroup
from general_settings.utilities import get_creation_time
from .utilities import get_mailing_group, get_mailing_group_with_branch
from .statistics import ongoing_ticket, user_time_worked_today, user_time_worked_lastweek, ticket_closed_for_month


@login_required
def remove_message(request):
    return HttpResponse("")


@login_required
def search_ticket(request):
    search_word = request.POST.get('search')
    
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        
        tickets = Ticket.objects.filter(
            Q(title__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            team=team
        )
    
    elif request.user.user_type == Customer.CUSTODIAN:
        branch=request.user.branch
        
        tickets = Ticket.objects.filter(
            Q(title__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            branch=branch
        )

    context = {
        'tickets': tickets,   
    }
    return render(request, 'tickets/partials/dashboard_tables.html', context)


@login_required
def search_closed_ticket(request):
    search_word = request.POST.get('search')
    
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        
        tickets = Ticket.objects.filter(
            Q(title__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            team=team,
            status='closed'
        )
    
    elif request.user.user_type == Customer.CUSTODIAN:
        branch=request.user.branch
        
        tickets = Ticket.objects.filter(
            Q(title__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            branch=branch,
            status='closed'
        )

    context = {
        'tickets': tickets,   
    }
    return render(request, 'tickets/partials/closed_tables.html', context)


@login_required
@user_is_custodian
@require_http_methods(['POST'])
def create_ticket(request):
    if request.POST.get('action') == 'create-ticket':
        title = request.POST.get('title')
        description = str(request.POST.get('description'))
        category_id = request.POST.get('category')
        terminal_id = request.POST.get('terminal')
        
        branch = request.user.branch
        category = get_object_or_404(Category, pk=category_id, meta=True)
        terminal = get_object_or_404(Terminals, pk=terminal_id)
        
        company = get_object_or_404(VendorCompany, category=category, name=terminal.vendor.name)
        founder = get_object_or_404(Customer, vendor_company=company, is_vendor=True)
        team = get_object_or_404(Team, created_by=founder)
        
        # try:
        #     company = VendorCompany.objects.get(category=category, name=terminal.vendor.name)
        # except Exception as e:
        #     print(str(e))
        #     company = None
        #     return JsonResponse({'errors':f'Vendor not implemented error', 'message':''}, safe=False)
        # try:
        #     founder = Customer.objects.get(Customer, vendor_company=company, is_vendor=True)
        #     team = Team.objects.get(Team, created_by=founder)
        # except Exception as e:
        #     print(str(e))
        #     founder = None
        #     team = None
        #     return JsonResponse({'errors':f'Vendor not found error', 'message':''}, safe=False)
        
        created_by = request.user
        if company is not None and founder is not None and founder is not team:
            try:
                Ticket.create(
                    created_by, 
                    title, 
                    category, 
                    branch, 
                    terminal, 
                    description,
                    team
                )

            except Exception as e:
                error = str(e)
                print(error)
                return JsonResponse({'errors':f'{error}', 'message':''}, safe=False)

            message = f'Ticket created successfuly'
            return JsonResponse({'errors':'', 'message':message}, safe=False)
                            
        return JsonResponse({'errors':'Please contact Administrator', 'message':''}, safe=False)


@login_required
def ticket_list(request):
    if request.user.user_type == Customer.VENDOR:
        category = request.user.vendor_company.category
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, category=category, status="unassigned")

        context = {
            'team': team,
            'tickets': tickets
        }
        return render(request, 'tickets/vendor_ticket_list.html', context)
        

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        ticketform = TicketForm(branch, request.POST or None)
        tickets = Ticket.objects.filter(branch=request.user.branch).exclude(status="closed")
        
        context = {
            'ticketform': ticketform,
            'tickets': tickets
        }
        return render(request, 'tickets/custodian_ticket_list.html', context)
    

@login_required
def unassigned_ticket_list(request):
    branch = None
    team = None
    tickets = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, status='unassigned')

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        tickets = Ticket.objects.filter(branch=branch, status='unassigned')

    context = {
        'tickets': tickets,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),            
        'ticket_closed_this_month': ticket_closed_for_month(request),            
    }
    return render(request, 'tickets/unassigned_ticket.html', context)
    

@login_required
def assigned_ticket_list(request):
    branch = None
    team = None
    tickets = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, status='assigned')

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        tickets = Ticket.objects.filter(branch=branch, status='assigned')

    context = {
        'tickets': tickets,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),
        'ticket_closed_this_month': ticket_closed_for_month(request),           
    }
    return render(request, 'tickets/assigned_ticket.html', context)


@login_required
def started_list(request):
    branch = None
    team = None
    tickets = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, status='started')

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        tickets = Ticket.objects.filter(branch=branch, status='started')

    context = {
        'tickets': tickets,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),
        'ticket_closed_this_month': ticket_closed_for_month(request),            
    }
    return render(request, 'tickets/started_ticket.html', context)
    

@login_required
def deffered_list(request):
    branch = None
    team = None
    tickets = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, status='deffered')

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        tickets = Ticket.objects.filter(branch=branch, status='deffered')

    context = {
        'tickets': tickets,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),
        'ticket_closed_this_month': ticket_closed_for_month(request),   
    }
    return render(request, 'tickets/deffered_ticket.html', context)


@login_required
def reopened_list(request):
    branch = None
    team = None
    tickets = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, status='reopen')

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        tickets = Ticket.objects.filter(branch=branch, status='reopen')

    context = {
        'tickets': tickets,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),
        'ticket_closed_this_month': ticket_closed_for_month(request),   
    }
    return render(request, 'tickets/reopen_ticket.html', context)
    

@login_required
def closed_list(request):
    branch = None
    team = None
    ticket_obj = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        ticket_obj = Ticket.objects.filter(team=team, status='closed')

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        ticket_obj = Ticket.objects.filter(branch=branch, status='closed')

    page = request.GET.get('page', 1)
    paginator = Paginator(ticket_obj, 10)
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)

    context = {
        'protoheader': 'Closed Tickets',
        'tickets': tickets,
    }
    return render(request, 'tickets/closed_ticket.html', context)
    

@login_required
def ticket_detail(request, ticket_id):
    ticket = None
    branch = None
    team = None
    assignee = None
    resolution = None
    assignform = None
    assign_job = None
    incidence = None
    expiry = None
    assign_variance = None
    total_minutes = None
    deffered_count = None
    team_member = None
    assign_time_greater = None
    arrival_time_greater = None
    arrival_variance = None
    duration_end_time = None
    duration_start_time = None
    arrival_time = None
    created_time = None
    assign_time = None
    arrival_confirm = None

    if request.user.user_type == Customer.VENDOR:
        category = request.user.vendor_company.category
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        ticket = get_object_or_404(Ticket, pk=ticket_id, team=team, category=category)
        assignee = request.user.team_member.filter(pk=request.user.vendor.active_team_id, status=Team.ACTIVE)
        assignform = AssignForm(assignee, request.POST or None)

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        ticket = get_object_or_404(Ticket, pk=ticket_id, branch=branch)

    assign_job = AssignMember.objects.filter(ticket = ticket, ticket__status = 'assigned')
    if assign_job.count() > 0:
        resolution = assign_job.first()
        duration_start_time = resolution.created_at
        duration_end_time = resolution.arrival_time

    ticket_closed = AssignMember.objects.filter(ticket = ticket, ticket__status = 'closed')
    if ticket_closed.count() > 0:
        incidence = ticket_closed.first()

        created_time = incidence.ticket.created_at
        assign_time = incidence.ticket.arrival_time
        arrival_time = incidence.arrival_time
        arrival_confirm = incidence.arrival_confirm
        assign_variance = int(((assign_time - created_time)/60).seconds)
        total_minutes = incidence.total_minutes
        deffered_count = incidence.deffered_count
        team_member = incidence.assignee.get_full_name
        expiry = incidence.completion_time + timedelta(days=3)
        # STAGE ONE
        if (created_time + timedelta(minutes=10) >= assign_time):
            assign_time_greater = 'Swift'
        elif (created_time + timedelta(minutes=20) >= assign_time):
            assign_time_greater = 'Good'
        elif (created_time + timedelta(minutes=30) >= assign_time):
            assign_time_greater = 'Average'
        else:
            assign_time_greater = 'Poor'

        # STAGE TWO
        if arrival_confirm > arrival_time:
            arrival_variance = round(((arrival_confirm - arrival_time)/60).seconds)
            arrival_time_greater = 'Behind SLA'
        else:
            arrival_variance = round(((arrival_time - arrival_confirm)/60).seconds)
            arrival_time_greater = 'Within SLA'

    context = {
        'ticket': ticket,
        'checklist': Checklist.objects.all(),
        'assignform': assignform,
        'slaform': SLAExceptionsForm(),
        'resolution': resolution,
        'team_member': team_member,
        'expiry': expiry,
        'today': timezone.now(),
        'duration_start_time': duration_start_time,
        'duration_end_time': duration_end_time,
        'incidence': incidence,
        'created_time': created_time,
        'assign_time': assign_time,
        'assign_variance': assign_variance,
        'assign_time_greater': assign_time_greater,
        'arrival_time': arrival_time,
        'arrival_confirm': arrival_confirm,
        'arrival_variance': arrival_variance,
        'arrival_time_greater': arrival_time_greater,
        'total_minutes': total_minutes,
        'deffered_count': deffered_count, 
    }
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def ticket_preview(request, ticket_id, ticket_slug):
    ticket = None
    branch = None
    team = None
    expiry = None
    assignee = None
    resolution = None
    assignform = None
    assign_job = None
    incidence = None
    assign_variance = None
    total_minutes = None
    deffered_count = None
    team_member = None
    assign_time_greater = None
    arrival_time_greater = None
    arrival_variance = None
    duration_end_time = None
    duration_start_time = None
    arrival_time = None
    created_time = None
    assign_time = None
    arrival_confirm = None

    if request.user.user_type == Customer.VENDOR:
        category = request.user.vendor_company.category
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        ticket = get_object_or_404(Ticket, pk=ticket_id, team=team, slug=ticket_slug, category=category)
        assignee = request.user.team_member.filter(pk=request.user.vendor.active_team_id, status=Team.ACTIVE)
        assignform = AssignForm(assignee, request.POST or None)

    elif request.user.user_type == Customer.CUSTODIAN or request.user.user_type == Customer.ADMIN:
        branch = request.user.branch
        ticket = get_object_or_404(Ticket, pk=ticket_id, slug=ticket_slug, branch=branch)

    assign_job = AssignMember.objects.filter(ticket = ticket, ticket__status = 'assigned')
    if assign_job.count() > 0:
        resolution = assign_job.first()
        duration_start_time = resolution.created_at
        duration_end_time = resolution.arrival_time

    ticket_closed = AssignMember.objects.filter(ticket = ticket, ticket__status = 'closed')
    if ticket_closed.count() > 0:
        incidence = ticket_closed.first()

        created_time = incidence.ticket.created_at
        assign_time = incidence.ticket.arrival_time
        arrival_time = incidence.arrival_time
        arrival_confirm = incidence.arrival_confirm
        assign_variance = int(((assign_time - created_time)/60).seconds)
        total_minutes = incidence.total_minutes
        deffered_count = incidence.deffered_count
        team_member = incidence.assignee.get_full_name
        expiry = incidence.completion_time + timedelta(days=3)

        # STAGE ONE
        if (created_time + timedelta(minutes=10) >= assign_time):
            assign_time_greater = 'Swift'
        elif (created_time + timedelta(minutes=20) >= assign_time):
            assign_time_greater = 'Good'
        elif (created_time + timedelta(minutes=30) >= assign_time):
            assign_time_greater = 'Average'
        else:
            assign_time_greater = 'Poor'

        # STAGE TWO
        if arrival_confirm > arrival_time:
            arrival_variance = round(((arrival_confirm - arrival_time)/60).seconds)
            arrival_time_greater = 'Behind SLA'
        else:
            arrival_variance = round(((arrival_time - arrival_confirm)/60).seconds)
            arrival_time_greater = 'Within SLA'
     
    context = {
        'ticket': ticket,
        'checklist': Checklist.objects.all(),
        'assignform': assignform,
        'slaform': SLAExceptionsForm(),
        'resolution': resolution,
        'expiry': expiry,
        'today': timezone.now(),
        'team_member': team_member,
        'duration_start_time': duration_start_time,
        'duration_end_time': duration_end_time,
        'incidence': incidence,
        'created_time': created_time,
        'assign_time': assign_time,
        'assign_variance': assign_variance,
        'assign_time_greater': assign_time_greater,
        'arrival_time': arrival_time,
        'arrival_confirm': arrival_confirm,
        'arrival_variance': arrival_variance,
        'arrival_time_greater': arrival_time_greater,
        'total_minutes': total_minutes,
        'deffered_count': deffered_count,
    }
    return render(request, 'tickets/ticket_preview.html', context)


@login_required
@user_is_moderator
def assign_ticket(request, ticket_id): 
    team = None
    assignee = None
    assignform = None
    resolution = None
    duration_start_time = ''    
    duration_end_time = ''
    category = request.user.vendor_company.category    
    team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
    tickets = get_object_or_404(Ticket, pk=ticket_id, team=team, category=category, status="unassigned")
    assignee = request.user.team_member.filter(pk=request.user.vendor.active_team_id, status=Team.ACTIVE)

    assignform = AssignForm(assignee, request.POST or None)
    if not AssignMember.objects.filter(ticket=tickets).exists():
        if assignform.is_valid():
            assign = assignform.save(commit=False)
            assign.vendor = request.user.vendor_company
            assign.team = team
            assign.ticket = tickets
            assign.assignor = request.user
            assign.is_assigned = True
            if tickets.created_at > timezone.now():
                messages.error(request, f'Error! assign time must be ahead of creation time')
            else:
                assign.save()

                try:
                    Ticket.assign_and_predict(tickets.pk, assign.pk)
                    messages.info(request, 'Ticket assigned successfully!')
                except Exception as e:
                    messages.error(request, f'{e}')

        else:
            messages.error(request, 'Error! Please ensure to select assignee')
    else:
        messages.error(request, 'Ticket already assigned')

    ticket = tickets = get_object_or_404(Ticket, pk=ticket_id)
    assign_job = AssignMember.objects.filter(ticket = ticket)
    if assign_job.count() > 0:
        resolution = assign_job.first()
        duration_start_time = resolution.created_at
        duration_end_time = resolution.arrival_time

    context = {
        'ticket': ticket,  
        'assignform': assignform,
        'resolution': resolution,
        'slaform': SLAExceptionsForm(),
        'duration_end_time': duration_end_time,
        'duration_start_time': duration_start_time,
    }
    return render(request, 'tickets/partials/ticket_state.html', context)


@login_required
@user_is_custodian
@db_transaction.atomic
def confirm_arrival(request, ticket_id):
    branch = request.user.branch
    ticket = get_object_or_404(Ticket, pk=ticket_id, branch=branch)
    resolution = get_object_or_404(AssignMember, ticket=ticket)
    
    arrival = request.POST.get("arrivalconfirmed")

    if not arrival:
        messages.error(request, 'Unknown request')
    
    elif arrival and ticket.created_at > timezone.now():
        messages.error(request, f'Error! Arrival time must be ahead of assign time')
    
    elif arrival and ticket.arrival_time > timezone.now():
        messages.error(request, f'Error! You can only confirm after journey start time')
    
    else:
        resolution.arrival_confirm = timezone.now()
        resolution.save()

        ticket.status = 'started'
        ticket.arrival_time = timezone.now()
        ticket.save()

        mailgroup = get_mailing_group_with_branch(ticket.branch)

        if get_started_ticket_feature():
            try:
                ticket_ongoing_alert.delay(resolution.pk, mailgroup)
            except Exception as e:
                print(str(e))
        messages.info(request, 'Confirmed successfully!')

    context = {
        'ticket': ticket,
        'slaform': SLAExceptionsForm(),  
        'resolution': resolution,  
    }
    return render(request, 'tickets/partials/ticket_state.html', context)


@login_required
@user_is_custodian
def close_ticket(request, ticket_id):
    assign_variance = None
    total_minutes = None
    deffered_count = None
    team_member = None
    assign_time_greater = None
    arrival_time_greater = None
    arrival_variance = None
    duration_end_time = None
    duration_start_time = None
    arrival_time = None
    created_time = None
    assign_time = None
    arrival_confirm = None
    
    branch = request.user.branch
    ticket = get_object_or_404(Ticket, pk=ticket_id, branch=branch)
    assign = get_object_or_404(AssignMember, ticket=ticket)

    assign_check = AssignMember.objects.filter(Q(ticket__status ='started')| Q(ticket__status ='reopen')| Q(ticket__status = 'deffered'), ticket=ticket)

    if ticket.created_at > timezone.now():
        messages.error(request, f'Error! Closure time must be ahead of creation time')

    elif assign_check:        
        close = request.POST.get("closetask")
        closure = request.POST.getlist('closure')

        if close:
            
            if assign.ticket.status == 'deffered':
                assign.completion_time = timezone.now()
                assign.save()

            if assign.ticket.status == 'started':
                time_worked = timezone.now() - assign.arrival_confirm
                minutes = round(time_worked.seconds/60)
                assign.total_minutes += minutes
                assign.completion_time = timezone.now()
                assign.save()

            if assign.ticket.status == 'reopen':   
                time_worked = timezone.now() - assign.arrival_confirm
                minutes = round(time_worked.seconds/60)
                assign.total_minutes += minutes
                assign.completion_time = timezone.now()
                assign.save()

            for item in closure:
                ticket.checklist.add(item)
            
            ticket.status = 'closed'
            ticket.save()    

            created_time = assign.ticket.created_at
            assign_time = assign.ticket.arrival_time
            arrival_time = assign.arrival_time
            arrival_confirm = assign.arrival_confirm
            assign_variance = int(((assign_time - created_time)/60).seconds)
            total_minutes = assign.total_minutes
            deffered_count = assign.deffered_count
            team_member = assign.assignee.get_full_name
            
            # STAGE ONE
            if (created_time + timedelta(minutes=10) >= assign_time):
                assign_time_greater = 'Swift'
            elif (created_time + timedelta(minutes=20) >= assign_time):
                assign_time_greater = 'Good'
            elif (created_time + timedelta(minutes=30) >= assign_time):
                assign_time_greater = 'Average'
            else:
                assign_time_greater = 'Poor'

            # STAGE TWO
            if arrival_confirm > arrival_time:
                arrival_variance = round(((arrival_confirm - arrival_time)/60).seconds)
                arrival_time_greater = 'Breached SLA'
            else:
                arrival_variance = round(((arrival_time - arrival_confirm)/60).seconds)
                arrival_time_greater = 'Within SLA'

            mailgroup = get_mailing_group_with_branch(ticket.branch)
            if get_closed_ticket_feature():
                try:
                    ticket_closed_alert.delay(ticket.pk, mailgroup)
                except Exception as e:
                    print(str(e))                        
            messages.info(request, 'Ticket closed successfully!')
        else:
            messages.error(request, 'Error! please try again')

    else:
        messages.error(request, 'Error! You cannot close this ticket')

    context = {
        'ticket': ticket,
        'team_member': team_member,
        'duration_start_time': duration_start_time,
        'duration_end_time': duration_end_time,
        'created_time': created_time,
        'assign_time': assign_time,
        'assign_variance': assign_variance,
        'assign_time_greater': assign_time_greater,
        'arrival_time': arrival_time,
        'arrival_confirm': arrival_confirm,
        'arrival_variance': arrival_variance,
        'arrival_time_greater': arrival_time_greater,
        'total_minutes': total_minutes,
        'deffered_count': deffered_count,          
    }
    return render(request, 'tickets/partials/ticket_state.html', context)


@login_required
@user_is_vendor
def ticket_remark(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, status='closed')
    assign = get_object_or_404(AssignMember, ticket=ticket)
    
    new_remarks = request.POST.get('remarks')
    if not new_remarks:
        messages.error(request, 'Remarks is required!')
    
    elif not (assign.assignee == request.user or request.user.is_vendor):
        messages.error(request, 'Elevation required!')
    
    else:
        ticket.remarks = new_remarks
        ticket.remarks_date = timezone.now()
        ticket.save()

        mailgroup = get_mailing_group_with_branch(ticket.branch)
        if get_remarks_feature():
            ticket_remark_alert.delay(ticket.pk, mailgroup)

    expiry = assign.completion_time + timedelta(days=3)
    
    context = {
        'ticket': ticket,       
        'assign': assign,       
        'expiry': expiry,
        'today': timezone.now()      
    }
    return render(request, 'tickets/partials/ticket_remarks.html', context)


@login_required
@user_is_custodian
def deffer_ticket(request, ticket_id):
    branch = request.user.branch
    tickets = get_object_or_404(Ticket, pk=ticket_id, branch=branch)
    assigns = get_object_or_404(AssignMember, ticket=tickets)
    slaform = SLAExceptionsForm(request.POST or None)

    assign_check = AssignMember.objects.filter(Q(ticket__status ='started')| Q(ticket__status ='reopen'), ticket=tickets)
    
    if not assign_check:
        messages.error(request, 'You cannot pause this task')

    elif tickets.created_at > timezone.now():
        messages.error(request, f'Error! Closure time must be ahead of creation time')
    
    elif assigns.arrival_confirm > timezone.now():
        messages.error(request, f'Error! Arrival time must be ahead of closing time')
        
    else:
        deffer = request.POST.get("defferedtask")
        exception_pk = request.POST.get("name")

        if deffer and exception_pk:

            Ticket.defer_ticket(tickets.pk, assigns.pk, exception_pk)
            
            messages.info(request, 'Confirmed successfully!')
        else:
            messages.error(request, 'Error! please try again')

    ticket = get_object_or_404(Ticket, pk=ticket_id, branch=branch)
    assign = get_object_or_404(AssignMember, ticket=ticket)

    context = {
        'ticket': ticket,  
        'assign': assign,
        'slaform': slaform,
        'slaform': SLAExceptionsForm(),
        'resolution': assigns,  
    }
    return render(request, 'tickets/partials/ticket_state.html', context)


@login_required
@user_is_custodian
def reopen_ticket(request, ticket_id):
    branch = request.user.branch
    ticket = get_object_or_404(Ticket, pk=ticket_id, branch=branch)
    assign = get_object_or_404(AssignMember, ticket=ticket)
    
    assign_check = AssignMember.objects.filter(ticket=ticket, ticket__status ='deffered')
    if not assign_check:
        messages.error(request, 'You cannot reopen this task')
        pass
    else:
        deffer = request.POST.get("reopentask")
        if deffer:
            ticket.status = 'reopen'
            ticket.paused_by_system = False
            ticket.save()

            assign.arrival_confirm = timezone.now()
            assign.save()

            mailgroup = get_mailing_group(ticket.branch)
            if get_reopen_ticket_feature():
                try:
                    ticket_reopen_alert.delay(ticket.pk, mailgroup)
                except Exception as e:
                    print(str(e)) 
            messages.info(request, 'Confirmed successfully!')
        else:
            messages.error(request, 'Error! please try again')

    context = {
        'ticket': ticket,  
        'assign': assign,
        'slaform': SLAExceptionsForm(),
        'resolution': assign,  
    }
    return render(request, 'tickets/partials/ticket_state.html', context)


@login_required
@user_is_custodian
def recall_ticket(request):
    ticket_id = int(request.POST.get("recall"))
    branch = request.user.branch
    ticket = get_object_or_404(Ticket, pk=ticket_id, created_by = request.user, branch=branch)
    ticket.status = 'closed'
    ticket.save()

    mailgroup = get_mailing_group_with_branch(ticket.branch)
    print(mailgroup)
    ticket_recalled.delay(ticket.pk, mailgroup)

    tickets = Ticket.objects.filter(branch=branch).exclude(status = 'closed')

    context={
        'tickets':tickets
    }
    return render(request, 'tickets/partials/dashboard_tables.html', context)


@login_required
@user_is_vendor
def my_ticket_list(request):
    team = get_object_or_404(Team, pk=request.user.vendor.active_team_id)
    tickets = AssignMember.objects.filter(team=team, assignee=request.user).exclude(ticket__status='closed')

    context = {
        'protoheader': 'My Assigned Jobs',   
        'tickets': tickets,   
    }
    return render(request, 'tickets/my_tickets.html', context)


@login_required
def recommendations(request):
    branch = None
    team = None
    tickets = 0
    ticket_obj = None
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id)
        ticket_obj = Ticket.objects.filter(team=team, remarks__isnull=False, status='closed')

    elif request.user.user_type == Customer.CUSTODIAN and request.user.branch.inventory == False:
        branch = request.user.branch
        ticket_obj = Ticket.objects.filter(branch=branch, remarks__isnull=False, branch__inventory = False, status='closed')
    
    elif request.user.user_type == Customer.CUSTODIAN and request.user.branch.inventory == True:
        branch = request.user.branch
        ticket_obj = Ticket.objects.filter(remarks__isnull=False, status='closed')

    if ticket_obj is not None:
        page = request.GET.get('page', 1)
        paginator = Paginator(ticket_obj, 20)
        try:
            tickets = paginator.page(page)
        except PageNotAnInteger:
            tickets = paginator.page(1)
        except EmptyPage:
            tickets = paginator.page(paginator.num_pages)
    else:
        tickets = ticket_obj
    context = {
        'protoheader': 'Feedbacks',   
        'tickets': tickets,   
    }
    return render(request, 'tickets/recommendations.html', context)
    

@login_required
def search_recommendation(request):
    search_word = request.POST.get('search')
    
    if request.user.user_type == Customer.VENDOR:
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        
        tickets = Ticket.objects.filter(
            Q(remarks__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            team=team,
            status='closed'
        ).distinct()
    
    elif request.user.user_type == Customer.CUSTODIAN and request.user.branch.inventory == False:
        branch=request.user.branch
        
        tickets = Ticket.objects.filter(
            Q(remarks__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            branch=branch,
            branch__inventory = False,
            status='closed'
        ).distinct()

    elif request.user.user_type == Customer.CUSTODIAN and request.user.branch.inventory == True:
        branch=request.user.branch
        
        tickets = Ticket.objects.filter(
            Q(remarks__icontains = search_word)| 
            Q(reference__icontains = search_word)|
            Q(terminal__name__icontains = search_word),
            status='closed'
        ).distinct()

    context = {
        'tickets': tickets,   
    }
    return render(request, 'tickets/partials/recommendation.html', context)
