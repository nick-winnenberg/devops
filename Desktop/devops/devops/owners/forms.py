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
    Form for creating communication reports with dynamic office filtering.
    
    This form includes special logic to limit office choices based on the
    owner context, ensuring users can only select offices they own.
    The employee, owner, and author fields are set automatically in views.
    
    Features:
        - Dynamic office queryset filtering by owner
        - Optional office selection for flexible report relationships
        - All report content and metadata fields included
    
    Fields:
        - subject: Optional subject line
        - transcript: Whether transcript is available (checkbox)
        - content: Main report content (required)
        - vibe: Interaction quality rating 1-10 (required, default 5)
        - calltype: Communication method (required, dropdown)
        - office: Optional office selection (filtered by owner)
    """
    class Meta:
        model = Report
        # include office so owners can choose one of their offices when creating a report
        fields = ['subject','transcript','content','vibe','calltype', 'office']

    def __init__(self, *args, **kwargs):
        # accept an optional `owner` kwarg to limit office choices
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        # office is optional on the model, so don't require it on the form
        self.fields['office'].required = False
        if owner is not None:
            self.fields['office'].queryset = Office.objects.filter(owner=owner)
        else:
            # default to empty queryset to avoid exposing unrelated offices
            self.fields['office'].queryset = Office.objects.none()