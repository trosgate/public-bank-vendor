from .models import InventoryRequest
from django.utils.translation import gettext_lazy as _
from django import forms
from general_settings.models import Inventory


class InventoryForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Inventory.objects.all(), empty_label='Select Category')

    class Meta:
        model = InventoryRequest
        fields = [
            'category', 'line_one', 'line_one_order',
            'line_two', 'line_two_order',
            'line_three', 'line_three_order',
            'line_four', 'line_four_order', 
            'request_message', 
        ] 

        required = ['category', 'line_one', 'line_one_order']  

    def __init__(self, *args, **kwargs):
        super(InventoryForm, self).__init__(*args, **kwargs) 

        # 'Basic Info'
        self.fields['category'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})            
        # 'Product/Service #1',                    
        self.fields['line_one'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['line_one_order'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 0})
        # 'Product/Service #2',        
        self.fields['line_two'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})            
        self.fields['line_two_order'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 0})        
        # 'Product/Service #3',                    
        self.fields['line_three'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['line_three_order'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 0})
        # 'Product/Service #4',                    
        self.fields['line_four'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
        self.fields['line_four_order'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 0})    
        self.fields['request_message'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Explanatory note to justify the quantity'}) 

        for field in self.Meta.required:
            self.fields[field].required = True


class InventoryReviewForm(forms.ModelForm):
    class Meta:
        model = InventoryRequest
        fields = ['line_one_issue', 'line_two_issue', 'line_three_issue','line_four_issue', 'issue_remark'] 
         
    def __init__(self, *args, **kwargs):
        super(InventoryReviewForm, self).__init__(*args, **kwargs) 

        self.fields['line_one_issue'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})

        self.fields['line_two_issue'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 0})
                     
        self.fields['line_three_issue'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})

        self.fields['line_four_issue'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': ''})
                      
        self.fields['issue_remark'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Explanatory note to justify your acceptance/rejection'}) 
 

class InventoryConfirmForm(forms.ModelForm):
    class Meta:
        model = InventoryRequest
        fields = ['condition'] 
         
    def __init__(self, *args, **kwargs):
        super(InventoryConfirmForm, self).__init__(*args, **kwargs) 

        self.fields['condition'].widget.attrs.update(
            {'class': 'form-control col-6', 'placeholder': ''})
