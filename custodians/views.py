from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Custodian, HelpDesk, HelpDeskMessage
from django.http.response import HttpResponse
from .forms import CustodianProfileForm, HelpDeskForm, RoutingForm, HelpDeskMessageForm, HelpDeskStatusForm
from account.decorators import user_is_moderator, user_is_vendor, user_is_custodian
from account.models import Customer
from general_settings.models import Branch, Category
from datetime import timedelta
from django.utils import timezone
from future.utilities import get_vendor_role_feature
from django.contrib import messages
from inventory.models import InventoryRequest
from django.db import transaction as db_transaction
from tickets.utilities import get_mailing_group, get_mailing_group_with_branch
from future.utilities import(
    get_complaint_created_feature,
    get_complaint_routing_feature,
    get_complaint_reply_feature
    # get_requisition_created_feature,
    # get_requisition_dispatched_feature,
    # get_requisition_confirm_feature
)
from .tasks import complaint_created_alert, complaint_routing_alert, complaint_reply_alert
from tickets.statistics import ongoing_ticket, user_time_worked_today, user_time_worked_lastweek, ticket_closed_for_month


@login_required
@user_is_custodian
def branch_page(request, branch_slug):
    branch = get_object_or_404(Branch, pk=request.user.branch.pk, slug=branch_slug)
    colleagues = branch.branch.all()
    complaints = None
    category = None

    title = request.POST.get("title")
    category_pk = int(request.POST.get("category", 0))
    condition = request.POST.get("condition")
    content = request.POST.get("content")
    file = request.FILES.get("file", None)

    if Category.objects.filter(pk=category_pk, meta=False).exists():
        category = get_object_or_404(Category, pk=category_pk, meta=False)

    if category is not None and title and condition and content:
        complaint = HelpDesk.objects.create(
            title=title, 
            category=category, 
            condition=condition, 
            content=content,
            request_branch=request.user.branch,
            created_by=request.user,
        )
        stan = f'{complaint.pk}'.zfill(4)
        complaint_br = f'{complaint.request_branch.pk}'
        complaint.reference = f'#{complaint_br}{stan}'
        complaint.save()

        if file is not None:
            complaint.file.save(file.name, file)

        mailgroup = get_mailing_group_with_branch(request.user.branch)

        if get_complaint_created_feature():
            complaint_created_alert.delay(complaint.pk, mailgroup)

    if request.user.branch.inventory == False:
        complaints = HelpDesk.objects.filter(request_branch=request.user.branch, status='active')
    elif request.user.branch.inventory == True:
        complaints = HelpDesk.objects.filter(status = 'active')
    
    context = {
        'branch':branch,
        'colleagues':colleagues,
        'complaints':complaints,
        'routingform':RoutingForm(),
        'helpform':HelpDeskForm(),
    }
    if request.htmx:
        return render(request, 'custodians/partials/complaints.html', context)
    return render(request, 'custodians/branch_detail.html', context)


@login_required
@user_is_custodian
def complaint_detail(request, request_id, request_slug):
    helpdesk = get_object_or_404(HelpDesk, pk=request_id, slug=request_slug)
    replies = helpdesk.deskreplies.all().order_by('-id')
    statusform = HelpDeskStatusForm(request.POST or None, instance=helpdesk)

    context = {
        'helpdesk':helpdesk,
        'replies':replies,
        'statusform':statusform,
        'helpform': HelpDeskMessageForm(request.POST or None),
        'routingform':RoutingForm(request.POST or None),
    }
    return render(request, 'custodians/manage_complaints.html', context)


@login_required
@user_is_custodian
def my_profile(request, short_name):
    user = get_object_or_404(Custodian, user=request.user, user__short_name=short_name)

    profileform = CustodianProfileForm(request.POST or None, instance=user)
    context = {
        "user": user,
        "profileform": profileform,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),
        'ticket_closed_this_month': ticket_closed_for_month(request),        
    }
    return render(request, 'custodians/my_profile.html', context)


@login_required
@user_is_custodian
def modify_profile(request, short_name):
    user = get_object_or_404(Custodian, user=request.user, user__short_name=short_name)
    gender = str(request.POST.get('gender'))
    tagline = str(request.POST.get('tagline'))
    address = str(request.POST.get('address'))
    description = str(request.POST.get('description'))

    user.gender = gender
    user.tagline = tagline
    user.address = address
    user.description = description
    user.save()

    messages.info(request, 'Profile modified successfully!')

    profileform = CustodianProfileForm(instance=user)
    context = {
        "user": user,
        "profileform": profileform,
    }
    return render(request, 'custodians/partials/profile_form.html', context)


@login_required
@user_is_custodian
def upload_photo(request, short_name):
    user = get_object_or_404(Custodian, user=request.user, user__short_name=short_name)
    profile_photo = request.FILES.get('profile_photo', None)

    if profile_photo == None:
        messages.error(request, 'Error! No new file detected!')
    else:
        user.profile_photo.save(profile_photo.name, profile_photo)

    context = {
        "user": user,
    }
    return render(request, 'custodians/partials/profile_photo.html', context)


@login_required
@user_is_custodian
def helpdesk_reply(request, request_id):
    helpdesk = get_object_or_404(HelpDesk, pk=request_id)
    status = request.POST.get('status')
    content = request.POST.get('content')

    if helpdesk.status == 'closed':
        messages.error(request, 'Error! Case already closed')    
    elif helpdesk.request_branch == request.user.branch or request.user.branch.inventory == True or helpdesk.support_branch == request.user.branch:
        if content:
            reply = HelpDeskMessage.objects.create(
                helpdesk=helpdesk, 
                content=content, 
                support=request.user
            )
            helpdesk.status = status
            helpdesk.save()

            mailgroup = get_mailing_group_with_branch(request.user.branch)

            if get_complaint_reply_feature():
                complaint_reply_alert.delay(reply.pk, mailgroup)

            messages.info(request, 'Response added!')
    
        else:
            messages.error(request, 'Message required')
    else:
        messages.error(request, 'Error! Request denied')

    replies = helpdesk.deskreplies.all().order_by('-id')

    context = {
        'replies':replies,
    }
    return render(request, 'custodians/partials/helpdesk_reply.html', context)


@login_required
@user_is_custodian
def route_to_branch(request, request_id):
    helpdesk = get_object_or_404(HelpDesk, pk=request_id)
    route_branch_pk = request.POST.get("support_branch")
    support_branch = None
    
    if Branch.objects.filter(pk=route_branch_pk).exists():
        support_branch = get_object_or_404(Branch, pk=route_branch_pk)
        
    if helpdesk.is_routed == False:
        helpdesk.support_branch = support_branch
        helpdesk.support_by = request.user
        helpdesk.is_routed = True
        helpdesk.save()

        mailgroup = get_mailing_group_with_branch(request.user.branch)

        if get_complaint_routing_feature():
            complaint_routing_alert.delay(helpdesk.pk, mailgroup)

        messages.info(request, 'We shall notify the unit!')
    else:
        helpdesk.is_routed = False
        helpdesk.save()

    statusform = HelpDeskStatusForm(request.POST or None, instance=helpdesk)
    complaints = HelpDesk.objects.filter(request_branch = request.user.branch, status = 'active')
    
    context = {
        'statusform':statusform,
        'helpdesk':helpdesk,
        'complaints':complaints,
        'routingform':RoutingForm(),
        'helpform':HelpDeskForm(),
    }

    return render(request, 'custodians/partials/routing_or_reply.html', context)

