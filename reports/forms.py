from django.forms import ModelForm
from django import forms
from general_settings.models import VendorCompany, Branch
from django.utils.translation import gettext_lazy as _


class DateInput(forms.DateInput):
    input_type = 'date'

# class MyDateInput(forms.DateInput):
#     input_type = 'datetime-local'


class SearchVendorForm(forms.Form):
    name = forms.ModelChoiceField(queryset=VendorCompany.objects.filter(status=True), empty_label='Select Vendor')
    start_date = forms.DateField(widget=DateInput, required=True)
    end_date = forms.DateField(widget=DateInput, required=True)
    size = forms.IntegerField(initial=10000, required=False)
    
    def __init__(self, *args, **kwargs):
        super(SearchVendorForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update(
            {'class': 'form-control mb-2'})
        self.fields['start_date'].widget.attrs.update(
            {'class': 'form-control mb-2'})
        self.fields['end_date'].widget.attrs.update(
            {'class': 'form-control mb-2'})
        self.fields['size'].widget.attrs.update(
            {'class': 'form-control mb-2'})


class CustomExcelCsvForm(forms.Form):
    EXCEL = 'excel'
    CSV = 'csv'
    DATA_TYPE = (
        (EXCEL, _('Excel')),
        (CSV, _('CSV')),
    )   
    branch = forms.ModelChoiceField(queryset=Branch.objects.filter(status=True), empty_label='Select Branch')
    vendor = forms.ModelChoiceField(queryset=VendorCompany.objects.filter(status=True), empty_label='Select Vendor')    
    start_date = forms.DateField(widget=DateInput, required=True)
    end_date = forms.DateField(widget=DateInput, required=True)
    download_type = forms.ChoiceField(choices=DATA_TYPE, label="Select Data Source", required=True)    
    size = forms.IntegerField(initial=10000, required=False)    

    
    def __init__(self, *args, **kwargs):
        super(CustomExcelCsvForm, self).__init__(*args, **kwargs)

        self.fields['branch'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['vendor'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['download_type'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['size'].widget.attrs.update(
            {'class': 'form-control'})


class ExcelCsvForm(forms.Form):
    EXCEL = 'excel'
    CSV = 'csv'
    DATA_TYPE = (
        (EXCEL, _('Excel')),
        (CSV, _('CSV')),
    )
   
    download_type = forms.ChoiceField(choices=DATA_TYPE, label="Select Data Source", required=True)    
    start_date = forms.DateField(widget=DateInput, required=True)
    end_date = forms.DateField(widget=DateInput, required=True)
    size = forms.IntegerField(initial=10000, required=False)
    
    def __init__(self, *args, **kwargs):
        super(ExcelCsvForm, self).__init__(*args, **kwargs)

        self.fields['download_type'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['size'].widget.attrs.update(
            {'class': 'form-control'})


class AllBranchesForm(forms.Form):
    EXCEL = 'excel'
    CSV = 'csv'
    DATA_TYPE = (
        (EXCEL, _('Excel')),
        (CSV, _('CSV')),
    )
   
    download_type = forms.ChoiceField(choices=DATA_TYPE, label="Select Data Source", required=True)    
    start_date = forms.DateField(widget=DateInput, required=True)
    end_date = forms.DateField(widget=DateInput, required=True)
    
    def __init__(self, *args, **kwargs):
        super(AllBranchesForm, self).__init__(*args, **kwargs)

        self.fields['download_type'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update(
            {'class': 'form-control'})


class VendorCompareForm(forms.Form):
    vendorone = forms.ModelChoiceField(queryset=VendorCompany.objects.filter(status=True), empty_label='Select Vendor One')
    vendortwo = forms.ModelChoiceField(queryset=VendorCompany.objects.filter(status=True), empty_label='Select Vendor Two')
    start_date = forms.DateField(widget=DateInput, required=True)
    end_date = forms.DateField(widget=DateInput, required=True)
    
    def __init__(self, *args, **kwargs):
        super(VendorCompareForm, self).__init__(*args, **kwargs)

        self.fields['vendorone'].widget.attrs.update(
            {'class': 'form-control mb-2'})
        self.fields['vendortwo'].widget.attrs.update(
            {'class': 'form-control mb-2'})
        self.fields['start_date'].widget.attrs.update(
            {'class': 'form-control mb-2'})
        self.fields['end_date'].widget.attrs.update(
            {'class': 'form-control mb-2'})
