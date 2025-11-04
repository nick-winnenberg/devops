"""
Django Forms for DevOps CRM System

This module defines forms for creating and editing CRM entities including
owners, offices, employees, and communication reports. All forms use
ModelForm for automatic field generation with custom validation and
field configuration where needed.

Forms included:
    - OwnerForm: Create/edit property owners
    - OfficeForm: Create/edit office spaces  
    - EmployeeForm: Create/edit employees
    - ReportForm: Create communication reports with dynamic office filtering
"""

from django import forms
from .models import Owner, Office, Employee, Report
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect


class OwnerForm(forms.ModelForm):
    """
    Form for creating and editing Owner instances.
    
    Includes basic owner information like name and email.
    The user field is automatically set in the view to ensure
    proper data ownership and multi-tenant isolation.
    
    Fields:
        - name: Owner/company name (required)
        - email: Contact email address (optional)
    """
    class Meta:
        model = Owner
        fields = ['name', 'email',]

class OfficeForm(forms.ModelForm):
    """
    Form for creating and editing Office instances.
    
    Includes all office location and identification details.
    The owner field is automatically set in the view based on
    the URL context to ensure proper relationships.
    
    Fields:
        - name: Office identifier/name (required)
        - number: Office number with 1-100 validation (required) 
        - address: Street address (required)
        - city: City name (required)
        - state: State/province (required)
        - zip_code: Postal/ZIP code (required)
    """
    class Meta:
        model = Office
        fields = ['name','number','address','city','state','zip_code']


class EmployeeForm(forms.ModelForm):
    """
    Form for creating and editing Employee instances.
    
    Includes employee personal and professional information.
    The office and owner fields are automatically set in the view
    based on URL context to maintain proper relationships.
    
    Fields:
        - name: Employee full name (required)
        - position: Job title/role (required)
        - email: Contact email address (optional)
        - potential: Business potential rating 1-10 (required, default 5)
    """
    class Meta:
        model = Employee
        fields = ['name','position','email','potential']


class ReportForm(forms.ModelForm):
    """
    Form for creating communication reports with enhanced owner-office clarity.
    
    This form includes special logic to limit office choices based on the
    owner context, ensuring users can only select offices they own.
    Enhanced with better labeling and help text for multi-owner scenarios.
    
    Features:
        - Dynamic office queryset filtering by owner
        - Clear owner-office relationship display
        - Optional additional parties field for complex scenarios
        - All report content and metadata fields included
    
    Fields:
        - subject: Optional subject line
        - transcript: Whether transcript is available (checkbox)
        - content: Main report content (required)
        - vibe: Interaction quality rating 1-10 (required, default 5)
        - calltype: Communication method (required, dropdown)
        - office: Optional office selection (filtered by owner with enhanced labels)
        - additional_parties: Optional field for noting other involved parties
    """
    
    # Add field for noting additional parties involved
    additional_parties = forms.CharField(
        max_length=500,
        required=False,
        help_text="Note any additional owners, partners, or parties involved in this communication",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., John Smith (Partner), Mary Johnson (Co-owner)',
            'class': 'form-control'
        }),
        label="Additional Parties Involved"
    )
    
    class Meta:
        model = Report
        # include office and new additional_parties field
        fields = ['subject', 'transcript', 'content', 'vibe', 'calltype', 'office', 'additional_parties']

    def __init__(self, *args, **kwargs):
        # accept an optional `owner` kwarg to limit office choices
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # office is optional on the model, so don't require it on the form
        self.fields['office'].required = False
        
        if owner is not None:
            # Filter offices and enhance labels to show owner relationship
            offices = Office.objects.filter(owner=owner)
            self.fields['office'].queryset = offices
            
            # Enhance office field label to show current owner context
            self.fields['office'].label = f"Select Office (Owner: {owner.name})"
            
            # Add helpful text about office selection
            if offices.count() > 1:
                self.fields['office'].help_text = f"Choose which of {owner.name}'s offices this communication relates to, or leave blank for general owner communication."
            elif offices.count() == 1:
                self.fields['office'].help_text = f"Optional: Select {offices.first().name} if this communication is office-specific."
            else:
                self.fields['office'].help_text = f"No offices found for {owner.name}. Create an office first if needed."
        else:
            # default to empty queryset to avoid exposing unrelated offices
            self.fields['office'].queryset = Office.objects.none()
            self.fields['office'].help_text = "Office selection will be available when creating reports from owner context."
    
    def save(self, commit=True):
        """
        Enhanced save method to incorporate additional parties into report content.
        """
        report = super().save(commit=False)
        
        # Append additional parties information to content if provided
        additional = self.cleaned_data.get('additional_parties')
        if additional and additional.strip():
            # Add a clear separator and additional parties info
            separator = "\n\n" + "="*50 + "\nADDITIONAL PARTIES INVOLVED:\n" + "="*50 + "\n"
            report.content += separator + additional.strip()
            
        if commit:
            report.save()
        return report