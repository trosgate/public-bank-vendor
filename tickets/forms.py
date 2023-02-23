from django import forms
from .models import Ticket, AssignMember
from general_settings.models import Terminals, Category, SLAExceptions
from account.models import Customer



class TicketForm(forms.ModelForm):
    terminal = forms.ModelChoiceField(
        queryset=Ticket.objects.all(), empty_label='Select Branch Terminal'
    )
  
    class Meta:
        model = Ticket
        fields = ['title', 'category', 'terminal', 'description']
        required = ['title', 'category', 'terminal', 'description']


    def __init__(self, branch, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['terminal'].queryset = Terminals.objects.filter(branch=branch)
        self.fields['category'].queryset = Category.objects.filter(meta=True)

        self.fields['title'].widget.attrs.update(
            {'class': 'form-control col-12 float-left', 'placeholder': ''})

        self.fields['category'].widget.attrs.update(
            {'class': 'form-control col-12 float-left', 'placeholder': ''})

        self.fields['terminal'].widget.attrs.update(
            {'class': 'form-control col-12 float-left', 'placeholder': ''})
        
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control col-12 float-left', 'placeholder': ''})
        
        
        for field in self.Meta.required:
            self.fields[field].required = True


class AssignForm(forms.ModelForm):
    assignee = forms.ModelChoiceField(queryset=AssignMember.objects.all(), empty_label='Select Team Member')

    class Meta:
        model = AssignMember
        fields = ['assignee'] 

    def __init__(self, assignee, *args, **kwargs):
        super(AssignForm, self).__init__(*args, **kwargs)
        self.fields['assignee'].queryset = Customer.objects.filter(team_member__in=assignee)

        self.fields['assignee'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})


class SLAExceptionsForm(forms.ModelForm):
    name = forms.ModelChoiceField(queryset=SLAExceptions.objects.all(), empty_label='Select deferring factor')

    class Meta:
        model = SLAExceptions
        fields = ['name'] 
        required = ['name']

    def __init__(self, *args, **kwargs):
        super(SLAExceptionsForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})

        for field in self.Meta.required:
            self.fields[field].required = True
