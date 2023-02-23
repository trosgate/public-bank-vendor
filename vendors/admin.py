import sys
from django.contrib import admin
from .models import Vendor, Team


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'tagline', 'image_tag']
    list_display_links = ['user','tagline']    
    readonly_fields = [
        'image_tag', 'profile_photo', 'user','gender', 'address', 'tagline','description', 
    ]
    list_per_page = sys.maxsize
    search_fields = ('user__short_name','gender','tagline',)
    fieldsets = (
        ('Personal info', {'fields': ('user', 'gender', 'image_tag', 'profile_photo',)}),
        ('Background and Description', {'fields': ('address', 'tagline','description',)})
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['title', 'purpose', 'status']
    list_display_links = ['title', 'status']
    search_fields = ['title', 'purpose']
    list_filter =  ['status']
    readonly_fields = [
        'created_at', 'updated_at', 'purpose', 'title', 'slug', 'members', 'ordering' 
        
    ]

    fieldsets = (
        ('Introduction', {'fields': ('title', 'slug',  'status')}),
        ('Details and Background', {'fields': ('members','purpose',)}),
    )  

    radio_fields = {'status': admin.HORIZONTAL}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set() 

        if not is_superuser: 
            disabled_fields |= {
                'status',
            }

        for field in disabled_fields:
            if field in form.base_fields:
                form.base_fields[field].disabled = True
        
        return form

    def has_add_permission(self, request):
        return False
        
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

