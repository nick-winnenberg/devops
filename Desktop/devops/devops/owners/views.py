"""
DevOps CRM Views Module

Handles all business logic for the CRM system with multi-owner support.
Security: All views filter data by authenticated user ownership.
"""

from django import forms
from django.db import models
from django.db.models import Count, Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from datetime import date, timedelta

from .forms import OwnerForm, OfficeForm, EmployeeForm, ReportForm
from .models import Owner, Office, Employee, Report


def index(request):
    """Health check endpoint."""
    return HttpResponse("Hello, world. Welcome!")

def home(request):
    """Main dashboard showing activity statistics and entity lists."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user's data
    owners = Owner.objects.filter(user=request.user)
    offices = Office.objects.filter(
        models.Q(owners__in=owners) | models.Q(primary_owner__in=owners) | models.Q(owner__in=owners)
    ).distinct()
    reports_qs = Report.objects.filter(
        models.Q(owner__in=owners) | models.Q(office__in=offices)
    ).distinct().order_by('-created_at')
    
    current_date = date.today()
    current_year = current_date.year
    this_week = current_date.isocalendar()[1]
    last_week = (current_date - timedelta(days=7)).isocalendar()[1]
    this_month = current_date.month
    
    # Calculate last month (handles year boundary)
    if this_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = this_month - 1
        last_month_year = current_year

    # Filter reports by time periods
    today_reports = reports_qs.filter(created_at__date=current_date)
    this_week_reports = reports_qs.filter(created_at__week=this_week, created_at__year=current_year)
    last_week_reports = reports_qs.filter(created_at__week=last_week, created_at__year=current_year)
    this_month_reports = reports_qs.filter(created_at__month=this_month, created_at__year=current_year)
    last_month_reports = reports_qs.filter(created_at__month=last_month, created_at__year=last_month_year)

    # Calculate counts for each period
    def get_report_stats(period_reports):
        """Helper to calculate report statistics for a time period."""
        return {
            'total': period_reports.count(),
            'fovs': period_reports.filter(calltype='fov').count(),
            'owner': period_reports.filter(owner__in=owners).count(),
            'employee': period_reports.filter(employee__office__in=offices).count(),
        }

    today = get_report_stats(today_reports)
    this_week_stats = get_report_stats(this_week_reports)
    last_week_stats = get_report_stats(last_week_reports)
    this_month_stats = get_report_stats(this_month_reports)
    last_month_stats = get_report_stats(last_month_reports)

    return render(request, "owners/home.html", {
        "owners": owners,
        "offices": offices,
        "current_date": current_date,
        # Today stats
        "today_reports_count": today['total'],
        "today_fovs": today['fovs'],
        "today_owner_reports_count": today['owner'],
        "today_employee_reports_count": today['employee'],
        # This week stats
        "this_week_number_reports_count": this_week_stats['total'],
        "this_week_number_fov_counts": this_week_stats['fovs'],
        "this_week_owner_reports_count": this_week_stats['owner'],
        "this_week_employee_reports_count": this_week_stats['employee'],
        # Last week stats
        "last_week_number_reports_count": last_week_stats['total'],
        "last_week_number_fov_counts": last_week_stats['fovs'],
        "last_week_owner_reports_count": last_week_stats['owner'],
        "last_week_employee_reports_count": last_week_stats['employee'],
        # This month stats
        "this_month_number_reports_count": this_month_stats['total'],
        "this_month_number_fov_counts": this_month_stats['fovs'],
        "this_month_owner_reports_count": this_month_stats['owner'],
        "this_month_employee_reports_count": this_month_stats['employee'],
        # Last month stats
        "last_month_number_reports_count": last_month_stats['total'],
        "last_month_number_fov_counts": last_month_stats['fovs'],
        "last_month_owner_reports_count": last_month_stats['owner'],
        "last_month_employee_reports_count": last_month_stats['employee'],
    })

def owner_create(request):
    """Create new owner with optional office associations."""
    if request.method == "POST":
        form = OwnerForm(data=request.POST, user=request.user)
        if form.is_valid():
            owner = form.save(commit=False)
            owner.user = request.user
            owner.save()
            
            # Handle office associations
            selected_offices = form.cleaned_data.get('offices')
            set_as_primary = form.cleaned_data.get('set_as_primary', False)
            
            if selected_offices:
                for office in selected_offices:
                    office.owners.add(owner)
                    if set_as_primary and not office.primary_owner:
                        office.primary_owner = owner
                        office.save()
            
            return redirect(reverse('home'))
    else:
        form = OwnerForm(user=request.user)
    
    return render(request, "owners/create.html", {"form": form})

def owner_create_from_office(request, office_id):
    """Create new owner and associate with specified office."""
    office = get_object_or_404(Office, pk=office_id)
    
    # Security check
    user_owners = Owner.objects.filter(user=request.user)
    if not Office.objects.filter(
        models.Q(id=office_id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists():
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = OwnerForm(data=request.POST, user=request.user)
        if form.is_valid():
            owner = form.save(commit=False)
            owner.user = request.user
            owner.save()
            
            office.owners.add(owner)
            
            if request.POST.get('set_as_primary_for_office') and not office.primary_owner:
                office.primary_owner = owner
                office.save()
            
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = OwnerForm(user=request.user)
    
    existing_owners = list(office.owners.all()) if office.owners.exists() else ([office.owner] if office.owner else [])
    
    return render(request, "owners/owner_from_office_create.html", {
        "form": form,
        "office": office,
        "existing_owners": existing_owners,
        "page_title": f"Add Owner to {office.name}",
        "form_type": "owner_from_office"
    })

def owner_edit(request, owner_id):
    """Edit owner information and office associations."""
    owner = get_object_or_404(Owner, pk=owner_id)
    
    if owner.user != request.user:
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = OwnerForm(data=request.POST, instance=owner, user=request.user)
        if form.is_valid():
            updated_owner = form.save()
            selected_offices = form.cleaned_data.get('offices', [])
            set_as_primary = form.cleaned_data.get('set_as_primary', False)
            
            if selected_offices:
                # Remove from unselected offices
                for office in updated_owner.offices.all():
                    if office not in selected_offices:
                        office.owners.remove(updated_owner)
                        if office.primary_owner == updated_owner:
                            office.primary_owner = None
                            office.save()
                
                # Add to selected offices
                for office in selected_offices:
                    office.owners.add(updated_owner)
                    if set_as_primary and not office.primary_owner:
                        office.primary_owner = updated_owner
                        office.save()
            
            return redirect(reverse('owner_dashboard', args=[owner_id]))
    else:
        form = OwnerForm(instance=owner, user=request.user)
        if owner.offices.exists():
            form.fields['offices'].initial = owner.offices.all()
        if owner.primary_offices.exists():
            form.fields['set_as_primary'].initial = True
    
    return render(request, "owners/owner_edit.html", {
        "form": form, 
        "owner": owner,
        "page_title": f"Edit {owner.name}"
    })

def owner_delete(request, owner_id):
    owner = get_object_or_404(Owner, pk=owner_id)
    if request.method == "POST":
        owner.delete()
        return redirect(reverse('home'))
    return render(request, "owners/delete.html", {"object": owner, "type": "owner"})

def office_delete(request, office_id):
    office = get_object_or_404(Office, pk=office_id)
    if request.method == "POST":
        office.delete()
        return redirect(reverse('home'))
    return render(request, "owners/delete.html", {"object": office, "type": "office"})

def owner_dashboard(request, owner_id):
    owner = get_object_or_404(Owner, pk=owner_id)
    # Updated to use multi-owner relationships - show offices where this owner is involved
    offices = Office.objects.filter(
        models.Q(owners=owner) | models.Q(primary_owner=owner) | models.Q(owner=owner)
    ).distinct()
    reports_qs = Report.objects.filter(owner=owner).order_by('-created_at')
    reports = reports_qs[:5]

    # compute fov count from the full queryset (not the sliced one)
    fovs = reports_qs.filter(calltype='fov').count()



    return render(request, "owners/owner_dashboard.html", {
        "owner": owner,
        "offices": offices,
        "reports": reports,
        "fovs": fovs,
    })

def office_create(request, owner_id):
    owner = get_object_or_404(Owner, pk=owner_id)
    if request.method == "POST":
        form = OfficeForm(request.POST)
        if form.is_valid():
            office = form.save(commit=False)
            # Set both legacy and new owner fields for compatibility
            office.owner = owner  # Legacy field
            office.primary_owner = owner  # New primary owner field
            office.save()
            # Add to many-to-many relationship
            office.owners.add(owner)
            return redirect(reverse('owner_dashboard', args=[owner_id]))
    else:
        form = OfficeForm()
    return render(request, "owners/form_create.html", {"form": form, "owner": owner})

def office_edit(request, office_id):
    """Edit office information."""
    office = get_object_or_404(Office, pk=office_id)
    
    # Security check
    user_owners = Owner.objects.filter(user=request.user)
    if not Office.objects.filter(
        models.Q(id=office_id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists():
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = OfficeForm(data=request.POST, instance=office)
        if form.is_valid():
            form.save()
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = OfficeForm(instance=office)
    
    office_owners = list(office.owners.all()) if office.owners.exists() else ([office.owner] if office.owner else [])
    
    return render(request, "owners/office_edit.html", {
        "form": form,
        "office": office,
        "office_owners": office_owners,
        "page_title": f"Edit {office.name}"
    })

def office_manage_owners(request, office_id):
    """Admin function to manage office owner associations."""
    office = get_object_or_404(Office, pk=office_id)
    
    # Security check
    user_owners = Owner.objects.filter(user=request.user)
    if not Office.objects.filter(
        models.Q(id=office_id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists():
        return redirect(reverse('home'))
    
    if request.method == "POST":
        selected_owner_ids = request.POST.getlist('owners')
        primary_owner_id = request.POST.get('primary_owner')
        
        office.owners.clear()
        
        if selected_owner_ids:
            selected_owners = Owner.objects.filter(id__in=selected_owner_ids, user=request.user)
            office.owners.set(selected_owners)
            
            if primary_owner_id and primary_owner_id in selected_owner_ids:
                office.primary_owner = Owner.objects.get(id=primary_owner_id, user=request.user)
            elif selected_owners.exists():
                office.primary_owner = selected_owners.first()
            office.save()
        
        return redirect(reverse('office_dashboard', args=[office_id]))
    
    return render(request, "owners/office_manage_owners.html", {
        "office": office,
        "current_owners": office.owners.all(),
        "available_owners": Owner.objects.filter(user=request.user),
        "primary_owner": office.primary_owner,
        "page_title": f"Manage Owners - {office.name}"
    })

def office_dashboard(request, office_id):
    """Display dashboard for a specific office."""
    office = get_object_or_404(Office, pk=office_id)
    
    # Get office owners
    if office.owners.exists():
        office_owners = office.owners.all()
    elif office.owner:
        office_owners = Owner.objects.filter(id=office.owner.id)
    else:
        office_owners = Owner.objects.none()
    
    employees = Employee.objects.filter(office=office)
    reports_qs = Report.objects.filter(office=office).order_by('-created_at')
    reports = reports_qs[:5]
    average_vibe = reports_qs.aggregate(Avg('vibe'))['vibe__avg'] if reports_qs.exists() else None
    fovs = reports_qs.filter(calltype='fov').count()

    return render(request, "owners/office_dashboard.html", {
        "office": office,
        "employees": employees,
        "reports": reports,
        "average_vibe": average_vibe,
        "office_owners": office_owners,
        "fovs": fovs,
    })

def employee_create(request, office_id):
    """Create a new employee for an office."""
    office = get_object_or_404(Office, pk=office_id)
    
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.office = office
            employee.owner = office.owner
            employee.save()
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = EmployeeForm()
    
    return render(request, "owners/form_create.html", {"form": form, "office": office, "employee": True})

def employee_edit(request, employee_id):
    """Edit employee information."""
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Security check
    user_owners = Owner.objects.filter(user=request.user)
    if not Office.objects.filter(
        models.Q(id=employee.office.id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists():
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = EmployeeForm(data=request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect(reverse('office_dashboard', args=[employee.office.id]))
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, "owners/employee_edit.html", {
        "form": form,
        "employee": employee,
        "office": employee.office,
        "page_title": f"Edit {employee.name}"
    })

def employee_delete(request, employee_id):
    """Delete an employee."""
    employee = get_object_or_404(Employee, pk=employee_id)
    office_id = employee.office.id
    employee.delete()
    return redirect(reverse('office_dashboard', args=[office_id]))

def log_call_from_employee(request, employee_id):
    """Log a call report from employee page."""
    employee = get_object_or_404(Employee, pk=employee_id)
    
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.employee = employee
            report.owner = employee.owner
            report.office = employee.office
            report.author = request.user
            report.save()
            
            # Update last_contacted fields
            if report.office:
                report.office.last_contacted = date.today()
                report.office.save()
            if report.owner:
                report.owner.last_contacted = date.today()
                report.owner.save()
            
            return redirect(reverse('office_dashboard', args=[employee.office.id]))
    else:
        form = ReportForm()
    
    return render(request, "owners/form_create.html", {"form": form, "employee": employee})

def log_call_from_office(request, office_id):
    """Log a call report from office page."""
    office = get_object_or_404(Office, pk=office_id)
    
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.owner = office.owner
            report.office = office
            report.author = request.user
            report.save()
            
            # Update last_contacted fields
            if report.office:
                report.office.last_contacted = date.today()
                report.office.save()
            if report.owner:
                report.owner.last_contacted = date.today()
                report.owner.save()
            
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = ReportForm()
    
    return render(request, "owners/form_create.html", {"form": form, "office": office})


def log_call_from_owner(request, owner_id):
    """Log a call report from owner page."""
    owner = get_object_or_404(Owner, pk=owner_id)
    owner_offices = Office.objects.filter(owner=owner)
    
    if request.method == "POST":
        form = ReportForm(request.POST, owner=owner)
        if form.is_valid():
            report = form.save(commit=False)
            report.owner = owner
            
            # Validate office belongs to owner
            if report.office and report.office.owner_id != owner.id:
                report.office = None
            
            report.author = request.user
            report.save()
            
            # Update last_contacted fields
            if report.office:
                report.office.last_contacted = date.today()
                report.office.save()
            if report.owner:
                report.owner.last_contacted = date.today()
                report.owner.save()
            
            return redirect(reverse('owner_dashboard', args=[owner_id]))
    else:
        form = ReportForm(owner=owner)
    
    return render(request, "owners/form_create.html", {
        "form": form, 
        "owner": owner,
        "owner_offices": owner_offices,
        "office_count": owner_offices.count(),
        "page_title": f"Log Communication - {owner.name}",
        "form_type": "owner_report"
    })

def report_dashboard(request, report_id):
    """Display individual report details."""
    report = get_object_or_404(Report, pk=report_id)
    return render(request, "owners/report_dashboard.html", {"report": report})

def activity_dashboard(request):
    """Activity reporting dashboard with date range filtering and owner vs calltype matrix."""
    user = request.user
    reports = Report.objects.filter(author=user)
    owners = Owner.objects.filter(user=user)

    class DateRangeForm(forms.Form):
        start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
        end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    form = DateRangeForm(request.GET if request.GET else None)
    show_table = False
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if start_date or end_date:
            show_table = True
        if start_date:
            reports = reports.filter(created_at__gte=start_date)
        if end_date:
            reports = reports.filter(created_at__lte=end_date)

    # Build owner × calltype matrix
    aggregated = reports.values('owner__id', 'owner__name', 'calltype').annotate(count=Count('id'))
    calltype_list = [{'code': c, 'label': l} for c, l in getattr(Report, 'calltype_choices', [])]
    owners_list = list(owners)
    
    # Initialize matrix
    matrix = {owner.id: {ct['code']: 0 for ct in calltype_list} for owner in owners_list}
    
    # Fill matrix from aggregated results
    for row in aggregated:
        oid = row.get('owner__id')
        ct = row.get('calltype')
        cnt = row.get('count', 0)
        if oid not in matrix:
            matrix.setdefault(oid, {ct0['code']: 0 for ct0 in calltype_list})
        matrix[oid][ct] = cnt

    # Compute totals
    totals_by_calltype = {ct['code']: 0 for ct in calltype_list}
    totals_by_owner = {}
    grand_total = 0
    
    for owner in owners_list:
        oid = owner.id
        row_total = sum(matrix.get(oid, {}).values())
        totals_by_owner[oid] = row_total
        grand_total += row_total
        for ct in calltype_list:
            totals_by_calltype[ct['code']] += matrix.get(oid, {}).get(ct['code'], 0)

    fov_reports = reports.filter(calltype='fov')

    return render(request, "owners/activity_dashboard.html", {
        "reports": reports,
        "form": form,
        "show_table": show_table,
        "owners": owners_list,
        "calltype_list": calltype_list,
        "matrix": matrix,
        "totals_by_calltype": totals_by_calltype,
        "totals_by_owner": totals_by_owner,
        "grand_total": grand_total,
        "fov_reports": fov_reports,
    })

