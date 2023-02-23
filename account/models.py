from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)
from . managers import UserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.safestring import mark_safe
from django.urls import reverse
from . utilities import auth_code
from django_cryptography.fields import encrypt
from django.core.exceptions import ValidationError


class Customer(AbstractBaseUser, PermissionsMixin):

    ADMIN = 'admin'
    VENDOR = 'vendor'
    CUSTODIAN = 'custodian'
    INITIATOR = 'initiator'
    OFFICER = 'officer'
    HEAD = 'head'    
    USER_TYPE = (
        (ADMIN, _('Administrator')),
        (VENDOR, _('Vendor, ATM')),
        (CUSTODIAN, _('Custodian, ATM')),
        (INITIATOR, _('Member, Onboarding')),
        (OFFICER, _('Lead, Onboarding')),
        (HEAD, _('Head, Onboarding')),        
    )
   
    email = models.EmailField(_("Email Address"), max_length=100, unique=True)
    short_name = models.CharField(_("Username"), max_length=30, unique=True)
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    phone = models.CharField(_("Phone"), max_length=20, blank=True, null=True)
    is_active = models.BooleanField(_("Active User"), default=True, help_text="Important: This controls login access for All staffs and Vendors")
    is_staff = models.BooleanField(_("Permit Staff"), default=False, help_text="Important: This is extra login control for All Staffs only")
    is_superuser = models.BooleanField(_("Administrator"), default=False)
    is_assistant = models.BooleanField(_("Admin's Assistant"), default=False)
    is_stakeholder = models.BooleanField(_("Onboarding Group"), default=False, help_text="This indicates that the staff is one of the Onboarding members")
    is_vendor = models.BooleanField(_("Vendor Admin"), default=False, help_text="Important: This attribute determine Vendor Admin from their team")
    user_type = models.CharField(_("User Type"), choices=USER_TYPE, max_length=30)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)
    last_login = models.DateTimeField(_("Last Login"), auto_now=True)
    vendor_company = models.ForeignKey(
        'general_settings.VendorCompany', 
        verbose_name=_("Vendor Company"),  
        null=True, 
        blank=True,
        help_text="This option is only applicable to vendor type of users", 
        on_delete=models.CASCADE #RESTRICT
    )
    branch = models.ForeignKey(
        'general_settings.Branch', 
        verbose_name=_("Branch or Unit"),
        related_name="branch",  
        null=True, 
        blank=True,
        help_text="This option is only applicable to staffs", 
        on_delete=models.CASCADE #RESTRICT
    )

    class Meta:
        ordering = ("date_joined",)
        verbose_name = "User Manager"
        verbose_name_plural = "User Manager"

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['short_name']
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.short_name

    def get_username(self):
        return self.email

    def get_first_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def clean(self):
        if self.is_superuser == True and self.is_vendor == True:
            raise ValidationError(
                {'is_vendor': _('An administrator cannot be a vendor')})
        
        if self.is_assistant == True and self.is_vendor == True:
            raise ValidationError(
                {'is_vendor': _('An assistant is part of staff and cannot be a vendor')})
        
        if self.is_superuser == True and self.is_assistant == True:
            raise ValidationError(
                {'is_assistant': _('An assistant cannot be an Administrator at the same time')})
        
        if self.is_superuser == True and self.is_staff == False:
            raise ValidationError(
                {'is_staff': _('Administrator must have "Active Staff" status')})
        
        if self.is_assistant == True and self.is_staff == False:
            raise ValidationError(
                {'is_staff': _('Assistant must have "Active Staff" status')})
        
        if self.is_stakeholder == True and self.is_staff == False:
            raise ValidationError(
                {'is_staff': _('Stakeholder must have "Active Staff" status')})
        
        if self.user_type == 'vendor' and self.is_assistant == True:
            raise ValidationError(
                {'is_assistant': _('Vendor cannot be a Staff or Assistant.')})
        
        if self.user_type == 'vendor' and self.vendor_company is None:
            raise ValidationError(
                {'vendor_company': _('Vendor company is required for all vendor creation')})
        
        if self.user_type == 'custodian' and self.vendor_company is not None:
            raise ValidationError(
                {'vendor_company': _('Vendor company cannot be associated with staff')})
        
        if self.user_type == 'custodian' and self.branch is None:
            raise ValidationError(
                {'branch': _('A staff must be mapped to a particular branch or unit')})
        
        if self.user_type == 'initiator' and self.branch is None:
            raise ValidationError(
                {'branch': _('Stakeholder/Officer must be mapped to a particular branch or unit')})
        
        if self.user_type == 'officer' and self.branch is None:
            raise ValidationError(
                {'branch': _('Stakeholder/Officer must be mapped to a particular branch or unit')})
        
        if self.user_type == 'head' and self.branch is None:
            raise ValidationError(
                {'branch': _('Stakeholder/Staff must be mapped to a particular branch or unit')})
        
        if self.user_type == 'vendor' and self.branch is not None:
            raise ValidationError(
                {'branch': _('A Vendor cannot be mapped to a branch or unit')})
        
        if self.user_type == 'admin' and self.branch is None:
            raise ValidationError(
                {'branch': _('As a staff, you must be mapped to a particular branch or unit')})

        if self.user_type == 'admin' and self.vendor_company is not None:
            raise ValidationError(
                {'vendor_company': _('Vendor company cannot be associated with admin')})
        

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='twofactorauth', on_delete=models.CASCADE)
    pass_code = encrypt(models.CharField(_("Access Token"), max_length=255, blank=True, null=True))
    last_login = models.DateTimeField(_("Last Login"), auto_now=True)
    
    def __str__(self):
        return f'{self.user.get_full_name()}'    

    class Meta:
        ordering = ("last_login",)
        verbose_name = "Access Token"
        verbose_name_plural = "Access Token"

    def save(self, *args, **kwargs):
        self.pass_code = auth_code()
        super(TwoFactorAuth, self).save(*args, **kwargs)

































