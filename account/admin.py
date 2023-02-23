from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import Customer, TwoFactorAuth
from django.utils.translation import gettext_lazy as _
import sys
from django.contrib.admin.models import LogEntry
from .forms import CustomerAdminCreationForm


MAX_OBJECTS = 0

class CustomerChangeForm(forms.ModelForm):
    # password = ReadOnlyPasswordHashField()
  
    class Meta:
        model = Customer
        fields = ['email', 'short_name', 'user_type', 'password', 'is_active', 'is_superuser']

    def clean_password(self):
        return self.initial['password']


@admin.register(Customer)
class CustomerAdmin(BaseUserAdmin,):  
    form = CustomerChangeForm
    add_form = CustomerAdminCreationForm

    list_display = ['id', 'short_name', 'user_type', 'is_staff', 'is_vendor', 'is_stakeholder','is_active']
    readonly_fields = ['date_joined', 'last_login'] #
    list_display_links = ['short_name']
    list_filter = ['user_type', 'is_superuser', 'is_staff',]
    fieldsets = (
        ('Personal Information', {'fields': ('email', 'short_name', 'first_name', 'last_name', 'phone', 'password',)}),
        ('User Access Control', {'fields': ('user_type', 'is_active',)}),
        ('Vendor Specific Roles', {'fields': ('vendor_company', 'is_vendor',)}),
        ('Emerging Unit or Branch', {'fields': ('branch','is_staff',)}),
        ('Bank Specific Roles', {'fields': ('is_stakeholder', 'is_assistant', 'is_superuser',)}),
        ('Activity Log', {'fields': ('date_joined', 'last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'short_name', 'first_name', 'last_name', 'user_type', 'vendor_company', 'branch', 'password1', 'password2',)
        }),
    )
    search_fields = ('pk', 'email', 'first_name', 'last_name',)
    ordering = ('pk',)
    filter_horizontal = ()
    list_per_page = 50
    is_superuser = False

    def get_queryset(self, request):
        qs = super(CustomerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.all()  
        else:
            return qs.filter(pk=request.user.pk, is_staff=True)  

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
        
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['email'].widget.attrs['style'] = 'width: 45em;'
        form.base_fields['short_name'].widget.attrs['style'] = 'width: 45em;'
        form.base_fields['first_name'].widget.attrs['style'] = 'width: 45em;'
        form.base_fields['last_name'].widget.attrs['style'] = 'width: 45em;'
        form.base_fields['user_type'].widget.attrs['style'] = 'width: 45em;'
        form.base_fields['vendor_company'].widget.attrs['style'] = 'width: 45em;'

        is_superuser = request.user.is_superuser
        disabled_fields = set() 

        if Customer.objects.filter(is_superuser=True).count() > 0:
            disabled_fields |= {
                'is_superuser',
            }

        if obj is not None and obj.is_superuser == True:            
            disabled_fields |= {
                'is_assistant',
                'is_vendor',
            }

        if (obj is not None and obj.is_assistant == True):            
            disabled_fields |= {
                'is_superuser',
                'is_vendor',
            }

        if (not is_superuser and obj is not None):            
            disabled_fields |= {
                'user_type',
                'is_vendor',
            }

        if (not is_superuser and obj is not None and obj == request.user):
            disabled_fields |= {
                'short_name',
                'email',
                'user_type',
                'is_active',
                'is_vendor',
                'is_superuser',
                'is_staff',
                'is_stakeholder',
                'is_assistant',
            }        

        if (not is_superuser and obj is not None and obj != request.user):
            disabled_fields |= {
                'short_name',
                'first_name',
                'last_name',
                'email',
                'phone',
                'password',
                'user_type',
                'is_vendor',
                'is_active',
                'is_superuser',
                'is_staff',
                'is_assistant',             
            }

        if obj is not None and obj.user_type == 'vendor':
            disabled_fields |= {                
                'is_superuser',
                'is_staff',
                'is_assistant',
                'branch'
            }

        if obj is not None and obj.user_type == 'custodian':
            disabled_fields |= {                
                'is_vendor',
                'vendor_company',
            }

        if obj is not None and obj.user_type == 'head':
            disabled_fields |= {                
                'is_vendor',
                'vendor_company',
            }
        if obj is not None and obj.user_type == 'officer':
            disabled_fields |= {                
                'is_vendor',
                'vendor_company',
            }

        if obj is not None and obj.user_type == 'admin':
            disabled_fields |= {                
                'is_vendor',
                'vendor_company',
            }

        if obj is not None and obj.user_type == 'vendor' and obj.password == '':
            disabled_fields |= {                
                'is_active',
            }

        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        
        return form


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'action_time',  'action_flag']
    readonly_fields = [
        'action_time', 'user', 'content_type', 'action_flag', 
        'object_repr', 'change_message', 'object_id'
    ]
    list_display_links = ['content_type', 'user']
    search_fields = ['object_repr', 'change_message']
    list_filter = ('action_flag',)

    def get_queryset(self, request):
        qs = super(LogEntryAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.all()  
        else:
            return qs.filter(user=request.user)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):   
    list_display = ['user', 'get_user_type', 'last_login', 'pass_code']
    readonly_fields = ['user', 'last_login', 'pass_code']     
    list_display_links = None

    def get_queryset(self, request):
        qs = super(TwoFactorAuthAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(user__is_staff=True) 
        elif request.user.is_assistant:
            return qs.filter(user=request.user) 
        else:
            return qs.filter(pk=0)  
            
    @admin.display(description='User Types', ordering='user__user_type')
    def get_user_type(self, obj):
        return obj.user.user_type.capitalize()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.unregister(Group)