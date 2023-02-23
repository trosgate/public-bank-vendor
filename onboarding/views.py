from django.shortcuts import render, get_object_or_404, redirect
from general_settings.models import Category, VendorCompany
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.contrib import messages
from .models import Composer, Tender, Contacts, Parameters, Invitation, Application, Grading, Panelist, BlacklistedVendor
from .forms import (
    InstructionForm, 
    ContactForm, 
    ParameterForm, 
    InvitemessageForm, 
    TenderForm, 
    InvitationForm, 
    GeneralApplicationForm, 
    CategorizedApplicationForm, 
    GradingForm, 
    ApprovalForm,
    PanelistForm
)
from django.db import transaction as db_transaction
from django.http import HttpResponse
from account.decorators import user_is_officer, user_is_procurement_head
from general_settings.models import WebsiteSetting, SupportProduct
from .controller import max_number_of_invited_links, has_atleast_one_applicant, invite_link_has_expired
from django.utils import timezone
from .utilities import create_random_code, validate_mail
from .tasks import pending_approval, approved_and_profiled
from account.models import Customer
from django.db.models import Q,F
from django.views.decorators.http import require_http_methods


@login_required
def search_group(request):
    search_word = request.POST.get('search')

    applications = Application.objects.filter(
        Q(invitation__tender__title__icontains = search_word)| 
        Q(invitation__tender__reference__icontains = search_word),
        status='graded',
    )
    
    context = {
        'protovariable': 'requiregrading',  
        'applications': applications,
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def composer_view(request, website_pk):
    instruction = get_object_or_404(WebsiteSetting, pk=website_pk)
    context = {
        'instruction': instruction,
        'protovariable': 'modifiedcontent',
    }
    return render(request, 'onboarding/composer.html', context)


@login_required
@user_is_officer
def instruction_form(request, website_pk):
    instruction = get_object_or_404(WebsiteSetting, pk=website_pk)
    context = {
        'protovariable': 'applicantinstruction',
        'instruction': instruction,
        'instruction_form': InstructionForm(instance=instruction),
    }
    return render(request, 'onboarding/partials/composer.html', context)


@login_required
@user_is_officer
def invitemessage_form(request, website_pk):
    instruction = get_object_or_404(WebsiteSetting, pk=website_pk)
    context = {
        'protovariable':'invitemessage',
        'instruction': instruction,
        'invitemessage_form': InvitemessageForm(instance=instruction),
    }
    return render(request, 'onboarding/partials/composer.html', context)


@login_required
@user_is_officer
def composed_messages(request, website_pk):
    instruction = get_object_or_404(WebsiteSetting, pk=website_pk)
    applicant_inst = request.POST.get('applicant_instruction', '')
    invitation_msg = request.POST.get('invite_message', '')

    if instruction and applicant_inst != '':
        instruction.applicant_instruction = applicant_inst
        instruction.save()

    if instruction and invitation_msg != '':
        instruction.invite_message = invitation_msg
        instruction.save()

    context = {
        'protovariable': 'modifiedcontent',
        'instruction': instruction,  
    }
    return render(request, 'onboarding/partials/composer.html', context)


# @login_required
# @user_is_officer
# def vendor_category(request):
#     categories = Category.objects.filter(status=True)
#     context = {
#         'protovariable': 'stageone', 
#         'categories': categories,  
  
#     }
#     return render(request, 'onboarding/partials/tender_states.html', context)


@login_required
@user_is_officer
def tender_group(request):
    tender_form = TenderForm(request.POST or None)
    context = {
        'tender_form': tender_form, 
    }
    return render(request, 'onboarding/partials/tender_group.html', context)


@login_required
@user_is_officer
def create_tender(request):
    tender_form = TenderForm(request.POST or None)
    if tender_form.is_valid():
        
        try:
            Tender.create(
                title=tender_form.cleaned_data['title'], 
                duration=tender_form.cleaned_data['duration'],
                number_of_links=tender_form.cleaned_data['number_of_links'],
                mode=tender_form.cleaned_data['mode'], 
                created_by=request.user,
                category=tender_form.cleaned_data['category']
            )
        except Exception as e:
            print(str(e))
            messages.error(request, f'{e}')

        tender = Tender.objects.filter(duration__gte=timezone.now())
        context = {
            'protovariable': 'listoftenders', 
            'tender': tender,
        }
        return render(request, 'onboarding/partials/tender_nav.html', context)
    else:
        messages.error(request, f'Please ensure to complete required fields above')        
        context = {
            'tender_form': TenderForm(request.POST or None),
        }
        return render(request, 'onboarding/partials/tender_group.html', context)        


@login_required
@user_is_officer
def tender_list_nav(request):
    tender = Tender.objects.filter(duration__gte=timezone.now())
    context = {
        'protovariable': 'listoftenders',  
        'tender': tender,  

    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def invitation_detail(request, tender_pk, tender_slug):
    tender = get_object_or_404(Tender, pk=tender_pk, slug=tender_slug)
    invitation_form = InvitationForm(request.POST or None)
    invitations = Invitation.objects.filter(tender=tender)
    context = {
        'tender': tender,
        'invitations': invitations,
        'invitation_form': invitation_form,
        'max_number_of_invites': max_number_of_invited_links(tender),    
        'has_applicant': has_atleast_one_applicant(tender),    
    }
    return render(request, 'onboarding/invitation_detail.html', context)


@login_required
@user_is_officer
def add_contact(request):
    contacts = Contacts.objects.all()
    contact_form = ContactForm(request.POST or None)
       
    context = {
        'contact_form': contact_form,
        'contacts': contacts,
    }
    return render(request, 'onboarding/contacts.html', context)


@login_required
@user_is_officer
def create_contact(request):
    contacts = Contacts.objects.all()
    contact_form = ContactForm(request.POST or None)
    if contact_form.is_valid():
        new_contact = contact_form.save(commit=False)
        new_contact.created_by = request.user
        new_contact.save()
        messages.info(request, f'Created Successfully')

    else:
        messages.error(request, f'Error! Please correct error(s) below')

    context = {
        'contact_form': ContactForm(),
        'contacts': contacts,
    }
    return render(request, 'onboarding/partials/contact_list.html', context)


@login_required
@user_is_officer
def remove_contact(request):
    contact_pk = request.POST.get('contact')
    contact = get_object_or_404(Contacts, pk=contact_pk, created_by=request.user)
    contact.delete()
    contacts = Contacts.objects.all()
    context = {
        'contact_form': ContactForm(),
        'contacts': contacts,
    }
    return render(request, 'onboarding/partials/contact_list.html', context)


@login_required
@user_is_officer
def parameter_list_nav(request):
    parameters = Parameters.objects.all()
    context = {
        'protovariable': 'listofparams',  
        'parameters': parameters,

    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def parameter_detail(request, reference):
    parameter = get_object_or_404(Parameters, reference=reference)
    context = {
        'parameter': parameter,
    }
    return render(request, 'onboarding/parameter.html', context)


@login_required
@user_is_officer
def param_form(request, reference):
    parameter = get_object_or_404(Parameters, reference=reference)
    parameter_form = ParameterForm(request.POST or None, instance = parameter)

    context = {
        'protovariable': 'paramform',
        'parameter_form': parameter_form,
        'parameter': parameter,
    }
    return render(request, 'onboarding/partials/parameter.html', context)

@login_required
@user_is_officer
def modify_param_form(request, reference):
    parameter = get_object_or_404(Parameters, reference=reference)
    parameter_form = ParameterForm(request.POST or None, instance = parameter)

    if parameter_form.is_valid():
        new_param = parameter_form.save(commit=False)
        new_param.edited_by = request.user
        new_param.save()

        parameter = get_object_or_404(Parameters, reference=parameter.reference)

    context = {
        'modifyparam': 'modifyparam',
        'parameter_form': ParameterForm(),
        'parameter': parameter,
    }
    return render(request, 'onboarding/partials/parameter.html', context)


@login_required
@user_is_officer
def invitation_link(request, invite_pk):
    tender = get_object_or_404(Tender, pk=invite_pk)
    invitation_form = InvitationForm(request.POST or None)
    max_invite = max_number_of_invited_links(tender)

    if invitation_form.is_valid() and max_invite:
        try:
            Invitation.send_invitation(
                tender=tender,
                created_by=request.user,
                receiver=invitation_form.cleaned_data['receiver'],
            )
        except Exception as e:
            messages.error(request, f'{e}')
            
    else:
        messages.error(request, f'Error! Please correct error(s) below')
    invitations = Invitation.objects.filter(tender=tender)
    context = {
        'tender': tender,
        'invitations': invitations,
        'invitation_form': InvitationForm(),
    }
    return render(request, 'onboarding/partials/invitation_list.html', context)            


@login_required
@user_is_officer
def invitation_list_nav(request):
    invitations = Invitation.objects.filter(status='invited')
    context = {
        'protovariable': 'listofinvitees',  
        'invitations': invitations,
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def ungraded_application_list_nav(request):
    applications = Application.objects.filter(
        Q(status='notgraded')|
        Q(status='incomplete')
    )
    context = {
        'protovariable': 'listofapplication',  
        'applications': applications,  

    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def reviewed_application_list_nav(request):
    applications = Application.objects.filter(
        Q(status='reviewed')| 
        Q(status='graded'),
        visibility=True
    )
    context = {
        'protovariable': 'revewedgrading',
        'applications': applications,  

    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def hide_application(request):
    application_pk = request.POST.get('hideshowapplicant')
    application = get_object_or_404(Application, pk=application_pk)

    if application.visibility == True:
        application.visibility = False
        application.save()

    applications = Application.objects.filter(
        Q(status='reviewed')|
        Q(status='graded'),
        visibility=True
    )

    context = {
        'protovariable': 'revewedgrading',
        'applications': applications,  
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_officer
def restore_application(request): 
    applications = Application.objects.filter(
        Q(status='reviewed')|
        Q(status='graded'),
        visibility=False
    )
    if request.method == "POST":
        application_pk = int(request.POST.get('showapplicant'))
        application = get_object_or_404(Application, pk=application_pk)
        application.visibility = True
        application.save()

    context = {
        'protovariable': 'revewedgrading',
        'applications': applications,  
    }
    if request.htmx:
        return render(request, 'onboarding/partials/restore_application.html', context)
    return render(request, 'onboarding/application_restore.html', context)


@login_required
@user_is_officer
def graded_application_list_nav(request):
    applications = Application.objects.filter(status='graded')
    context = {
        'protovariable': 'requiregrading',  
        'protovariable22': 'requiresearch',  
        'applications': applications,
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_procurement_head
def bulk_application_list_nav(request):
    applications = Application.objects.filter(status='graded', is_marked=True)
    context = {
        'protovariable': 'bulkgrading',  
        'applications': applications,  

    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@require_http_methods(['POST', 'GET'])
def application_view(request, invite_reference, tender_slug):
    invitation = get_object_or_404(Invitation, reference=invite_reference, tender__slug=tender_slug)
    
    if invitation.tender.mode == 'general':
        application_form = GeneralApplicationForm(request.POST or None, request.FILES or None)
    else:
        category = invitation.tender.category
        application_form = CategorizedApplicationForm(category, request.POST or None, request.FILES or None)

    application_expiry = invitation.tender.duration

    context = {
        'invitation': invitation,
        'application_form': application_form,    
        'application_expiry': application_expiry,    
        'invite_link_expired': invite_link_has_expired(invitation.tender),    
    }
    return render(request, 'onboarding/application.html', context)


def verify_products(request):
    product_pk = request.POST.get('category')
    category = get_object_or_404(Category, pk=product_pk)
    products = SupportProduct.objects.filter(category=category)
    product_list = [product.name for product in products]
    all_products = ', '.join(product_list)
    if products.count():
        return HttpResponse(f"<div id='product_list' style='color:green;' class='wt-tabscontenttitle'>Nature of Supports Available: <br> {all_products}</div>")
    else:
        return HttpResponse("<div id='product_list' style='color:green;'> No category Selected Yet </div>") 


@login_required
@user_is_officer
def mylinks(request):
    panelists = Panelist.objects.filter(panelist=request.user)
    context = {
        'panelists': panelists,  
    }
    return render(request, 'onboarding/mylinks.html', context)


@require_http_methods(['POST'])
def unlock_application(request, invite_reference):
    invitations = get_object_or_404(Invitation, reference=invite_reference)
    application_expiry = invitations.tender.duration

    if invitations.tender.mode == 'general':
        application_form = GeneralApplicationForm()
    else:
        category = invitations.tender.category
        application_form = CategorizedApplicationForm(category)
    
    email = request.POST.get('email')
    token = request.POST.get('password')

    if invitations.receiver.email == email and invitations.token == token:
        invitations.access = 'unlocked'
        invitations.save()

        context = {
            'protovariable': 'nonav',
            'invitation': invitations,
            'application_form': application_form,
            'application_expiry': application_expiry,    
        }
        return render(request, 'onboarding/partials/application_form.html', context)
    
    else:
        error_message = f'Invalid email or token!'
        context = {
            'error_message': error_message,
            'invitation': invitations,
            'application_expiry': application_expiry,    
        }
        return render(request, 'onboarding/partials/application_form.html', context)


@require_http_methods(['POST'])
def submit_application(request, invite_reference):
    invitations = get_object_or_404(Invitation, reference=invite_reference, status='invited')
    application_expiry = invitations.tender.duration

    if invitations.tender.mode == 'general':
        application_form = GeneralApplicationForm(request.POST or None, request.FILES or None)
    else:
        category = invitations.tender.category
        application_form = CategorizedApplicationForm(category, request.POST or None, request.FILES or None)
    
    if application_form.is_valid():
        new_application = application_form.save(commit=False)

        new_application.invitation = invitations
        new_application.reference =f'{create_random_code()}'

        if invitations.tender.mode == 'general':
            mycategory = application_form.cleaned_data['category']
            support_product = SupportProduct.objects.filter(category=mycategory)
            new_application.save()

            for product in support_product:
                new_application.support_product.add(product.pk)

        else:# This is category-based
            new_application.category=invitations.tender.category
            new_application.save()
            application_form.save_m2m()

        invitations.status = 'applied'
        invitations.save()
        context = {            
            'invitation': invitations,    
        }
        return render(request, 'onboarding/partials/application_form.html', context)

    else:
        error_message = f'Please correct the error(s) above!'
        context = {
            'error_message': error_message,
            'invitation': invitations,    
            'application_form': application_form,    
            'application_expiry': application_expiry,    
        }
        return render(request, 'onboarding/partials/application_form.html', context)


@login_required
@user_is_officer
def pool_review(request, reference, vendor_name):
    application = get_object_or_404(Application, pk=reference, name=vendor_name)

    context = {
        'application': application,
    }
    return render(request, 'onboarding/application_review.html', context)


@login_required
@user_is_officer
@require_http_methods(['POST', 'GET'])
def application_review(request):
    application_pk = int(request.POST.get('selectedapplicant'))
    button_chosen = str(request.POST.get('buttonchosen'))
    reasons = str(request.POST.get('reason'))
    application = get_object_or_404(Application, pk=application_pk)
    
    if button_chosen == 'incomplete':
        application.status = 'incomplete'
        application.reviewed_by = request.user
        application.reason = reasons
        application.reviewed_at = timezone.now()
        application.save()

    elif button_chosen == 'complete':
        application.status = 'reviewed'
        application.approved_by = request.user
        application.save()

    context = {
        'application': application,
    }
    return render(request, 'onboarding/partials/review_action.html', context)


@login_required
@user_is_officer
def panelist_view(request, applicant_name):
    application = get_object_or_404(Application, name=applicant_name)

    ext_panelists = Panelist.objects.filter(application=application, email__isnull=False, mode='external')
    int_panelists = Panelist.objects.filter(application=application, panelist__isnull=False, mode='internal')
    invited_list = [panel.panelist.pk for panel in int_panelists]

    team_members = Customer.objects.filter(
        is_stakeholder = True,
        is_active=True
    ).exclude(pk__in=invited_list)

    panel_form = PanelistForm(request.POST or None)

    context = {
        'application': application,
        "panel_form": panel_form,    
        "team_members": team_members,
        "int_panelists": int_panelists,
        "ext_panelists": ext_panelists,
    }
    return render(request, 'onboarding/panelist_detail.html', context)


@login_required
@user_is_officer
def panelist(request, application_pk):
    invited_list = None
    team_members = None
    int_panelists = None
    ext_panelists = None
    application = get_object_or_404(Application, pk=application_pk)

    invite_modes = str(request.POST.get('modes'))

    if invite_modes == 'internal':
        panelist_pk = int(request.POST.get('panel'))
        panelist = get_object_or_404(Customer, pk=panelist_pk, is_active=True)

        Panelist.objects.get_or_create(application=application, panelist=panelist, access='unlocked')[0]
        int_panelists = Panelist.objects.filter(application=application, panelist__isnull=False, mode='internal')
        invited_list = [panel.panelist.pk for panel in int_panelists]
        
        team_members = Customer.objects.filter(
            is_stakeholder = True,
            is_active=True
        ).exclude(pk__in=invited_list)

        context = {
            'application': application,
            "int_panelists": int_panelists,
            "team_members": team_members,
        }
        return render(request, 'onboarding/partials/panel_list.html', context) 

    elif invite_modes == 'external':
        name = str(request.POST.get('name'))
        email = request.POST.get('email')        
        new_email = validate_mail(email)

        Panelist.objects.get_or_create(application=application, name=name, email=new_email, mode='external')[0]
            
        ext_panelists = Panelist.objects.filter(application=application, email__isnull=False, mode='external')

        context = {
            'application': application,
            "ext_panelists": ext_panelists,
        }
        return render(request, 'onboarding/partials/ext_panel_list.html', context) 


@require_http_methods(['POST', 'GET'])
def external_scoresheet(request, reference, vendor_name):
    application = get_object_or_404(Application, name=vendor_name)
    panelist = get_object_or_404(Panelist, reference=reference, application=application, mode='external')
    parameter=None
    parameters = Parameters.objects.all()
    if parameters.count()> 0:
        parameter = parameters.last()
    if application.status == 'reviewed' or application.status == 'graded':
        grading_form = GradingForm(request.POST or None)
        context = {
            'panelist': panelist,
            'application': application,
            'parameter': parameter,
            'grading_form': grading_form,
        }
        return render(request, 'onboarding/grading.html', context)

    else:
        context = {
            'panelist': panelist,
            'application': application,
        }
        return render(request, 'onboarding/invalid.html', context)
    

@login_required
@user_is_officer
@require_http_methods(['POST', 'GET'])
def internal_scoresheet(request, reference, vendor_name):
    application = get_object_or_404(Application, name=vendor_name)
    panelist = get_object_or_404(Panelist, reference=reference, application=application, mode='internal')
    parameter=None
    parameters = Parameters.objects.all()
    if parameters.count()> 0:
        parameter = parameters.last()
    if application.status == 'reviewed' or application.status == 'graded':
        grading_form = GradingForm(request.POST or None)
        context = {
            'panelist': panelist,
            'application': application,
            'parameter': parameter,
            'grading_form': grading_form,
        }
        return render(request, 'onboarding/grading.html', context)

    else:
        context = {
            'application': application,
        }
        return render(request, 'onboarding/invalid.html', context)
    

@require_http_methods(['POST'])
def unlock_panelist(request, invite_reference):
    panelist = get_object_or_404(Panelist, reference=invite_reference)
    application = get_object_or_404(Application, pk=panelist.application.pk)
    parameter = None
    parameters = Parameters.objects.all()
    if parameters.count()> 0:
        parameter = parameters.last()
    email = request.POST.get('email')
    token = request.POST.get('password')
    mygrading_form = GradingForm(request.POST or None)

    if panelist.email == email and panelist.token == token:
        panelist.access = 'unlocked'
        panelist.save()

        context = {
            'panelist': panelist,
            'grading_form': GradingForm(),
            'application': application,
            'parameter': parameter,
        }
        return render(request, 'onboarding/partials/grading.html', context)
    
    else:
        error_message = f'Invalid email or token!'
        context = {
            'error_message': error_message,
            'panelist': panelist,   
            'application': application,   
        }
        return render(request, 'onboarding/partials/grading.html', context)


@require_http_methods(['POST'])
def panel_grading(request, reference):
    panelist = get_object_or_404(Panelist, reference=reference)
    application = get_object_or_404(Application, pk=panelist.application.pk)
    tender = get_object_or_404(Tender, pk=application.invitation.tender.pk)
    parameters = Parameters.objects.all()
    parameter = None
    if parameters.count()> 0:
        parameter = parameters.last()
    grading_form = GradingForm(request.POST or None)

    # with db_transaction.atomic():
    if grading_form.is_valid():
        grading = grading_form.save(commit=False)
        grading.application = application
        grading.panelist = panelist
        grading.save()
        
        application.status = 'graded'
        application.counter += 1
        application.save()

        panelist.status = 'graded'
        panelist.save()
        
        try:
            pending_approval(grading.pk)
        except Exception as e:
            print(str(e))

        context = {
            'application': application,
            'tender': tender,
            'parameter': parameter,
            'panelist': panelist,
        }
        return render(request, 'onboarding/partials/grading.html', context)

    else:
        messages.error(request, 'error! Please ensure to fill all fields')
        context = {
            'application': application,
            'tender': tender,
            'grading_form': grading_form,
            'parameter': parameter,
            'panelist': panelist,
        }
        return render(request, 'onboarding/partials/grading.html', context)


@login_required
@user_is_officer
def master_scoresheet(request, reference, vendor_name):
    application = get_object_or_404(Application, pk=reference, name=vendor_name)
    tender = get_object_or_404(Tender, pk=application.invitation.tender.pk)
    gradings = Grading.objects.filter(application=application).order_by('id')
    applications = Application.objects.filter(invitation__tender=tender).order_by('id')

    mygradings = None
    if gradings.count() > 0:
        mygradings = gradings.last()

    criteria_class_inject = "col-md-3"
    marks_class_inject = "col-md-8"

    if gradings.count() == 1:
        criteria_class_inject = "col-md-6"
        marks_class_inject = "col-md-5"
    elif gradings.count() == 2:
        criteria_class_inject = "col-md-3"
        marks_class_inject = "col-md-4"
    elif gradings.count() == 3:
        criteria_class_inject = "col-md-2"
        marks_class_inject = "col-md-3"
    elif gradings.count() == 4:
        criteria_class_inject = "col-md-3"
        marks_class_inject = "col-md-2"
    elif gradings.count() == 5:
        criteria_class_inject = "col-md-1"
        marks_class_inject = "col-md-2"
    else:
        criteria_class_inject = "col-md-1"
        marks_class_inject = "col-md-1"

    context = {
        'mygradings': mygradings,
        'application': application,
        'gradings': gradings,
        'tender': tender,
        'applications': applications,
        'marks_class_inject': marks_class_inject,
        'criteria_class_inject': criteria_class_inject,
    }
    return render(request, 'onboarding/scoresheet.html', context)


@login_required
@user_is_procurement_head
def approval(request, application_pk, vendor_name):
    application = get_object_or_404(Application, pk=application_pk, name=vendor_name, status='graded')
    invitation = get_object_or_404(Invitation, pk=application.invitation.pk)
    tender = get_object_or_404(Tender, pk=invitation.tender.pk)

    context = {
        'application': application,
        'tender': tender,
        'approval_form': ApprovalForm(),
    }

    return render(request, 'onboarding/partials/approval.html', context)

 
@login_required
@user_is_procurement_head
@require_http_methods(['POST', 'GET'])
def select_or_unselect_approval(request):
    applications_pk = int(request.POST.get('selectedapplicant'))
    application = get_object_or_404(Application, pk=applications_pk, status='graded')

    if application.is_marked == True:
        application.is_marked = False
        application.save()

    elif application.is_marked == False:
        application.is_marked = True
        application.save()

    applications = Application.objects.filter(status='graded').order_by("id")
    context = {
        'protovariable': 'requiregrading',
        'applications': applications,
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)

    
@login_required
@user_is_procurement_head
def remove_approval(request):
    application_pk = int(request.POST.get('removeapplicant'))
    application = get_object_or_404(Application, pk=application_pk, status='graded')

    if application.is_marked == True:
        application.is_marked = False
        application.save()

    applications = Application.objects.filter(status='graded', is_marked=True)
    context = {
        'protovariable': 'bulkgrading',
        'applications': applications,
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_procurement_head
@require_http_methods(['POST'])
def approval_single(request, application_pk):
    applications = Application.objects.filter(status='graded').order_by("id")
    with db_transaction.atomic():
        application = Application.objects.select_for_update().get(pk=application_pk, status='graded')
        
        application.expire_invitation()

        status = request.POST.get('status')
        justification = request.POST.get('justification', '')

        if status == 'rejected' and justification == '' or status == 'rejected' and justification is None:

            messages.error(request, f'Justification required for rejecting applicant')
            context = {
                'applications': applications,
                'application': application,
                'approval_form': ApprovalForm(request.POST or None),
            }

            return render(request, 'onboarding/partials/approval.html', context)

        elif status == 'rejected' and justification:
            application.status = status
            application.justification = justification
            application.save()
            
            BlacklistedVendor.objects.get_or_create(
                category = application.category,
                name = application.name,
                registered_name = application.registered_name,
                email = application.email,
                reason = application.justification,
                instation_arrival = application.instation,
                outstation_arrival = application.outstation,

            )[0]

            context = {
                'protovariable': 'requiregrading',
                'application': application,
                'applications': applications,
            }
            return render(request, 'onboarding/partials/tender_nav.html', context)

        elif status == 'approved':
            application.status = status
            application.save()

            vendor = VendorCompany.objects.get_or_create(
                category = application.category,
                name = application.name,
                registered_name = application.registered_name,
                email = application.email,
                purpose = f'Contracted to work in the {application.category} category',
                instation_arrival = application.instation,
                outstation_arrival = application.outstation,

            )[0]
            try:
                db_transaction.on_commit(lambda: approved_and_profiled(application.pk, vendor.pk))
            except Exception as e:
                print(str(e))
            context = {
                'protovariable': 'requiregrading',
                'application': application,
                'applications': applications,
            }
            return render(request, 'onboarding/partials/tender_nav.html', context)
        else:    
            context = {
                    'protovariable': 'requiregrading',
                    'application': application,
                    'applications': applications,
                }
            return render(request, 'onboarding/partials/tender_nav.html', context)


@login_required
@user_is_procurement_head
@db_transaction.atomic
@require_http_methods(['GET'])
def bulk_approval(request):
    applications = Application.objects.filter(status='graded', is_marked=True).order_by("id")
    for application in applications:
        application = Application.objects.select_for_update().get(pk=application.pk)
        application.expire_invitation()
        
        application.status = 'approved'
        application.is_marked=False
        application.save()

        vendor = VendorCompany.objects.get_or_create(
            category = application.category,
            name = application.name,
            registered_name = application.registered_name,
            email = application.email,
            purpose = f'Contracted to work in the {application.category} category',
            instation_arrival = application.instation,
            outstation_arrival = application.outstation,

        )[0]
        try:
            db_transaction.on_commit(lambda: approved_and_profiled(application.pk, vendor.pk))
        except Exception as e:
            print(str(e))
    applications = Application.objects.filter(status='graded', is_marked=True).order_by("id")
    
    context = {
        'protovariable': 'bulkgrading',
        'applications': applications,
    }
    return render(request, 'onboarding/partials/tender_nav.html', context)

    

