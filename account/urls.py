from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import PasswordResetForm, PasswordResetConfirmForm
from django.views.generic import TemplateView
from . import views
from general_settings.utilities import (
    website_name,
    get_protocol_with_domain_path,
)

app_name = 'account'

# shared accounts app urls
urlpatterns = [
    path("", views.homepage, name='homepage'),
    path("login/", views.loginView, name = "login"),
    path("logout/", views.Logout, name = "logout"),
    path("autologout/", views.autologout, name="autologout"),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('register/', views.account_register, name='register'),
    path("activate/<slug:uidb64>/<slug:token>)/", views.account_activate, name="activate"),
    path("password_creation/", views.password_creation, name='password_creation'),
    path("password_confirm/", views.password_confirm, name='password_confirm'),
    path("account/two-factor-auth/", views.two_factor_auth, name = "two_factor_auth"),      
    # User Reset password
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="account/user/password_reset_form.html",
        success_url="password_reset_email_confirm",
        email_template_name="account/user/password_reset_email.html",
        extra_context = {'protocol_with_domain_path':get_protocol_with_domain_path(), 'website_name':website_name()},
        form_class=PasswordResetForm,
    ),
        name="passwordreset",
    ),
    path("password_reset_confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(
        template_name="account/user/password_reset_confirm.html",
        success_url="/password_reset_complete/",
        extra_context = {'protocol_with_domain_path':get_protocol_with_domain_path(), 'website_name':website_name()},        
        form_class=PasswordResetConfirmForm,
    ),
        name="password_reset_confirm",
    ),
    path("password_reset/password_reset_email_confirm/", TemplateView.as_view(
        template_name="account/user/reset_status.html"),
        name="password_reset_done",
    ),
    path("password_reset_complete/", TemplateView.as_view(
        template_name="account/user/reset_status.html"),
        name="password_reset_complete",
    ),
        
]

htmx_urlpatterns = [
    path("verify_username/", views.verify_username, name = "verify_username"), 
]

urlpatterns += htmx_urlpatterns
