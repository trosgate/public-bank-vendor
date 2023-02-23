from django.contrib import admin
from .models import Custodian, HelpDesk, HelpDeskMessage
import sys


@admin.register(Custodian)
class CustodianAdmin(admin.ModelAdmin):
    list_display = ['user', 'tagline', 'image_tag',]
    list_display_links = ['user','tagline']    
    readonly_fields = ['user', 'image_tag']
    list_per_page = sys.maxsize
    search_fields = ('user__short_name','gender','tagline',)
    fieldsets = (
        ('Personal info', {'fields': ('user', 'gender', 'image_tag', 'profile_photo',)}),
        ('Background and Description', {'fields': ('address', 'tagline','description',)})
    )

    def get_queryset(self, request):
        qs = super(CustodianAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(user=request.user) 
        else:
            return qs.filter(pk=0)  

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        disabled_fields = set() 

        if obj is not None and obj.user != request.user:            
            disabled_fields |= {
                'gender', 
                'profile_photo',
                'address', 
                'tagline',
                'description',
            }

       
        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        
        return form


class HelpDeskMessageInline(admin.StackedInline):
    model = HelpDeskMessage
    readonly_fields = ('support', 'content', 'created_at',)
    extra = 0

    fieldsets = (
        ('Reply Body', {'fields': ('content',)}),
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HelpDesk)
class HelpDeskAdmin(admin.ModelAdmin):
    list_display = ['created_by', 'reference', 'request_branch', 'title', 'created_at']
    list_display_links = ['created_by', 'title']
    search_fields=['reference','title','request_branch__name','support_branch__name']
    list_filter = ['category', 'status']
    readonly_fields = [
        'title',  'category', 'slug', 'reference', 'condition', 'status','content','created_by',
        'request_branch', 'support_branch', 'created_at', 'modified_at'
    ]

    fieldsets = (
        ('Introduction', {'fields': ('title',  'slug', 'category', 'condition', 'reference', 'status',)}),
        ('Support Detail', {'fields': ('content', 'file', 'is_routed',)}),
        ('Other Info', {'fields': ('created_by', 'request_branch', 'support_branch', 'created_at', 'modified_at',)}),
    )
    radio_fields = {'status': admin.HORIZONTAL}
    inlines = [HelpDeskMessageInline]

    @admin.display(description='Customer Type', ordering='created_by__user_type')
    def get_user_type(self, obj):
        return obj.created_by.get_user_type_display()
        
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions 