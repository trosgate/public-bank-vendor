from django.contrib import admin
from .models import InventoryRequest, RequisitionReview, RequisitionIssued, RequisitionClosed


# @admin.register(InventoryRequest)
# class InventoryRequestAdmin(admin.ModelAdmin):
#     list_display = ['reference', 'category', 'request_branch', 'request_at','status']
#     list_display_links = ['reference', 'category']
#     search_fields = ['reference', 'category__name', 'request_branch__name', 'line_one']
#     readonly_fields = [
#         'category', 'slug', 'reference', 
#         'status', 'request_branch', 'request_by','request_message',
#         'line_one', 'line_one_order', 'line_one_issue',
#         'line_two', 'line_two_order', 'line_two_issue',
#         'line_three', 'line_three_order', 'line_three_issue',
#         'line_four', 'line_four_order', 'line_four_issue',
#         'issue_branch', 'issued_by', 'issue_remark',
#         'request_at', 'issue_at', 'receive_at'
#         ]

#     fieldsets = (
#         ('Request Description', {'fields': ('category', 'slug', 'reference', 'status', 'request_branch', 'request_by','request_message',)}), 
#         ('Line One Items', {'fields': ('line_one', 'line_one_order', 'line_one_issue',)}),
#         ('Line Two Items', {'fields': ('line_two', 'line_two_order', 'line_two_issue',)}),
#         ('Line Three Items', {'fields': ('line_three', 'line_three_order', 'line_three_issue')}),
#         ('Line Four Items', {'fields': ('line_four', 'line_four_order', 'line_four_issue')}),
#         ('Fulfilling Order', {'fields': ('issue_branch', 'issued_by', 'issue_remark',)}),
#         ('Activity Log', {'fields': ('request_at', 'issue_at', 'receive_at')}),
#     )

#     def has_add_permission(self, request):
#         return False

#     def get_actions(self, request):
#         actions = super().get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions

#     def has_delete_permission(self, request, obj=None):
#         return False


@admin.register(RequisitionReview)
class RequisitionReviewAdmin(admin.ModelAdmin):
    list_display = ['reference', 'category', 'request_branch', 'request_at']
    list_display_links = ['reference', 'category']
    search_fields = ['reference', 'category__name', 'request_branch__name', 'line_one']
    readonly_fields = [
        'category', 'slug', 'reference', 
        'status', 'request_branch', 'request_by','request_message',
        'line_one', 'line_one_order', 'line_one_issue',
        'line_two', 'line_two_order', 'line_two_issue',
        'line_three', 'line_three_order', 'line_three_issue',
        'line_four', 'line_four_order', 'line_four_issue',
        'issue_branch', 'issued_by', 'issue_remark',
        'request_at', 'issue_at', 'receive_at'
        ]

    fieldsets = (
        ('Request Description', {'fields': ('category', 'slug', 'reference', 'status', 'request_branch', 'request_by','request_message',)}), 
        ('Line One Items', {'fields': ('line_one', 'line_one_order', 'line_one_issue',)}),
        ('Line Two Items', {'fields': ('line_two', 'line_two_order', 'line_two_issue',)}),
        ('Line Three Items', {'fields': ('line_three', 'line_three_order', 'line_three_issue')}),
        ('Line Four Items', {'fields': ('line_four', 'line_four_order', 'line_four_issue')}),
        ('Fulfilling Order', {'fields': ('issue_branch', 'issued_by', 'issue_remark',)}),
        ('Activity Log', {'fields': ('request_at', 'issue_at', 'receive_at')}),
    ) 
       
    def get_queryset(self, request):
        qs = super(RequisitionReviewAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(status="review")  
        else:
            return qs.filter(issued_by=request.user, status="review")    

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RequisitionIssued)
class RequisitionIssuedAdmin(admin.ModelAdmin):
    list_display = ['reference', 'category', 'request_branch', 'request_at']
    list_display_links = ['reference', 'category']
    search_fields = ['reference', 'category__name', 'request_branch__name', 'line_one']
    readonly_fields = [
        'category', 'slug', 'reference', 
        'status', 'request_branch', 'request_by','request_message',
        'line_one', 'line_one_order', 'line_one_issue',
        'line_two', 'line_two_order', 'line_two_issue',
        'line_three', 'line_three_order', 'line_three_issue',
        'line_four', 'line_four_order', 'line_four_issue',
        'issue_branch', 'issued_by', 'issue_remark',
        'request_at', 'issue_at', 'receive_at'
        ]

    fieldsets = (
        ('Request Description', {'fields': ('category', 'slug', 'reference', 'status', 'request_branch', 'request_by','request_message',)}), 
        ('Line One Items', {'fields': ('line_one', 'line_one_order', 'line_one_issue',)}),
        ('Line Two Items', {'fields': ('line_two', 'line_two_order', 'line_two_issue',)}),
        ('Line Three Items', {'fields': ('line_three', 'line_three_order', 'line_three_issue')}),
        ('Line Four Items', {'fields': ('line_four', 'line_four_order', 'line_four_issue')}),
        ('Fulfilling Order', {'fields': ('issue_branch', 'issued_by', 'issue_remark',)}),
        ('Activity Log', {'fields': ('request_at', 'issue_at', 'receive_at')}),
    ) 
       
    def get_queryset(self, request):
        qs = super(RequisitionIssuedAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(status="issued")  
        else:
            return qs.filter(issued_by=request.user, status="issued")    

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RequisitionClosed)
class RequisitionClosedAdmin(admin.ModelAdmin):
    list_display = ['reference', 'category', 'request_branch', 'request_at']
    list_display_links = ['reference', 'category']
    search_fields = ['reference', 'category__name', 'request_branch__name', 'line_one']
    readonly_fields = [
        'category', 'slug', 'reference', 
        'status', 'request_branch', 'request_by','request_message',
        'line_one', 'line_one_order', 'line_one_issue',
        'line_two', 'line_two_order', 'line_two_issue',
        'line_three', 'line_three_order', 'line_three_issue',
        'line_four', 'line_four_order', 'line_four_issue',
        'issue_branch', 'issued_by', 'issue_remark',
        'request_at', 'issue_at', 'receive_at'
        ]

    fieldsets = (
        ('Request Description', {'fields': ('category', 'slug', 'reference', 'status', 'request_branch', 'request_by','request_message',)}), 
        ('Line One Items', {'fields': ('line_one', 'line_one_order', 'line_one_issue',)}),
        ('Line Two Items', {'fields': ('line_two', 'line_two_order', 'line_two_issue',)}),
        ('Line Three Items', {'fields': ('line_three', 'line_three_order', 'line_three_issue')}),
        ('Line Four Items', {'fields': ('line_four', 'line_four_order', 'line_four_issue')}),
        ('Fulfilling Order', {'fields': ('issue_branch', 'issued_by', 'issue_remark',)}),
        ('Activity Log', {'fields': ('request_at', 'issue_at', 'receive_at')}),
    ) 
       
    def get_queryset(self, request):
        qs = super(RequisitionClosedAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(status="closed")  
        else:
            return qs.filter(issued_by=request.user, status="closed")    

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False