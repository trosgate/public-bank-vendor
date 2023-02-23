from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.views.decorators.cache import cache_control
from django.db import transaction as db_transaction
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Customer, TwoFactorAuth
from .forms import (
    SearchTypeForm, VendorCreationForm, UserLoginForm, 
    TwoFactorAuthForm, VendorPasswordForm
)
from general_settings.utilities import homepage_layout
from general_settings.models import Category
from .tokens import account_activation_token
from vendors.models import Team, Vendor
from django.db import transaction as db_transaction
from .decorators import user_is_moderator
from .tasks import invitation_to_team, two_factor_auth_mailer
from future.utilities import get_token_feature
from django.views.decorators.http import require_http_methods
from tickets.forms import TicketForm
from tickets.models import Ticket
from onboarding.models import Tender, Application, Grading
from django.utils import timezone



@login_required
def Logout(request):
    logout(request)
    return redirect('account:homepage')


@login_required
def autologout(request):
    logout(request)
    return redirect('account:homepage')


def homepage(request):
    if request.user.is_authenticated and request.user.user_type == Customer.VENDOR:
        return redirect('account:dashboard')

    if request.user.is_authenticated and request.user.is_staff and "/" in request.path:
        return redirect('account:dashboard')

    if not 'admin' in request.path and request.user.is_authenticated and request.user.user_type == Customer.ADMIN and request.user.is_superuser == True:
        return redirect('account:dashboard')

    if 'admin' in request.path and request.user.is_authenticated and request.user.user_type == Customer.ADMIN and request.user.is_superuser == True:
        return redirect('/admin')

    searchform = SearchTypeForm()
    home_layout = homepage_layout()

    loginform = UserLoginForm()

    context = {
        'searchform': searchform,        
        'home_layout': home_layout,        
        'loginform': loginform,        
        'userloginmodal': 'userloginmodal'      
    }
    return render(request, 'homepage.html', context)


@require_http_methods(['POST'])
def loginView(request):

    session = request.session
    user_redirect_url = f"{'http://'}{str(get_current_site(request))}/dashboard",
    user_auth_url = f"{'http://'}{str(get_current_site(request))}/account/two-factor-auth/",
    
    if request.POST.get('action') == 'login-now':
        email = str(request.POST.get('emailid'))
        password = str(request.POST.get('PassworD'))

        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.user_type == Customer.VENDOR and user.is_active == True and user.is_staff == False:
                
            login(request, user)

            messages.info(request, f'Welcome back {user.short_name}')
            response = JsonResponse({'errors':'', 'redirect_url':user_redirect_url,}, safe=False)
            return response

        elif user is not None and user.user_type == Customer.CUSTODIAN and user.is_staff == True and user.is_active == True and user.is_superuser == False and not get_token_feature():
                
            login(request, user)

            messages.info(request, f'Welcome back {user.short_name}')
            response = JsonResponse({'errors':'', 'redirect_url':user_redirect_url,}, safe=False)
            return response
        
        elif user is not None and user.user_type == Customer.CUSTODIAN and user.is_staff == True and user.is_active == True and user.is_superuser == False and get_token_feature():
                
            if "twofactoruser" not in session:
                session["twofactoruser"] = {"user_pk": user.pk}
                session.modified = True
                response = JsonResponse({'errors':'', 'redirect_url':user_auth_url,}, safe=False)
                return response
            response = JsonResponse({'errors':'', 'redirect_url':user_auth_url,}, safe=False)
            return response

        elif user is not None and user.is_staff == True and user.is_active == True and user.is_stakeholder == True and not get_token_feature():
                
            login(request, user)

            messages.info(request, f'Welcome back {user.short_name}')
            response = JsonResponse({'errors':'', 'redirect_url':user_redirect_url,}, safe=False)
            return response

        elif user is not None and user.is_staff == True and user.is_active == True and user.is_stakeholder == True and get_token_feature():
                
            if "twofactoruser" not in session:
                session["twofactoruser"] = {"user_pk": user.pk}
                session.modified = True
                response = JsonResponse({'errors':'', 'redirect_url':user_auth_url,}, safe=False)
                return response
            response = JsonResponse({'errors':'', 'redirect_url':user_auth_url,}, safe=False)
            return response

        elif not "admin" in request.path and user is not None and user.user_type == Customer.ADMIN and user.is_staff == True and user.is_active == True and user.is_superuser == True and not get_token_feature():
                
            login(request, user)

            messages.info(request, f'Welcome back {user.short_name}')
            response = JsonResponse({'errors':'', 'redirect_url':user_redirect_url,}, safe=False)
            return response
        
        elif not "admin" in request.path and user is not None and user.user_type == Customer.ADMIN and user.is_staff == True and user.is_active == True and user.is_superuser == True and get_token_feature():
                
            if "twofactoruser" not in session:
                session["twofactoruser"] = {"user_pk": user.pk}
                session.modified = True
                response = JsonResponse({'errors':'', 'redirect_url':user_auth_url,}, safe=False)
                return response
            response = JsonResponse({'errors':'', 'redirect_url':user_auth_url,}, safe=False)
            return response

        else:
            response = JsonResponse({'errors':'Error! Email or Password incorect'}, safe=False)
            return response


def two_factor_auth(request):
    if "twofactoruser" not in request.session:
        return redirect("/")

    try:
        returned_user_pk = request.session["twofactoruser"]["user_pk"]
        returned_user = TwoFactorAuth.objects.get(user__pk=returned_user_pk, user__is_active=True)
        pass_code = returned_user.pass_code
        user = Customer.objects.get(pk=returned_user_pk, is_active=True)
    except:
        returned_user=None
        user=None
        return redirect("/")

    twofactorform = TwoFactorAuthForm(request.POST or None)

    if not request.POST:
        try:
            two_factor_auth_mailer.delay(user.pk, pass_code)
        except:
            print('Activation token not sent')
   
    if twofactorform.is_valid():
        received_code = twofactorform.cleaned_data['pass_code']

        if pass_code == received_code:
            returned_user.save()

            login(request, user)

            messages.info(request, f'Welcome back {request.user.short_name}')

            return redirect("account:dashboard")

        messages.error(request, 'Invalid code!')
    else:
        messages.error(request, 'Invalid code!')

    context = {
        'twofactorform': twofactorform
    }
    return render(request, "account/two_factor_auth.html", context)


@login_required
@user_is_moderator
@db_transaction.atomic
def account_register(request):
    team = get_object_or_404(Team, pk=request.user.vendor.active_team_id)
    if request.POST.get('action') == 'register-now':
        first_name = str(request.POST.get('first_name'))
        last_name = str(request.POST.get('last_name'))
        short_name = str(request.POST.get('short_name'))
        email = request.POST.get('email')
        phone = str(request.POST.get('phone'))

        if Customer.objects.filter(Q(email__icontains=email)|Q(short_name__icontains=short_name)).exists():
            return JsonResponse({'errors':'User with provided email or username already exists'}, safe=False)
        
        user = Customer.objects.create(
            first_name=first_name, last_name=last_name,
            short_name=short_name, email=email, phone=phone
        )
        user.vendor_company = request.user.vendor_company
        user.user_type = 'vendor'
        user.is_active = False
        user.save()
        team.members.add(user)
            
        Vendor.objects.create(
            user=user, 
            active_team_id=team.pk
        )
        
        moderator = f'{request.user.get_full_name()}<{request.user.email}'
        
        db_transaction.on_commit(lambda: invitation_to_team.delay(user.pk, team.pk, moderator))

        return JsonResponse({'errors':'', 'message':'User invited Successfully'}, safe=False)


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, request.user.DoesNotExist):
        user = None
    
    session = request.session
    if user is not None and account_activation_token.check_token(user, token):      

        if "vendorpassword" not in session:
            session["vendorpassword"] = {"user_id": user.id}
            session.modified = True
        else:
            session["vendorpassword"]["user_id"] = user.id
            session.modified = True

        return redirect('account:password_creation')

    else:
        return render(request, 'account/registration/register_activation_invalid.html')


def password_creation(request):
    session = request.session
    if "vendorpassword" not in session:
        return redirect('account:homepage')

    context = {"resetform":VendorPasswordForm()}
    return render(request, 'account/registration/password_creation.html', context)


def password_confirm(request):
    session = request.session
    if "vendorpassword" not in session:
        return redirect('account:homepage')
    user_redirect_url = f"{'http://'}{str(get_current_site(request))}/dashboard",
    try:
        user_session = request.session["vendorpassword"]["user_id"]
        user = Customer.objects.get(pk=user_session)
    except:
        user = None

    if user is not None and request.POST.get('action') == 'create-password':
        password1 = str(request.POST.get('password1'))
        password2 = str(request.POST.get('password2'))

        if password1 and password2 and password1 != password2:
            return JsonResponse({'errors':'Passwords donnot match'}, safe=False)
        
        if len(password1) < 8:
            return JsonResponse({'errors':'Password must be atleast 8 characters'}, safe=False)
        
        user.set_password(password1)
        user.is_active=True
        user.save()

        login(request, user)

        del request.session["vendorpassword"]["user_id"]
        messages.info(request, f'Welcome back {user.short_name}')

        return JsonResponse({'errors':'', 'user_redirect':user_redirect_url}, safe=False)


@login_required 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_dashboard(request):
    if request.user.user_type == Customer.VENDOR and request.user.is_active == True:
        category = request.user.vendor_company.category
        team = get_object_or_404(Team, pk=request.user.vendor.active_team_id, members__in=[request.user])
        tickets = Ticket.objects.filter(team=team, category=category, status="unassigned")
        context = {
            'regform': VendorCreationForm(),
            'team': team,
            'tickets': tickets
        }
        return render(request, 'account/user/vendor_dashboard.html', context)

    if request.user.user_type == Customer.CUSTODIAN and request.user.is_staff == True and request.user.is_active == True and request.user.is_superuser == False:
        branch = request.user.branch
        ticketform = TicketForm(branch, request.POST or None)
        tickets = Ticket.objects.filter(branch=request.user.branch).exclude(status="closed")

        context = {
            'ticketform': ticketform,
            'tickets': tickets
        }
        return render(request, 'account/user/custodian_dashboard.html', context)

    if request.user.user_type == Customer.ADMIN and request.user.is_staff == True and request.user.is_active == True and request.user.is_superuser == True:
        branch = request.user.branch
        ticketform = TicketForm(branch, request.POST or None)
        tickets = Ticket.objects.filter(branch=request.user.branch).exclude(status="closed")

        context = {
            'ticketform': ticketform,
            'tickets': tickets
        }
        return render(request, 'account/user/custodian_dashboard.html', context) 

    if (request.user.user_type == Customer.INITIATOR or request.user.user_type == Customer.OFFICER or request.user.user_type == Customer.HEAD) and request.user.is_staff == True and request.user.is_active == True:
        branch = request.user.branch
        tender = Tender.objects.filter(duration__gte=timezone.now())
        applications = Application.objects.filter(status='notgraded')
        # gradings = Grading.objects.filter(application__status='graded', qualification=True)
        context = {
            'protovariable': 'listoftenders',
            'branch': branch,
            'tender': tender,
            'applications': applications,
            # 'gradings': gradings,
            'domain':get_current_site(request)
        }
        return render(request, 'account/user/stakeholder_dashboard.html', context)

    # if request.user.user_type == Customer.OFFICER and request.user.is_staff == True and request.user.is_active == True and request.user.is_stakeholder == True:
    #     branch = request.user.branch
    #     applications = Application.objects.filter(status='notgraded')
    #     context = {
    #     'protovariable': 'listofapplication',  
    #     'applications': applications, 
    #         'domain':get_current_site(request)
    #     }
    #     return render(request, 'account/user/stakeholder_dashboard.html', context)
    
    # if request.user.user_type == Customer.HEAD and request.user.is_staff == True and request.user.is_active == True and request.user.is_stakeholder == True:
    #     branch = request.user.branch
    #     gradings = Grading.objects.filter(application__status='graded', qualification=True)
    #     context = {
    #     'protovariable': 'requiregrading',
    #     'gradings': gradings, 
    #         'branch': branch,
    #         'domain':get_current_site(request)
    #     }
    #     return render(request, 'account/user/stakeholder_dashboard.html', context)


@login_required
@user_is_moderator 
def verify_username(request):
    short_name = request.POST.get('short_name')
    if len(short_name) < 4:
        return HttpResponse("<div style='color:red;'> The username must be four characters or more </div>")
    else:
        if Customer.objects.filter(short_name=short_name).exists():
            return HttpResponse("<div id='short_name-status' style='color:red;' class='shortnameerrors'> Username already taken </div>")
        else:
            return HttpResponse("<div id='short_name-status' style='color:green;' class='shortnamesuccess'> This username is available </div>") 

