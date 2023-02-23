from django.shortcuts import render, get_object_or_404, redirect
from account.decorators import user_is_moderator, user_is_vendor, user_is_custodian
from django.contrib.auth.decorators import login_required
from account.models import Customer
from django.http import HttpResponse, JsonResponse
from tickets.models import Ticket, AssignMember
from account.exception import TicketException
from general_settings.models import Category, Terminals, Branch
from vendors.models import Team
from django.db.models import Q
from django.contrib import messages
from django.db import transaction as db_transaction
from datetime import timedelta
from django.utils import timezone
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .analytics import (
    today_vendor_ticket_count,
    today_vendor_unassign_ticket,
    today_vendor_assigned_ticket,
    today_vendor_started_ticket,
    today_vendor_deffered_ticket,
    today_vendor_closed_ticket,
    weekly_vendor_ticket_count,
    weekly_vendor_unassign_ticket,
    weekly_vendor_assigned_ticket,
    weekly_vendor_started_ticket,
    weekly_vendor_deffered_ticket,
    weekly_vendor_closed_ticket,
    dual_weekly_vendor_ticket_count,
    dual_weekly_vendor_unassign_ticket,
    dual_weekly_vendor_assigned_ticket,
    dual_weekly_vendor_started_ticket,
    dual_weekly_vendor_deffered_ticket,
    dual_weekly_vendor_closed_ticket,
)

from .forms import ExcelCsvForm, CustomExcelCsvForm, AllBranchesForm, SearchVendorForm, VendorCompareForm
from general_settings.models import VendorCompany
from . resources import TicketResource
from .reports import (
    vendor_time_worked, 
    closed_ticket_count,
    unassigned_ticket_count,
    assigned_ticket_count,
    started_ticket_count,
    deffered_ticket_count,
    reopen_ticket_count,
    total_ticket,
    average_response
)


@login_required
def ticket_by_vendor(request):
    vendors = VendorCompany.objects.filter(status=True)
    today = timezone.now()
    month_end = timezone.now() - timedelta(days=90)
    initial_vendor = VendorCompany.objects.filter(status=True).first()
    vendor_pk = int(request.POST.get('name', initial_vendor.pk))
    
    start_date = request.POST.get('start_date', today)
    end_date = request.POST.get('end_date', month_end)
    size = int(request.POST.get('size', 10000))

    selected_vendor = get_object_or_404(VendorCompany, pk=vendor_pk)

    tickets = Ticket.objects.filter(
        terminal__vendor = selected_vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).order_by("pk").reverse()[:size]

    context = {
        'protoheader': 'Vendor Insight', 
        'vendorform': SearchVendorForm(), 
        'vendors': vendors, 
        'tickets': tickets,
        'size': size, 
        'month_end': month_end, 
    }
    if request.htmx:
        return render(request, 'reports/partials/insight_by_vendor.html', context)
    return render(request, 'reports/insight_by_vendor.html', context)


@login_required
def ticket_by_status(request):
    today = timezone.now()
    month_end = timezone.now() - timedelta(days=90)
    initial_vendor = VendorCompany.objects.filter(status=True).first()
    vendor_pk = int(request.POST.get('name', initial_vendor.pk))
    
    start_date = request.POST.get('start_date', today)
    end_date = request.POST.get('end_date', month_end)
    status = str(request.POST.get('status'))

    selected_vendor = get_object_or_404(VendorCompany, pk=vendor_pk)

    tickets = Ticket.objects.filter(
        terminal__vendor = selected_vendor, created_at__date__gte=start_date,
        created_at__date__lte=end_date, status=status
    ).order_by("pk").reverse()

    context = {
        'protoheader': 'Vendor Insight', 
        'vendorform': SearchVendorForm(), 
        'tickets': tickets,
        'month_end': month_end, 
    }

    if request.htmx:
        return render(request, 'reports/partials/insight_by_vendor.html', context)
    return render(request, 'reports/insight_by_status.html', context)


@login_required
def ticket_by_vendor_comparison(request):
    today = timezone.now()
    month_end = timezone.now()
    
    vendorone = int(request.POST.get('vendorone', 0))
    vendortwo = int(request.POST.get('vendortwo', 0))    
    start_date = request.POST.get('start_date', today)
    end_date = request.POST.get('end_date', month_end)

    vendor_one = None
    vendor_two = None
    v1 = VendorCompany.objects.filter(pk=vendorone)
    v2 = VendorCompany.objects.filter(pk=vendortwo)
    if v1.exists():
        vendor_one = get_object_or_404(VendorCompany, pk=vendorone)
    if v2.exists():
        vendor_two = get_object_or_404(VendorCompany, pk=vendortwo)

    # total Tickets by period
    total_ticket_v1 = total_ticket(vendor_one, start_date, end_date)
    total_ticket_v2 = total_ticket(vendor_two, start_date, end_date)
    
    # total Tickets by vendor closed within period
    closed_ticket_v1 = closed_ticket_count(vendor_one, start_date, end_date)
    closed_ticket_v2 = closed_ticket_count(vendor_two, start_date, end_date)
    
    # total Tickets by vendor Unassigned within period
    unassigned_ticket_v1 = unassigned_ticket_count(vendor_one, start_date, end_date)
    unassigned_ticket_v2 = unassigned_ticket_count(vendor_two, start_date, end_date)
    
    # total Tickets by vendor assigned within period
    assigned_ticket_v1 = assigned_ticket_count(vendor_one, start_date, end_date)
    assigned_ticket_v2 = assigned_ticket_count(vendor_two, start_date, end_date)
    
    # total Tickets by vendor started within period
    started_ticket_v1 = started_ticket_count(vendor_one, start_date, end_date)
    started_ticket_v2 = started_ticket_count(vendor_two, start_date, end_date)
    
    # total Tickets by vendor deffered within period
    deffered_ticket_v1 = deffered_ticket_count(vendor_one, start_date, end_date)
    deffered_ticket_v2 = deffered_ticket_count(vendor_two, start_date, end_date)
    
    # total Tickets by vendor reopen within period
    reopen_ticket_v1 = reopen_ticket_count(vendor_one, start_date, end_date)
    reopen_ticket_v2 = reopen_ticket_count(vendor_two, start_date, end_date)

    # total time worked until closed by vendor within period
    time_worked_v1 = round(vendor_time_worked(vendor_one, start_date, end_date))
    time_worked_v2 = round(vendor_time_worked(vendor_two, start_date, end_date))
    
    # total of started and ongoing tickets
    ongoing_ticket_v1 = started_ticket_v1 + reopen_ticket_v1
    ongoing_ticket_v2 = started_ticket_v2 + reopen_ticket_v2

    v1_response = average_response(vendor_one, start_date, end_date)
    v2_response = average_response(vendor_two, start_date, end_date)
    default=0
    v1_assign_to_arrival = v1_response['arrival']
    v1_open_to_assign = v1_response['unassigned']

    v2_assign_to_arrival = v2_response['arrival']
    v2_open_to_assign = v2_response['unassigned']

    if v1_assign_to_arrival == None:
        v1_assign_to_arrival = default
    else:
        v1_assign_to_arrival = round((v1_response['arrival'].seconds/60))

    if v1_open_to_assign == None:
        v1_open_to_assign = default
    else:
        v1_open_to_assign = round((v1_response['unassigned'].seconds/60))

    if v2_assign_to_arrival == None:
        v2_assign_to_arrival = default
    else:
        v2_assign_to_arrival = round((v2_response['arrival'].seconds/60))

    if v2_open_to_assign == None:
        v2_open_to_assign = default
    else:
        v2_open_to_assign = round((v2_response['unassigned'].seconds/60))

    context = { 
        'protoheader': 'Vendor Analytics',
        'vendorform': VendorCompareForm(),
        'vendor_one': vendor_one, 
        'vendor_two': vendor_two, 
        'time_worked_v1': time_worked_v1, 
        'time_worked_v2': time_worked_v2, 
        'closed_ticket_v1': closed_ticket_v1, 
        'closed_ticket_v2': closed_ticket_v2, 
        'unassigned_ticket_v1': unassigned_ticket_v1, 
        'unassigned_ticket_v2': unassigned_ticket_v2, 
        'assigned_ticket_v1': assigned_ticket_v1, 
        'assigned_ticket_v2': assigned_ticket_v2, 
        'started_ticket_v1': started_ticket_v1, 
        'started_ticket_v2': started_ticket_v2, 
        'deffered_ticket_v1': deffered_ticket_v1, 
        'deffered_ticket_v2': deffered_ticket_v2, 
        'reopen_ticket_v1': reopen_ticket_v1, 
        'reopen_ticket_v2': reopen_ticket_v2, 
        'ongoing_ticket_v1': ongoing_ticket_v1, 
        'ongoing_ticket_v2': ongoing_ticket_v2, 
        'total_ticket_v1': total_ticket_v1, 
        'total_ticket_v2': total_ticket_v2,
        'v1_assign_to_arrival':v1_assign_to_arrival,
        'v1_open_to_assign':v1_open_to_assign,
        'v2_assign_to_arrival':v2_assign_to_arrival,
        'v2_open_to_assign':v2_open_to_assign,         
    }

    if request.htmx:
        return render(request, 'reports/partials/insight_by_vendor_compare.html', context)
    return render(request, 'reports/insight_by_vendor_compare.html', context)


@login_required
def ticket_by_hours_worked(request):
    today = timezone.now()
    yesterday = timezone.now() - timedelta(days=1)
    initial_vendor = VendorCompany.objects.filter(status=True).first()
    vendor_pk = int(request.POST.get('name', initial_vendor.pk))
    
    start_date = request.POST.get('start_date', today)
    end_date = request.POST.get('end_date', yesterday)
    hours = int(request.POST.get('hours', 0))
    minutes = int(request.POST.get('minutes', 0))
    benchmark_time = int((hours * 60) + minutes)

    selected_vendor = get_object_or_404(VendorCompany, pk=vendor_pk)

    tickets = AssignMember.objects.filter(
        vendor = selected_vendor, 
        created_at__date__gte=start_date,
        created_at__date__lte=end_date, 
        ticket__status = 'closed',
        total_minutes__gte=benchmark_time        
    )

    context = {
        'protoheader': 'Assign Response', 
        'vendorform': SearchVendorForm(), 
        'tickets': tickets,
        'today': today, 
        'yesterday': yesterday, 
    }
    if request.htmx:
        return render(request, 'reports/partials/insight_by_hours_worked.html', context)
    return render(request, 'reports/insight_by_hours_worked.html', context)


@login_required
def ticket_by_response(request):
    today = timezone.now()
    yesterday = timezone.now() - timedelta(days=1)
    initial_vendor = VendorCompany.objects.filter(status=True).first()
    vendor_pk = int(request.POST.get('name', initial_vendor.pk))
    
    selected_vendor = get_object_or_404(VendorCompany, pk=vendor_pk)
    start_date = request.POST.get('start_date', today)
    end_date = request.POST.get('end_date', yesterday)

    tickets = AssignMember.objects.filter(
        vendor = selected_vendor, 
        ticket__created_at__date__gte=start_date,
        ticket__created_at__date__lte=end_date,
        ticket__status = 'closed',
    )

    context = {
        'protoheader': 'Assign Response', 
        'vendorform': SearchVendorForm(), 
        'tickets': tickets,
        'today': today, 
        'yesterday': yesterday, 
    }
    if request.htmx:
        return render(request, 'reports/partials/insight_by_response.html', context)
    return render(request, 'reports/insight_by_response.html', context)


@login_required
def monitor(request):
    team = get_object_or_404(Team, pk=request.user.vendor.active_team_id)   
    today=timezone.now()
    week_from=timezone.now().date() - timedelta(days=7)
    week_to=timezone.now().date() - timedelta(days=1)
    dual_week_from=timezone.now().date() - timedelta(days=15)
    dual_week_to=timezone.now().date() - timedelta(days=8)

    context = {
        'today': today, 
        'week_from': week_from, 
        'week_to': week_to, 
        'dual_week_from': dual_week_from, 
        'dual_week_to': dual_week_to, 
        'today_ticket_count': today_vendor_ticket_count(team), 
        'today_unassign_ticket': today_vendor_unassign_ticket(team), 
        'today_assign_ticket': today_vendor_assigned_ticket(team), 
        'today_started_ticket': today_vendor_started_ticket(team), 
        'today_deffered_ticket': today_vendor_deffered_ticket(team), 
        'today_closed_ticket': today_vendor_closed_ticket(team), 
        'weekly_ticket_count': weekly_vendor_ticket_count(team), 
        'weekly_unassign_ticket': weekly_vendor_unassign_ticket(team), 
        'weekly_assign_ticket': weekly_vendor_assigned_ticket(team), 
        'weekly_started_ticket': weekly_vendor_started_ticket(team), 
        'weekly_deffered_ticket': weekly_vendor_deffered_ticket(team), 
        'weekly_closed_ticket': weekly_vendor_closed_ticket(team), 
        'dual_weekly_ticket_count': dual_weekly_vendor_ticket_count(team), 
        'dual_weekly_unassign_ticket': dual_weekly_vendor_unassign_ticket(team), 
        'dual_weekly_assign_ticket': dual_weekly_vendor_assigned_ticket(team), 
        'dual_weekly_started_ticket': dual_weekly_vendor_started_ticket(team), 
        'dual_weekly_deffered_ticket': dual_weekly_vendor_deffered_ticket(team), 
        'dual_weekly_closed_ticket': dual_weekly_vendor_closed_ticket(team), 

    }
    if request.htmx:
        return render(request, 'reports/partials/monitor.html', context)

    return render(request, 'reports/monitor.html', context)


@login_required
def excel_or_csv(request):
    context = {
        'protoheader': 'Download Report', 
        'excelcsvform': ExcelCsvForm(), 
    }
    return render(request, 'reports/excel_or_csv.html', context)


@login_required
def custom_excel_or_csv(request):
    context = {
        'protoheader': 'Custom Report', 
        'vendorform': CustomExcelCsvForm(), 
    }
    return render(request, 'reports/custom_excel_or_csv.html', context)


@login_required
def branches_excel_or_csv(request):
    context = {
        'protoheader': 'All Branches Report', 
        'vendorform': AllBranchesForm(), 
    }
    return render(request, 'reports/all_branches.html', context)


@login_required
def fetch_excel_or_csv(request):
    ticket_resource = TicketResource()
    today = timezone.now()
    last_week = timezone.now() - timedelta(days=7)  
    download_type = request.POST.get('download_type')
    start_date = request.POST.get('start_date', last_week)
    end_date = request.POST.get('end_date', today)
    size = int(request.POST.get('size', 10000))

    tickets = Ticket.objects.filter(
        branch=request.user.branch,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
        )[:size]
    
    dataset = ticket_resource.export(tickets)
    if download_type == 'excel':
        response = HttpResponse(dataset.xls, content_type='text/xls')
        response['Content-Disposition'] = 'attachment; filename="ticket_report.xls"'
    else:
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ticket_report.csv"'
    return response


@login_required
def fetch_allbranches(request):
    ticket_resource = TicketResource()
    today = timezone.now()
    last_week = timezone.now() - timedelta(days=7)  
    download_type = request.POST.get('download_type')
    start_date = request.POST.get('start_date', last_week)
    end_date = request.POST.get('end_date', today)

    tickets = Ticket.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )
    
    dataset = ticket_resource.export(tickets)
    if download_type == 'excel':
        response = HttpResponse(dataset.xls, content_type='text/xls')
        response['Content-Disposition'] = 'attachment; filename="ticket_report.xls"'
    else:
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ticket_report.csv"'
    return response


@login_required
def custom_fetch_excel_or_csv(request):
    ticket_resource = TicketResource()
    today = timezone.now()
    last_week = timezone.now() - timedelta(days=7)  
    branch_pk = request.POST.get('branch')
    vendor_pk = request.POST.get('vendor')
    download_type = request.POST.get('download_type')
    start_date = request.POST.get('start_date', last_week)
    end_date = request.POST.get('end_date', today)
    size = int(request.POST.get('size', 10000))
    
    selected_branch = get_object_or_404(Branch, pk=branch_pk, status=True)
    selected_vendor = get_object_or_404(VendorCompany, pk=vendor_pk, status=True)
    selected_team = get_object_or_404(Team, title=selected_vendor, status='active')

    tickets = Ticket.objects.filter(
        branch=selected_branch,
        team=selected_team,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
        )[:size]

    print(tickets)

    dataset = ticket_resource.export(tickets)
    if download_type == 'excel':
        response = HttpResponse(dataset.xls, content_type='text/xls')
        response['Content-Disposition'] = 'attachment; filename="ticket_report.xls"'
    else:
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ticket_report.csv"'
    return response


# @login_required
# def generatePdf(request):

#     tickets = Ticket.objects.all()
#     context = {
#         'tickets': tickets, 
#     }
#     pdf = render_to_pdf('reports/analytics.html', context)
#     return HttpResponse(pdf, content_type='application/pdf')


