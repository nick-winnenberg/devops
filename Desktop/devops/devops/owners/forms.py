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
from django.db import models
from .models import Owner, Office, Employee, Report
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from datetime import date


class OwnerForm(forms.ModelForm):
    """
    Enhanced form for creating and editing Owner instances with office association.
    
    Includes basic owner information and optional office selection to enable
    tying new owners to existing offices for multi-owner scenarios.
    
    Fields:
        - name: Owner/company name (required)
        - email: Contact email address (optional)
        - offices: Multiple office selection (optional)
        - set_as_primary: Whether to set as primary owner for selected offices
    """
    
    # Multi-select field for associating owner with existing offices
    offices = forms.ModelMultipleChoiceField(
        queryset=Office.objects.none(),  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select existing offices that this owner should be associated with"
    )
    
    # Option to set as primary owner for selected offices
    set_as_primary = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Check to set this owner as the primary contact for selected offices"
    )
    
    # Date field with current date default
    last_contacted = forms.DateField(
        required=False,
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text="Date of last contact with this owner (defaults to today)"
    )
    
    class Meta:
        model = Owner
        fields = ['name', 'email', 'last_contacted']
    
    def __init__(self, *args, **kwargs):
        # Accept user context to filter offices by the current user
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Show only offices owned by the current user (through primary_owner or legacy owner)
            user_offices = Office.objects.filter(
                models.Q(primary_owner__user=user) | 
                models.Q(owner__user=user)
            ).distinct()
            self.fields['offices'].queryset = user_offices
            
            # Update help text based on available offices
            office_count = user_offices.count()
            if office_count == 0:
                self.fields['offices'].help_text = f"No existing offices found for user '{user.username}'. Create offices first if you want to associate them with this owner."
                self.fields['set_as_primary'].widget = forms.HiddenInput()  # Hide if no offices
            else:
                self.fields['offices'].help_text = f"Select from your {office_count} existing office(s) to associate with this owner. (User: {user.username})"
        else:
            # No user context - hide office fields
            self.fields['offices'].widget = forms.HiddenInput()
            self.fields['set_as_primary'].widget = forms.HiddenInput()

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
    # Date field with current date default
    last_contacted = forms.DateField(
        required=False,
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text="Date of last contact with this office (defaults to today)"
    )
    
    class Meta:
        model = Office
        fields = ['name','number','address','city','state','zip_code','last_contacted']


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
    
    # Date field for when the call/communication actually happened
    call_date = forms.DateField(
        required=False,
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text="Date when this call or communication took place (defaults to today)",
        label="Call/Communication Date"
    )
    
    class Meta:
        model = Report
        # include office, additional_parties, and call_date fields
        fields = ['call_date', 'subject', 'transcript', 'content', 'vibe', 'calltype', 'office', 'additional_parties']
        widgets = {
            'created_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }

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
        Enhanced save method to incorporate additional parties and call date into report content.
        """
        report = super().save(commit=False)
        
        # Add call date information to content if provided
        call_date = self.cleaned_data.get('call_date')
        if call_date:
            # Add call date at the beginning of content
            date_header = f"CALL DATE: {call_date.strftime('%B %d, %Y')}\n" + "="*40 + "\n\n"
            report.content = date_header + report.content
        
        # Append additional parties information to content if provided
        additional = self.cleaned_data.get('additional_parties')
        if additional and additional.strip():
            # Add a clear separator and additional parties info
            separator = "\n\n" + "="*50 + "\nADDITIONAL PARTIES INVOLVED:\n" + "="*50 + "\n"
            report.content += separator + additional.strip()
            
        if commit:
            report.save()
        return report