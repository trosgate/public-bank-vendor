from django.contrib import admin
from .models import (
    WebsiteSetting, WebsiteContent, VendorCompany, SLAExceptions, Checklist, SupportProduct,
    Branch, Terminals, Mailer, TestMailSetting, Category, Inventory, MailingGroup
)
import sys

MAX_OBJECTS = 1


@admin.register(WebsiteSetting)
class WebsiteSettingAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_domain', 'site_logo_tag', ]
    list_display_links = ['site_name', 'site_domain']
    readonly_fields = ['site_logo_tag']
    list_per_page = sys.maxsize
    fieldsets = (
        ('Site Description', {'fields': ('site_name', 'site_domain', 'site_Logo', 'protocol',)}), 
        ('Color Scheme', {'fields': ('button_color', 'navbar_color',)}),
        ('Security Supervisor', {'fields': ('warning_time_schedule',)}),
        ('Social Media', {'fields': ('twitter_url', 'instagram_url', 'youtube_url', 'facebook_url',)}),
    )

    radio_fields = {'protocol': admin.HORIZONTAL}

    def has_add_permission(self, request):
        if self.model.objects.count() >= MAX_OBJECTS:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(WebsiteContent)
class WebsiteContentAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_description']
    list_per_page = sys.maxsize
    fieldsets = (
        ('Website headers - Content to display site-wide', {'fields': ('site_name', 'site_description',)}), 
        ('Onboarding Content - login and Reset Content on Homepage', {'fields': ('home_title', 'home_preview','login_preview','reset_preview',)}), 
        ('Default Profile Description (Vendor)', {'fields': ('profile_description',)}),
        ('Vendor Banner Content', {'fields': ('team_banner_title', 'team_banner_preview',)}),
    )

    def has_add_permission(self, request):
        if self.model.objects.count() >= MAX_OBJECTS:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ordering', 'quantity', 'status']
    list_display_links = ['id', 'name']
    list_editable = ['ordering', 'quantity', 'status']
    radio_fields = {'status': admin.VERTICAL}
    
    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class SupportProductAdmin(admin.TabularInline):
    model = SupportProduct
    list_display = ['category', 'name', 'status', 'created_at']
    list_display_links= ['category', 'name']
    readonly_fields=['created_at']
    extra = 0
    can_delete = False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'meta', 'ordering', 'status']
    list_editable = ['ordering', 'status']
    list_display_links = ['name', 'meta']
    radio_fields = {'meta': admin.VERTICAL, 'status': admin.VERTICAL}
    
    fieldsets = (
        ('Category Attributes', {'fields': ( 'name', 'meta', 'ordering', 'status',)}),
    )
    inlines = [SupportProductAdmin]
 

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(MailingGroup)
class MailingGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'branch', 'cluster']
    list_editable = ['email', 'branch']
    readonly_fields=['created_at']
    # list_filter=['cluster']

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ['item', 'ordering']
    list_editable = ['item', 'ordering']
    list_display_links = None
    
    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)


@admin.register(VendorCompany)
class VendorCompanyAdmin(admin.ModelAdmin):  
    list_display = ['name', 'category', 'working_hours', 'status', 'ordering']
    list_editable = ['status','ordering']
    list_filter = ['category','status']
    search_fields = ['name', 'registered_name'] 
    readonly_fields = ['created_at', 'track_working_time']
    fieldsets = (
        ('Basic Info', {'fields': ('email', 'name', 'registered_name', 'ordering',)}),
        ('Classification', {'fields': ('status', 'category',)}),
        ('SLA Operations', {'fields': ('working_hours', 'ticket_response', 'instation_arrival','outstation_arrival', 'track_working_time',)}),
        ('Creation Log', {'fields': ('created_at',)}),
    )
    radio_fields = {
        'category': admin.VERTICAL, 
        'status': admin.VERTICAL,
        'working_hours': admin.HORIZONTAL,
    }   

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        disabled_fields = set() 

        if obj is not None:            
            disabled_fields |= {
                'category',
                'name',
            }

        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        
        return form

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Mailer)
class MailerAdmin(admin.ModelAdmin):
    list_display = ['from_email', 'email_hosting_server', 'email_use_tls', 'email_use_ssl']
    list_display_links = ['from_email', 'email_hosting_server']
    list_per_page = sys.maxsize
    fieldsets = (
        ('SMTP Email API', {'fields': ('email_hosting_server','email_hosting_username', 'from_email', 'email_hosting_server_password',
         'email_hosting_server_port',)}),
        ('Email Server Certificate', {'fields': ('email_use_tls', 'email_use_ssl',)}),
        ('Email Config Error Control', {'fields': ('email_timeout', 'email_fail_silently',)}),
    )

    def has_add_permission(self, request):
        if self.model.objects.count() >= MAX_OBJECTS:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(TestMailSetting)
class TestEmailAdmin(admin.ModelAdmin):
    list_display = ['title', 'test_email']
    list_display_links = ['title', 'test_email']
    readonly_fields = ['title']
    fieldsets = (
        ('Description', {'fields': ('title',)}),
        ('Receiver Email: Enter email and click "Save" button to send Test mail', {'fields': ('test_email',)}),
    )
    def has_add_permission(self, request):
        if self.model.objects.count() >= MAX_OBJECTS:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):  
    list_display = ['id', 'name', 'location', 'status', 'inventory']
    list_editable = ['location', 'status']
    list_display_links = ['id', 'name']
    list_filter = ['location','status', 'inventory']
    prepopulated_fields = {'slug': ('name',)}


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        disabled_fields = set() 

        if obj is not None:            
            disabled_fields |= {
                'name',
            }

        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        
        return form

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Terminals)
class TerminalsAdmin(admin.ModelAdmin):
    list_display = ['terminal', 'name', 'category', 'branch']
    list_filter = ['type', 'vendor', 'status', 'category']
    search_fields = ['name', 'terminal']
    list_editable = ['category','branch']
    list_display_links = ['terminal', 'name']

    fieldsets = (
        ('Attributes', {'fields': ('name', 'terminal', 'branch', 'vendor',)}),
        ('Description', {'fields': ('description', 'gps_address', 'region',)}),
        ('Classification', {'fields': ('status', 'category','type', )}),
    )

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
        
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SLAExceptions)
class SLAExceptionsAdmin(admin.ModelAdmin):  
    list_display = ['name', 'ordering']
    list_editable = ['name', 'ordering']
    list_display_links = None

































