from django.core.exceptions import ValidationError
from .models import Custodian, HelpDesk, HelpDeskMessage
from django import forms
from account.models import Customer
from django.utils.translation import gettext_lazy as _
from general_settings.models import Category, Branch


class CustodianProfileForm(forms.ModelForm):
    profile_photo = forms.ImageField(widget=forms.FileInput,)

    class Meta:
        model = Custodian
        fields = ['gender', 'tagline','description', 'address', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Personal Details   
        self.fields['gender'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Select Gender'})         
        self.fields['tagline'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'tagline'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'description'})
        self.fields['address'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Country address'})
        self.fields['profile_photo'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'profile photo'})

            
class HelpDeskForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), empty_label='Select Category'
    )
    file = forms.ImageField(widget=forms.FileInput,label="Attachment(Optional)")
    class Meta:
        model = HelpDesk
        fields = ['title', 'category', 'condition', 'content', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(meta=False)

         # Personal Details   
        self.fields['title'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Title'})         
        self.fields['category'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})         
        self.fields['condition'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['content'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'description'})
        self.fields['file'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'upload file'})


class RoutingForm(forms.ModelForm):
    support_branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(), 
        empty_label='Select Routing Branch'
    )

    class Meta:
        model = HelpDesk
        fields = ['support_branch']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['support_branch'].queryset = Branch.objects.filter(status=True)
 
        self.fields['support_branch'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})


class HelpDeskMessageForm(forms.ModelForm):
    class Meta:
        model = HelpDeskMessage
        fields = ['content']
        required = ['content']
        readonly = ['content']
        disabled = ['content']
        
    def __init__(self, *args, **kwargs):
        super(HelpDeskMessageForm, self).__init__(*args, **kwargs)
         # Personal Details   
        self.fields['content'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Start typing something'}) 

        for field in self.Meta.required:
            self.fields[field].required = True

        for field in self.Meta.disabled:
            if self.instance.pk:
                self.fields[field].widget.attrs["disabled"] = True

        for field in self.Meta.readonly:
            if self.instance.pk:
                self.fields[field].widget.attrs["readonly"] = True


class HelpDeskStatusForm(forms.ModelForm):
    ACTIVE = 'active'
    CLOSED = 'closed'
    STATUS = (
        (ACTIVE, 'Active'),
        (CLOSED, 'Close'),
    )
    status = forms.ChoiceField(required=True, choices=STATUS, label="Select Status")
    
    class Meta:
        model = HelpDesk
        fields = ['status']
        required = ['status']

    def __init__(self, *args, **kwargs):
        super(HelpDeskStatusForm, self).__init__(*args, **kwargs)

        self.fields['status'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})

        for field in self.Meta.required:
            self.fields[field].required = True