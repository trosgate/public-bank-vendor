from django.db import transaction as db_transaction
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from . models import Customer, TwoFactorAuth
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils.text import slugify
from vendors.models import Team, Vendor
from custodians.models import Custodian
from .tasks import user_creation


class SearchTypeForm(forms.Form):
    WELCOME = 'welcome'
    VENDOR = 'vendor'
    BANK = 'bank'
    USER_TYPE = (
        (WELCOME, _('Select form option')),
        (VENDOR, _('Vendor')),
        (BANK, _('Bank')),
    )
   
    search_type = forms.ChoiceField(choices=USER_TYPE, label="Select Type")

    def __init__(self, *args, **kwargs):
        super(SearchTypeForm, self).__init__(*args, **kwargs)

        self.fields['search_type'].widget.attrs.update(
            {'class': 'form-control'})


class VendorCreationForm(forms.ModelForm):
    short_name = forms.CharField(label='Username', min_length=4, max_length=30)
    email = forms.EmailField(label='Email', max_length=100)
    first_name = forms.CharField(label='First Name',  min_length=2, max_length=50)
    last_name = forms.CharField(label='Last Name', min_length=2, max_length=50)
    phone = forms.CharField(label='Phone', min_length=2, max_length=50)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name','email', 'short_name', 'phone']    
        required = ['first_name', 'last_name','email', 'short_name', 'phone']               


    def __init__(self, *args, **kwargs):
        super(VendorCreationForm, self).__init__(*args, **kwargs)

        self.fields['short_name'].widget.attrs.update(
            {'class': 'input-group col-lg-12'})
        self.fields['email'].widget.attrs.update(
            {'class': 'input-group col-lg-12',})
        self.fields['first_name'].widget.attrs.update(
            {'class': 'input-group col-lg-12',})
        self.fields['last_name'].widget.attrs.update(
            {'class': 'input-group col-lg-12',})
        self.fields['phone'].widget.attrs.update(
            {'class': 'input-group col-lg-12',})

        for field in self.Meta.required:
            self.fields[field].required = True

    def clean_short_name(self):
        short_name = self.cleaned_data['short_name'].lower()
        a = Customer.objects.filter(short_name=short_name)
        if a.count():
            raise forms.ValidationError(_("Username already exists"))
        return short_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Oops! Email taken. Please try another Email"))
        if not email.islower():
            raise forms.ValidationError(_("Email characters must all be in lowercase"))
        return email


class VendorPasswordForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'login-pwd',
        }
    ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'id': 'login-pwd2',
        }
    ))
    class Meta:
        model = Customer
        fields = ['password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password1


class UserLoginForm(AuthenticationForm):
    email = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Email Address',
               'id': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'login-pwd',
        }
    ))


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email', 'id': 'form-email'}))

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     obj = Customer.objects.get(email=self.email)
    #     context["email"] = obj.email
    #     context.update({
    #     'email': self.email,
    #     **(self.extra_context or {})
    #     })
    #     return context        


    def clean_email(self):
        email = self.cleaned_data['email']
        cust_email = Customer.objects.filter(email=email)
        if not cust_email:
            raise forms.ValidationError(
                'Ooops! the input detail(s) is not valid')
        return email


class PasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-newpass'}))
    new_password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-new-pass2'}))


class TwoFactorAuthForm(forms.ModelForm): 
    pass_code = forms.CharField(help_text = "Enter verification token sent to your email")

    class Meta:
        model = TwoFactorAuth
        fields = ['pass_code']
          
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Personal Details   
        self.fields['pass_code'].widget.attrs.update(
            {'class': 'form-control',})

    def clean_passcode(self):
        pass_code = self.cleaned_data['pass_code']
        checker = TwoFactorAuth.objects.filter(pass_code=pass_code)

        if not checker:    
            raise forms.ValidationError(
                _('Invalid token entered. Please check and try again'))
        return pass_code


class CustomerAdminCreationForm(forms.ModelForm):
    SELECT_CATEGORY = '........'
    VENDOR = 'vendor'
    CUSTODIAN = 'custodian'
    INITIATOR = 'initiator'
    OFFICER = 'officer'
    HEAD = 'head'    
    USER_TYPE = (
        (SELECT_CATEGORY, _('Select User Category')),
        (VENDOR, _('Vendor, ATM')),
        (CUSTODIAN, _('Custodian, ATM')),
        (INITIATOR, _('Initiator, Onboarding')),
        (OFFICER, _('Officer, Onboarding')),
        (HEAD, _('Head, Onboarding')),        
    )
    user_type = forms.ChoiceField(choices=USER_TYPE, label="Select User",)    
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput,)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput,)

    class Meta:
        model = Customer
        fields = ('email', 'user_type', 'short_name','first_name','last_name')


    def clean_email(self):
        email = self.cleaned_data['email']
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Oops! Email taken. Please try another Email"))
        
        if not email.islower():
            raise forms.ValidationError(_("Email characters must all be in lowercase"))
        return email

    def clean_short_name(self):
        short_name = self.cleaned_data['short_name'].lower()
        a = Customer.objects.filter(short_name=short_name)
        if a.count():
            raise forms.ValidationError(_("Username already exists"))
        return short_name

    def clean_with_vendor_company(self):
        vendor_company = self.cleaned_data.get("vendor_company")
        a = Customer.objects.filter(vendor_company=vendor_company)
        if a.count():
            raise forms.ValidationError(_("A vendor with this company already exists. You can still replace existing user with the new user credentials"))
        return vendor_company

    def clean_vendor_company(self):
        vendor_company = self.cleaned_data.get("vendor_company")
        user_type = self.cleaned_data.get("user_type")
        if user_type == 'custodian' and vendor_company is not None:
            raise forms.ValidationError(_("Vendor company is only reserved for vendor type of users"))
        
        if user_type == 'initiator' and vendor_company is not None:
            raise forms.ValidationError(_("Vendor company is only reserved for vendor type of users"))
        
        if user_type == 'officer' and vendor_company is not None:
            raise forms.ValidationError(_("Vendor company is only reserved for vendor type of users"))
        
        if user_type == 'head' and vendor_company is not None:
            raise forms.ValidationError(_("Vendor company is only reserved for vendor type of users"))
        
        if user_type == 'vendor' and vendor_company is None:
            raise forms.ValidationError(_("Vendor company is required to create a vendor"))
        return vendor_company

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if len(password1) < 5:
            raise ValidationError("All password strength should be at least eight characters long")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    @db_transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.short_name = self.cleaned_data.get('short_name')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.vendor_company = self.cleaned_data.get('vendor_company')
        user.phone = self.cleaned_data.get('phone')
        user_type = self.cleaned_data.get("user_type")
        
        if user_type == 'vendor':
            user.is_vendor = True
            user.is_superuser = False
            user.is_staff = False
            
        elif user_type == 'custodian':
            user.is_staff = True

        elif user_type == 'officer':
            user.is_staff = True
            user.is_stakeholder = True

        elif user_type == 'initiator':
            user.is_staff = True
            user.is_stakeholder = True

        elif user_type == 'head':
            user.is_staff = True
            user.is_stakeholder = True

        user.set_password(self.cleaned_data["password1"])
        user.save()
        
        if user_type == 'vendor':

            team = Team.objects.get_or_create(
                title=user.vendor_company.name,
                purpose=f"This is {user.vendor_company.name} team", 
                created_by = user,
                slug = slugify(user.vendor_company.name)
            )[0]
            team.members.add(user)
            vendor_profile = Vendor.objects.get_or_create(user=user)[0]

            new_vendor = vendor_profile
            new_vendor.active_team_id = team.pk
            new_vendor.save()
        
        else:
            Custodian.objects.get_or_create(user=user)[0]

        db_transaction.on_commit(lambda: user_creation.delay(user.pk))
       
        return user

