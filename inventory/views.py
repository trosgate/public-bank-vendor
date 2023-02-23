from django.shortcuts import render, get_object_or_404, redirect
from account.decorators import user_is_custodian
from django.contrib.auth.decorators import login_required
from account.models import Customer
from django.http import HttpResponse, JsonResponse
from .models import InventoryRequest
from account.exception import TicketException
from general_settings.models import Category, Inventory, Terminals, Branch, SLAExceptions, VendorCompany
from .forms import InventoryForm, InventoryReviewForm, InventoryConfirmForm
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from .utilities import l1_variance, l2_variance, l3_variance, l4_variance


@login_required
@user_is_custodian
def requisition(request):
    inventories = None
    if request.user.branch.inventory == False:
        inventories = InventoryRequest.objects.filter(
            request_branch = request.user.branch, request_branch__inventory = False
        ).exclude(status="closed")

    elif request.user.branch.inventory == True:
        inventories = InventoryRequest.objects.all().exclude(status="closed")
    myreq = True
    context = {
        'myreq':myreq,
        'inventories':inventories,
        'stockform': InventoryForm()
    }

    return render(request, 'inventory/requisition.html', context)


@login_required
@user_is_custodian
def create_requisition(request):
    inventories = None
    issuing_branch = get_object_or_404(Branch, inventory=True)
    stockform = InventoryForm(request.POST or None)

    if stockform.is_valid():
        inventory = stockform.save(commit=False)
        inventory.request_branch = request.user.branch
        inventory.request_by = request.user
        inventory.issue_branch = issuing_branch
        inventory.save()
        
        stan = f'{inventory.pk}'.zfill(4)
        inventory_cat = f'{inventory.category.pk}'
        inventory.reference = f'REQ{inventory_cat}{stan}'
        inventory.save()
        messages.info(request, 'Requisition created')

    if request.user.branch.inventory == False:
        inventories = InventoryRequest.objects.filter(
            request_branch = request.user.branch, request_branch__inventory = False
        )

    elif request.user.branch.inventory == True:
        inventories = InventoryRequest.objects.filter(
            issue_branch= request.user.branch, 
            issue_branch__inventory = True
        )    
    context = {
        'inventories':inventories
    }    
    return render(request, 'inventory/partials/inventory_list.html', context)


@login_required
@user_is_custodian
def inventory_detail(request, pk):
    inventory = get_object_or_404(InventoryRequest, pk=pk)
    stockform = InventoryReviewForm(request.POST or None, instance=inventory)
    line_one_var = l1_variance(inventory)
    line_two_var = l2_variance(inventory)
    line_three_var = l3_variance(inventory)
    line_four_var = l4_variance(inventory)
    
    context = {
        'inventory':inventory,
        'stockform':stockform,
        'line_one_var':line_one_var,
        'line_two_var':line_two_var,
        'line_three_var':line_three_var,
        'line_four_var':line_four_var,
    }
    return render(request, 'inventory/partials/inventory_states.html', context)


@login_required
@user_is_custodian
def issue_inventory(request, pk):
    inventory = get_object_or_404(InventoryRequest, pk=pk)
    stockform = InventoryReviewForm()
    line_one_var = 0
    line_two_var = 0
    line_three_var = 0
    line_four_var = 0
    line_one_issue = int(request.POST.get('line_one_issue', 0))
    line_two_issue = int(request.POST.get('line_two_issue', 0))
    line_three_issue = int(request.POST.get('line_three_issue', 0))
    line_four_issue = int(request.POST.get('line_four_issue', 0))
    issue_remark = str(request.POST.get('issue_remark', 0))

    if line_one_issue > inventory.line_one_order:
        messages.error(request, 'Quantity issued cannot be greater than requested quantity')
        pass
    elif line_two_issue > inventory.line_two_order:
        messages.error(request, 'Quantity issued cannot be greater than requested quantity')
        pass
    elif line_three_issue > inventory.line_three_order:
        messages.error(request, 'Quantity issued cannot be greater than requested quantity')
        pass
    elif line_four_issue > inventory.line_four_order:
        messages.error(request, 'Quantity issued cannot be greater than requested quantity')
        pass
    else:
        inventory.line_one_issue = line_one_issue
        inventory.line_two_issue = line_two_issue
        inventory.line_three_issue = line_three_issue
        inventory.line_four_issue = line_four_issue
        inventory.issue_remark = issue_remark
        inventory.issued_by = request.user
        inventory.issue_at = timezone.now()
        inventory.status = 'issued'
        inventory.save()
        messages.info(request, 'Issued successfully')
        line_one_var = l1_variance(inventory)
        line_two_var = l2_variance(inventory)
        line_three_var = l3_variance(inventory)
        line_four_var = l4_variance(inventory)    
    context = {
        'inventory':inventory,
        'stockform':stockform,
        'line_one_var':line_one_var,
        'line_two_var':line_two_var,
        'line_three_var':line_three_var,
        'line_four_var':line_four_var,
    }
    return render(request, 'inventory/partials/inventory_states.html', context)


@login_required
@user_is_custodian
def inventory_preview(request, pk, inventory_slug):
    inventory = get_object_or_404(InventoryRequest, pk=pk, slug=inventory_slug)
    line_one_var = l1_variance(inventory)
    line_two_var = l2_variance(inventory)
    line_three_var = l3_variance(inventory)
    line_four_var = l4_variance(inventory)

    stockconfirmform = InventoryConfirmForm(request.POST or None)
    if stockconfirmform.is_valid():
        inventory.condition = stockconfirmform.cleaned_data['condition']
        inventory.status = 'closed'
        inventory.save()

        messages.info(request, 'Requisition confirmed and Closed')    
        return redirect('inventory:inventory_preview', pk=inventory.pk, inventory_slug=inventory.slug)


     
    context = {
        'inventory':inventory,
        'line_one_var':line_one_var,
        'line_two_var':line_two_var,
        'line_three_var':line_three_var,
        'line_four_var':line_four_var,
        'stockconfirmform':stockconfirmform,
    }
    return render(request, 'inventory/inventory_preview.html', context)

