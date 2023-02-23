from django.core.exceptions import ValidationError
from .models import Team, TeamChat, Vendor
from django import forms
from account.models import Customer
from django.utils.translation import gettext_lazy as _


class TeamCreationForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ['title','purpose'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update(
            {'class': 'form-control col-xs-12 col-sm-12 col-md-12 col-lg-12 float-center'})

        self.fields['purpose'].widget.attrs.update(
            {'class': 'form-control col-xs-12 col-sm-12 col-md-12 col-lg-12 float-center'})


class TeamChatForm(forms.ModelForm):
    content = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control col-xs-12 col-sm-12 col-md-12 col-lg-6 float-center', 'placeholder': 'send a message',}))

    class Meta:
        model = TeamChat
        fields = ['content'] 


class VendorProfileForm(forms.ModelForm): 
    profile_photo = forms.ImageField(widget=forms.FileInput,)

    class Meta:
        model = Vendor
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
