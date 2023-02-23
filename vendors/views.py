from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor, Team, TeamChat
from django.http.response import HttpResponse
from .forms import TeamChatForm, VendorProfileForm
from account.decorators import user_is_moderator, user_is_vendor, user_is_custodian
from account.models import Customer
from datetime import timedelta
from django.utils import timezone
from future.utilities import get_vendor_role_feature
from tickets.models import Ticket, AssignMember
from django.contrib import messages
from .analytics import (
    today_vendor_ticket_count,
    assigned_ticket_count,
    ongoing_ticket_count,
    deffered_ticket_count,
    unassigned_ticket_count,
    mytoday_ticket_count,
    mytoday_paused_count,
    mytoday_ongoing_count,
    mytoday_closed_count,
    mytoday_assigned_count,
)
from tickets.statistics import ongoing_ticket, user_time_worked_today, user_time_worked_lastweek, ticket_closed_for_month


@login_required
def vendor_profile(request, short_name):
    vendor_team = get_object_or_404(Vendor, user__short_name=short_name)
    team = get_object_or_404(Team, pk=vendor_team.active_team_id)
    member = AssignMember.objects.filter(team=team, assignee=vendor_team.user).count()
    
    unassign_count = unassigned_ticket_count(team)
    assign_count = assigned_ticket_count(team, vendor_team.user)
    ongoing_count = ongoing_ticket_count(team, vendor_team.user)
    deffered_count = deffered_ticket_count(team, vendor_team.user)
    
    # Actually represents data for weekly tickets ending today
    today_ticket_count = today_vendor_ticket_count(team)
    mytoday_count = mytoday_ticket_count(team, vendor_team.user)

    if today_ticket_count == 0:
        today_percent = 0
    else:
        today_percent = round((mytoday_count/today_ticket_count)*100)

    today_deffered_count = mytoday_paused_count(team, vendor_team.user)
    if mytoday_count == 0:
        today_paused_percent = 0
    else:    
        today_paused_percent = round((today_deffered_count/mytoday_count)*100)

    today_ongoing_count = mytoday_ongoing_count(team, vendor_team.user)
    if mytoday_count == 0:
        today_ongoing_percent = 0
    else:    
        today_ongoing_percent = round((today_ongoing_count/mytoday_count)*100)
    
    today_closed_count = mytoday_closed_count(team, vendor_team.user)
    if mytoday_count == 0:
        today_closed_percent = 0
    else: 
        today_closed_percent = round((today_closed_count/mytoday_count)*100)
    
    today_assigned_count = mytoday_assigned_count(team, vendor_team.user)
    if mytoday_count == 0:
        today_assigned_percent = 0
    else:
        today_assigned_percent = round((today_assigned_count/mytoday_count)*100)
   
    week_from = timezone.now().date() - timedelta(days=7)
    today = timezone.now()
    
    context = {
        'member':member,
        'vendor_team':vendor_team,
        'unassign_count':unassign_count,
        'assign_count':assign_count,
        'ongoing_count':ongoing_count,
        'deffered_count':deffered_count,
        'today_ticket_count':today_ticket_count,
        'mytoday_count':mytoday_count,
        'today_percent':today_percent,
        'today_deffered_count':today_deffered_count,
        'today_paused_percent':today_paused_percent,
        'today_ongoing_count':today_ongoing_count,
        'today_ongoing_percent':today_ongoing_percent,
        'today_closed_count':today_closed_count,
        'today_closed_percent':today_closed_percent,
        'today_assigned_count':today_assigned_count,
        'today_assigned_percent':today_assigned_percent,
        'today':today,
        'week_from':week_from
    }
    return render(request, 'vendors/profile_detail.html', context)


@login_required
@user_is_vendor
def my_profile(request, short_name):
    user = get_object_or_404(Vendor, user=request.user, user__short_name=short_name)
    profileform = VendorProfileForm(request.POST or None, instance=user)
    context = {
        "user": user,
        "profileform": profileform,
        'ongoing_ticket': ongoing_ticket(request), 
        'user_time_today': user_time_worked_today(request), 
        'user_time_lastweek': user_time_worked_lastweek(request),
        'ticket_closed_this_month': ticket_closed_for_month(request),        
    }
    return render(request, 'vendors/my_profile.html', context)


@login_required
@user_is_vendor
def modify_profile(request, short_name):
    user = get_object_or_404(Vendor, user=request.user, user__short_name=short_name)
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

    profileform = VendorProfileForm(instance=user)
    context = {
        "user": user,
        "profileform": profileform,
    }
    return render(request, 'vendors/partials/profile_form.html', context)


@login_required
@user_is_vendor
def upload_photo(request, short_name):
    user = get_object_or_404(Vendor, user=request.user, user__short_name=short_name)
    profile_photo = request.FILES.get('profile_photo', None)

    if profile_photo == None:
        messages.error(request, 'Error! No new file detected!')
    else:
        user.profile_photo.save(profile_photo.name, profile_photo)

    context = {
        "user": user,
    }
    return render(request, 'vendors/partials/profile_photo.html', context)


@login_required
@user_is_vendor
def vendor_detail(request, vendor_slug):
    teams = get_object_or_404(Team, pk=request.user.vendor.active_team_id, slug=vendor_slug, status=Team.ACTIVE, members__in=[request.user])
    vendor_role = get_vendor_role_feature()

    context = {
        "teams": teams,
        "vendor_role": vendor_role
    }
    return render(request, 'vendors/team_detail.html', context)


@login_required
@user_is_vendor
def vendor_upgrade_downgrade(request):
    teams = get_object_or_404(Team, pk=request.user.vendor.active_team_id, status=Team.ACTIVE, members__in=[request.user])

    member_pk = int(request.POST.get('upgradeMember'))
    if member_pk and get_vendor_role_feature():

        member = get_object_or_404(Customer, pk=member_pk, is_active=True)
        
        if member == request.user:
            messages.error(request, 'Forbidden!. You cannot modify your own role.')

        elif member.is_vendor == True:
            member.is_vendor = False
            member.save()            
            messages.info(request, 'Member downgraded successfully!')

        elif member.is_vendor == False:
            member.is_vendor = True
            member.save()
            messages.info(request, 'Member upgraded successfully!')
  
        else:
            messages.error(request, 'Error! Ensure user has confirmed signup')    
    else:
        messages.error(request, 'Error! Ensure user has confirmed signup')    

    context = {
        "teams": teams,
        "vendor_role": get_vendor_role_feature()
    }
    return render(request, 'vendors/partials/vendor_list.html', context)


@login_required
@user_is_vendor
def teamchat(request):
    team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, status=Team.ACTIVE, members__in=[request.user])
    content = request.POST.get('content', '')

    if content != '':
        TeamChat.objects.create(content=content, team=team, sender=request.user, is_sent=True)

    chats = team.teamchats.all()
    return render(request, 'vendors/partials/team_message.html', {'chats': chats})


@login_required
@user_is_vendor
def teamchatroom(request):
    team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, status=Team.ACTIVE)
    chats = team.teamchats.all()
    admin = Customer.objects.filter(user_type=Customer.ADMIN, is_active=True, is_staff=True).first()
    
    if request.htmx:
        return render(request, 'vendors/partials/team_message.html', {'chats': chats})
    else:
        return render(request, 'vendors/active_team_chat.html', {'chats': chats, 'admin': admin, 'date_and_time': timezone.now()})

