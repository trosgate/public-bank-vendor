from django.contrib import admin
from .models import Authenticator, Notifier

MAX_OBJECTS = 1

@admin.register(Authenticator)
class AuthenticatorAdmin(admin.ModelAdmin):

    list_display = ['preview']
    list_display_links = ['preview']
    readonly_fields = ['preview']

    fieldsets = (
        ('#1 - Two Factor Authenticator(Email Alert Available)', {'fields': ('token_authenticator',)}),       
        ('#2 - Vendor Team Upgrade Plugin', {'fields': ('vendor_role',)}),
    )

    radio_fields = {
        'token_authenticator': admin.HORIZONTAL,
        'vendor_role': admin.HORIZONTAL,
    }

    def get_queryset(self, request):
        qs = super(AuthenticatorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.all()  
        else:
            return qs.filter(pk=0)


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


@admin.register(Notifier)
class NotifierAdmin(admin.ModelAdmin):

    list_display = ['preview']
    list_display_links = ['preview']
    readonly_fields = ['preview']
    fieldsets = (
    	('Take charge of the notifications in every part of the software', {'fields': ('preview',)}),
        ('#1 - Mailing Group Plugin/Switch', {'fields': ('mailing_group',)}),       
        ('#2 - Ticket Notification Plugin/Switch', {'fields': ('open_ticket', 'assign_ticket', 'started_ticket','deferred_ticket',
            'reopen_ticket','closed_ticket', 'remarks',)}),       
        ('#3 - Complaint Notification Plugin/Switch', {'fields': ('complaint_created','complaint_routing','complaint_reply',)}),                 
        ('#4 - Requisition Notification Plugin/Switch', {'fields': ('requisition_created',)}),
    )
    radio_fields = {
        'mailing_group': admin.HORIZONTAL,
        'open_ticket': admin.HORIZONTAL,
        'assign_ticket': admin.HORIZONTAL,
        'started_ticket': admin.HORIZONTAL,
        'deferred_ticket': admin.HORIZONTAL,
        'reopen_ticket': admin.HORIZONTAL,
        'closed_ticket': admin.HORIZONTAL,
        'remarks': admin.HORIZONTAL,
        'complaint_created': admin.HORIZONTAL,
        'complaint_routing': admin.HORIZONTAL,
        'complaint_reply': admin.HORIZONTAL,
        'requisition_created': admin.HORIZONTAL,
    }

    def get_queryset(self, request):
        qs = super(NotifierAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.all()  
        else:
            return qs.filter(pk=0)

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
