from django import forms
from .models import Composer, Tender, Contacts, Parameters, Invitation, Application, Panelist, Grading
from general_settings.models import Category, SupportProduct
from django.utils.translation import gettext_lazy as _


class DateInput(forms.DateInput):
    input_type = 'date'


class InstructionForm(forms.ModelForm):
    class Meta:        
        model = Composer
        fields = ['applicant_instruction'] 

    def __init__(self, *args, **kwargs):
        super(InstructionForm, self).__init__(*args, **kwargs)

        self.fields['applicant_instruction'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class InvitemessageForm(forms.ModelForm):
    class Meta:        
        model = Composer
        fields = ['invite_message'] 

    def __init__(self, *args, **kwargs):
        super(InvitemessageForm, self).__init__(*args, **kwargs)

        self.fields['invite_message'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class TenderForm(forms.ModelForm):
    duration = forms.DateField(widget=DateInput, required=True)
    class Meta:        
        model = Tender
        fields = ['title', 'duration', 'number_of_links', 'mode', 'category'] 

    def __init__(self, *args, **kwargs):
        super(TenderForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['duration'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['number_of_links'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['mode'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['category'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class InvitationForm(forms.ModelForm):
    
    class Meta:
        model = Invitation
        fields = ['receiver'] 

    def __init__(self, *args, **kwargs):
        super(InvitationForm, self).__init__(*args, **kwargs)

        self.fields['receiver'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameters
        fields = [
            'criteria1', 'note1', 'criteria2', 'note2', 'criteria3', 'note3', 
            'criteria4', 'note4', 'criteria5', 'note5', 'criteria6', 'note6',
        ]

    def __init__(self, *args, **kwargs):
        super(ParameterForm, self).__init__(*args, **kwargs)

        self.fields['criteria1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['note1'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['note2'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria3'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['note3'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria4'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['note4'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria5'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['note5'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria6'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['note6'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['phone'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class GeneralApplicationForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='Select category', widget=forms.RadioSelect())
    class Meta:
        model = Application
        fields = [
            # New Application Window
            'applicant', 'email', 'name', 'registered_name','max_member_per_team',

            # SLA Operations
            'instation', 'outstation', 'working_hours', 'category', 'regional_availability', 
            # File attachments
            'proposal_attachment','company_attachment_1', 'company_attachment_2', 'company_attachment_3',
        ] 

    def __init__(self, *args, **kwargs):
        super(GeneralApplicationForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(status=True)

        self.fields['applicant'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['registered_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['max_member_per_team'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['regional_availability'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['instation'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['outstation'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['working_hours'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['proposal_attachment'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['company_attachment_1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['company_attachment_2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['company_attachment_3'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class CategorizedApplicationForm(forms.ModelForm):
    # support_product = forms.ModelMultipleChoiceField(queryset=SupportProduct.objects.all())
    class Meta:
        model = Application
        fields = [
            # New Application Window
            'applicant', 'email', 'name', 'registered_name','max_member_per_team','support_product',

            # SLA Operations
            'instation', 'outstation', 'working_hours', 'regional_availability', 
            # File attachments
            'proposal_attachment','company_attachment_1', 'company_attachment_2', 'company_attachment_3',
        ] 

    def __init__(self, category, *args, **kwargs):
        super(CategorizedApplicationForm, self).__init__(*args, **kwargs)
        self.fields['support_product'].queryset = SupportProduct.objects.filter(category=category, status=True)

        self.fields['applicant'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['registered_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['max_member_per_team'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['regional_availability'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['support_product'].widget.attrs.update(
            {'class': 'form-control chosen-select Skills', 'placeholder': ''})
        self.fields['instation'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['outstation'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['working_hours'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['proposal_attachment'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['company_attachment_1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['company_attachment_2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['company_attachment_3'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
            

class PanelistForm(forms.ModelForm):
    class Meta:
        model = Panelist
        fields = ['name',  'email']

    def __init__(self, *args, **kwargs):
        super(PanelistForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update(
            {'class': 'form-control custom-select', 'placeholder': ''})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control custom-select', 'placeholder': ''})
    

class GradingForm(forms.ModelForm):
    class Meta:
        model = Grading
        fields = [
            'criteria1', 'criteria2', 'criteria3', 'criteria4', 'criteria5','criteria6',
            'marks1', 'marks2', 'marks3', 'marks4', 'marks5', 'marks6',
        ]

        required = [
            'criteria1', 'criteria2', 'criteria3', 'criteria4', 'criteria5','criteria6',
            'marks1', 'marks2', 'marks3', 'marks4', 'marks5', 'marks6',
        ]

        readonly = [
            'criteria1', 'criteria2', 'criteria3', 'criteria4', 'criteria5','criteria6',
        ]

    def __init__(self, *args, **kwargs):
        super(GradingForm, self).__init__(*args, **kwargs)

        self.fields['criteria1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['marks1'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['marks2'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria3'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['marks3'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria4'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['marks4'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria5'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['marks5'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        self.fields['criteria6'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['marks6'].widget.attrs.update(
            {'class': 'custom-select', 'placeholder': ''})
        
        for field in self.Meta.required:
            self.fields[field].required = True

        for field in self.Meta.readonly:
            self.fields[field].widget.attrs["readonly"] = True


class ApprovalForm(forms.ModelForm):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    USER_TYPE = (
        (APPROVED, _("Approved")),
        (REJECTED, _("Rejected")),
    )
    status = forms.ChoiceField(choices=USER_TYPE, label="Select Status")    
    class Meta:
        model = Application
        fields = ['status', 'justification',]

    def __init__(self, *args, **kwargs):
        super(ApprovalForm, self).__init__(*args, **kwargs)

        self.fields['status'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['justification'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})

