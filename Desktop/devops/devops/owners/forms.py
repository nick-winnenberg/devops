from django import forms
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['name', 'email',]

class OfficeForm(forms.ModelForm):
    class Meta:
        model = Office
        fields = ['name','number','address','city','state','zip_code']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name','position','email','potential']

class ReportForm(forms.ModelForm):
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