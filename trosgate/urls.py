
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls', namespace='account')),
    path('vendors/', include('vendors.urls', namespace='vendors')),
    path('custodians/', include('custodians.urls', namespace='custodians')),
    path('layout/', include('general_settings.urls', namespace='generalsettings')),
    path('tickets/', include('tickets.urls', namespace='tickets')),
    path('analytics/', include('reports.urls', namespace='reports')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('onboarding/', include('onboarding.urls', namespace='onboarding')),

    # admin password
    # path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset',),
    # path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done',),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm',),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete',),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "I'vendor Admin"
admin.site.site_title = "I'vendor Admin Portal"
admin.site.index_title = "Welcome to I'vendor Admin"

