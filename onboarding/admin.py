from django.contrib import admin
from . models import Tender, Parameters, Panelist, Contacts, Invitation, Application, Grading, ActiveVendor, BlacklistedVendor


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'reference', 'created_at', 'number_of_links']
    list_display_links = ['title', 'created_by']
    readonly_fields = [
        'created_by', 'title', 'slug', 'number_of_links', 
         'reference','created_at', 'modified_at', 'reference', 
        ]
    fieldsets = (
        ('Background', {'fields': ('title', 'slug', 'reference', 'mode', 'category',)}),
        ('Activity Log', {'fields': ( 'created_by', 'created_at', 'duration', 'modified_at',)}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
        
MAX_OBJECTS = 1

@admin.register(Parameters)
class ParametersAdmin(admin.ModelAdmin):
    list_display = ['reference', 'criteria1', 'note1']

    def has_add_permission(self, request):
        if self.model.objects.count() >= MAX_OBJECTS:
            return False
        return super().has_add_permission(request)


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    list_display_links = ['name', 'email']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'created_by', 'receiver', 'status']
    list_display_links = ['reference', 'created_by']
    readonly_fields = [
        'reference','token', 'created_by', 'receiver', 
        'status', 'tender', 'sent_on',
    ]
    fieldsets = (
        ('New Application', {'fields': (
            'reference', 'created_by', 'receiver',
            'token', 'status', 'tender', 'sent_on'
        )}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'applicant', 'name', 'status', 'counter', 'invitation']
    list_display_links = ['reference', 'applicant']
    list_editable = ['counter','status',]
    readonly_fields = [
        'invitation', 'applicant','name', 'registered_name', 'status',
        'max_member_per_team', 'regional_availability','counter','category', 
        'instation', 'outstation', 'working_hours', 'support_product', 'proposal_attachment','reference'
        ]
    fieldsets = (
        ('New Application', {'fields': ('reference', 'counter', 'invitation', 'applicant','name', 'registered_name', 'status',)}),
        ('Vendor Size Determinants', {'fields': ('max_member_per_team', 'regional_availability',)}),
        ('SLA Operations', {'fields': ('instation', 'outstation', 'working_hours', 'category', 'support_product')}),
        ('Application Files', {'fields': (
            'proposal_attachment','company_attachment_1', 'company_attachment_2', 'company_attachment_3',
        )}),
    )
    radio_fields = {
        'regional_availability': admin.HORIZONTAL,
        'working_hours': admin.HORIZONTAL,
    } 

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = ['reference', 'application', 'mode', 'access', 'status']
    readonly_fields = [
        'reference', 'name', 'email', 'application', 'mode', 'access', 'token', 'status', 'panelist','created_at',
    ]


@admin.register(Grading)
class GradingAdmin(admin.ModelAdmin):
    list_display = ['id','get_panelist', 'application', 'total_marks']
    list_display_links = ['id','get_panelist','application']
    list_filter=['application__invitation__tender']
    readonly_fields = [
        'id', 'created_at', 'criteria1', 'criteria2', 'criteria3', 'criteria4', 'criteria5',
        'criteria6',

        'marks1', 'marks2', 'marks3', 'marks4', 'marks5',
        'marks6',
    ]
    fieldsets = (
        ('Grading One', {'fields': ('criteria1', 'marks1',)}),
        ('Grading Two', {'fields': ('criteria2', 'marks2',)}),
        ('Grading Three', {'fields': ('criteria3', 'marks3',)}),
        ('Grading Four', {'fields': ('criteria4', 'marks4',)}),
        ('Grading Five', {'fields': ('criteria5', 'marks5',)}),
        ('Grading Six', {'fields': ('criteria6', 'marks6',)}),

    )

    @admin.display(description='Panelist', ordering='')
    def get_panelist(self, obj):

        if obj.panelist.mode == 'internal':
            return obj.panelist.panelist.get_full_name()
        else:
            return obj.panelist.name
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(ActiveVendor)
class ActiveVendorAdmin(admin.ModelAdmin):  
    list_display = ['name', 'category', 'working_hours', 'status', 'ordering']
    list_editable = ['status','ordering']
    list_filter = ['category','status']
    search_fields = ['name', 'registered_name'] 
    readonly_fields = ['created_at', 'track_working_time']
    fieldsets = (
        ('Basic Info', {'fields': ('email', 'name', 'registered_name', 'ordering',)}),
        ('Classification', {'fields': ('status', 'category', 'purpose',)}),
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


@admin.register(BlacklistedVendor)
class BlacklistedVendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'working_hours', 'status', 'ordering']
    list_editable = ['status','ordering']
    list_filter = ['category','status']
    search_fields = ['name', 'registered_name'] 
    readonly_fields = ['created_at', 'track_working_time']
    fieldsets = (
        ('Basic Info', {'fields': ('email', 'name', 'registered_name', 'ordering',)}),
        ('Classification', {'fields': ('status', 'category', 'reason',)}),
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

