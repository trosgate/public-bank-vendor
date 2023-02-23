from django.contrib import admin
from .models import Ticket, AssignMember


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['reference', 'title', 'terminal', 'status']
    list_display_links = ['reference', 'title']
    list_filter = ['status', 'team', 'category']
    search_fields = ['reference', 'title', 'terminal__name']
    readonly_fields = [
        'title', 'slug', 'description', 'branch', 'team','category', 'status', 
        'remarks','created_by','terminal', 'arrival_time', 'reference',
        'sla_exception', 'checklist', 'remarks_date','created_at', 'timestamp'
    ]

    fieldsets = (
        ('Introduction', {'fields': ('title', 'slug','sla_exception',)}),
        ('Ticket Attributes', {'fields': ('created_by', 'timestamp','category', 'team','branch', 'terminal', 'reference','status','arrival_time',)}),
        ('Ticket Clossure', {'fields': ('checklist', 'remarks', 'remarks_date',)}),
    )
    radio_fields = {'status': admin.HORIZONTAL}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions 


@admin.register(AssignMember)
class AssignMemberAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'assignee', 'get_ticket', 'get_branch', 'created_at', 'total_minutes', 'get_ticket_status']
    search_fields = ['vendor__name', 'assignee__first_name', 'assignee__last_name', 'ticket__reference', 'ticket__branch__name']
    # list_display_links = None
    readonly_fields = [
        'vendor', 'team', 'ticket', 'assignor', 'assignee','created_at','arrival_time',
        'arrival_confirm', 'completion_time', 'total_minutes', 'deffered_count', 'get_ticket_status'
    ]

    fieldsets = (
        ('Assignment Detail', {'fields': ('vendor', 'team', 'ticket', 'assignor', 'assignee','created_at',)}),
    )

    @admin.display(description='Ticket #', ordering='ticket__reference')
    def get_ticket(self, obj):
        return obj.ticket.reference

    @admin.display(description='Status', ordering='ticket__status')
    def get_ticket_status(self, obj):
        return obj.ticket.get_status_display()

    @admin.display(description='Branch', ordering='ticket__branch')
    def get_branch(self, obj):
        return obj.ticket.branch

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions    