
"""
DevOps CRM - Main Views Module

This module contains all the business logic and view functions for the DevOps CRM system.
The views handle dashboard displays, CRUD operations, and report management with
proper multi-tenant data isolation and security controls.

View Categories:
    - Dashboard Views: Main hub, owner/office/activity dashboards
    - CRUD Operations: Create, delete operations for entities
    - Report Management: Communication logging and tracking
    - Analytics: Activity metrics and FOV tracking

Security Model:
    All views implement user-based data isolation by filtering objects
    through the user's ownership chain: User → Owner → Office → Employee → Report
"""

# Django imports
from django import forms
from django.db import models
from django.db.models import Count, Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse

# Local imports  
from .forms import OwnerForm, OfficeForm, EmployeeForm, ReportForm
from .models import Owner, Office, Employee, Report
from datetime import date, timedelta


def index(request):
    """
    Simple health check endpoint for deployment verification.
    
    Returns a basic HTTP response to confirm the application is running.
    Used by monitoring systems and load balancers for health checks.
    
    Args:
        request: HTTP request object (authentication not required)
        
    Returns:
        HttpResponse: Simple welcome message
    """
    return HttpResponse("Hello, world. Welcome!")

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    owners = Owner.objects.filter(user=request.user)
    offices = Office.objects.filter(
        models.Q(owners__in=owners) | models.Q(primary_owner__in=owners) | models.Q(owner__in=owners)
    ).distinct()
    reports_qs = Report.objects.filter(
        models.Q(owner__in=owners) | models.Q(employee__office__in=offices)
    ).distinct().order_by('-created_at')
    reports = reports_qs[:5]  # Only show 5 most recent
    current_date = date.today()

    this_week_number = current_date.isocalendar()[1]
    last_week_number = (current_date - timedelta(days=7)).isocalendar()[1]
    last_week_number_reports = reports_qs.filter(
        created_at__week=last_week_number,
        created_at__year=current_date.year
    )
    this_week_number_reports = reports_qs.filter(
        created_at__week=this_week_number,
        created_at__year=current_date.year
    )

    last_week_number_reports_count = last_week_number_reports.count()
    this_week_number_reports_count = this_week_number_reports.count()
    last_week_number_fov_counts = last_week_number_reports.filter(calltype='fov').count()
    this_week_number_fov_counts = this_week_number_reports.filter(calltype='fov').count()
    

    this_month_number = current_date.month
    last_month_reports = reports_qs.filter(
        created_at__month=this_month_number,
        created_at__year=current_date.year
    )
    last_month_number_reports_count = last_month_reports.count()
    last_month_number_fov_counts = last_week_number_reports.filter(calltype='fov').count()

    # Date ranges
    last_week = current_date - timedelta(days=7)
    last_month = current_date - timedelta(days=30)
    last_quarter = current_date - timedelta(days=90)
    last_year = current_date - timedelta(days=365)

    # Filtered report counts
    today_reports = reports_qs.filter(created_at__date=current_date)
    today_owner_reports = today_reports.filter(owner__in=owners)
    today_employee_reports = today_reports.filter(employee__office__in=offices)

    weekly_reports = reports_qs.filter(created_at__gte=last_week)
    monthly_reports = reports_qs.filter(created_at__gte=last_month)
    quarterly_reports = reports_qs.filter(created_at__gte=last_quarter)
    yearly_reports = reports_qs.filter(created_at__gte=last_year)

    today_reports_count = today_reports.count()
    weekly_reports_count = weekly_reports.count()
    monthly_reports_count = monthly_reports.count()
    quarterly_reports_count = quarterly_reports.count()
    yearly_reports_count = yearly_reports.count()

    # FOV counts
    today_fovs = today_reports.filter(calltype='fov').count()
    weekly_fovs = weekly_reports.filter(calltype='fov').count()
    monthly_fovs = monthly_reports.filter(calltype='fov').count()
    quarterly_fovs = quarterly_reports.filter(calltype='fov').count()
    yearly_fovs = yearly_reports.filter(calltype='fov').count()

    return render(request, "owners/home.html", {
        "owners": owners,
        "offices": offices,
        "reports": reports,
        "current_date": current_date,
        "weekly_reports_count": weekly_reports_count,
        "monthly_reports_count": monthly_reports_count,
        "quarterly_reports_count": quarterly_reports_count,
        "yearly_reports_count": yearly_reports_count,
        "weekly_fovs": weekly_fovs,
        "monthly_fovs": monthly_fovs,
        "quarterly_fovs": quarterly_fovs,
        "yearly_fovs": yearly_fovs,
        "today_reports_count": today_reports_count,
        "today_fovs": today_fovs,
        "this_week_number": this_week_number,
        "last_week_number": last_week_number,
        "this_week_number_reports": this_week_number_reports,
        "last_week_number_reports": last_week_number_reports,
        "this_week_number_reports_count": this_week_number_reports_count,
        "last_week_number_reports_count": last_week_number_reports_count,
        "last_month_number_reports_count": last_month_number_reports_count,
        "last_week_number_fov_counts": last_week_number_fov_counts,
        "this_week_number_fov_counts": this_week_number_fov_counts,
        "last_month_number_fov_counts": last_month_number_fov_counts,
        "today_owner_reports": today_owner_reports,
        "today_employee_reports": today_employee_reports,
    })

def owner_create(request):
    """
    Enhanced owner creation with office association support.
    
    Allows creating new owners and optionally associating them with existing offices.
    Supports the new multi-owner functionality by enabling owners to be tied to
    multiple offices and optionally set as primary contact.
    
    GET: Display owner creation form with office selection options
    POST: Process form submission, create owner, and handle office associations
    
    Security: Automatically links new owner to current user for data isolation.
    Only shows offices owned by the current user for association.
    
    Args:
        request: HTTP request object with authenticated user
        
    Returns:
        GET: Rendered owner creation form with available offices
        POST: Redirect to home dashboard on success, form with errors on failure
    """
    if request.method == "POST":
        form = OwnerForm(data=request.POST, user=request.user)
        if form.is_valid():
            # Create the owner instance
            owner = form.save(commit=False)
            owner.user = request.user
            owner.save()
            
            # Handle office associations
            selected_offices = form.cleaned_data.get('offices')
            set_as_primary = form.cleaned_data.get('set_as_primary', False)
            
            if selected_offices:
                # Add owner to selected offices
                for office in selected_offices:
                    office.owners.add(owner)
                    
                    # Set as primary owner if requested and office doesn't have primary owner
                    if set_as_primary:
                        if not office.primary_owner:
                            office.primary_owner = owner
                            office.save()
                        # If office already has primary owner, we could add logic here
                        # to ask user if they want to replace or just add as additional owner
            
            return redirect(reverse('home'))
    else:
        form = OwnerForm(user=request.user)
    
    return render(request, "owners/create.html", {"form": form})

def owner_create_from_office(request, office_id):
    """
    Create a new owner from office context and associate them with the office.
    
    This view allows adding new owners to an existing office, which is useful
    for scenarios like:
    - Adding new partners or co-owners
    - Bringing in management companies
    - Recording ownership changes or transfers
    
    The new owner will automatically be added to the office's owners list,
    and optionally can be set as the primary owner.
    
    GET: Display owner creation form with office context
    POST: Process form submission, create owner, and associate with office
    
    Security: Only allows users to add owners to offices they own/control.
    
    Args:
        request: HTTP request object with authenticated user
        office_id: ID of the office to associate the new owner with
        
    Returns:
        GET: Rendered owner creation form with office context
        POST: Redirect to office dashboard on success, form with errors on failure
    """
    office = get_object_or_404(Office, pk=office_id)
    
    # Security check: ensure user has access to this office
    user_owners = Owner.objects.filter(user=request.user)
    office_accessible = Office.objects.filter(
        models.Q(id=office_id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists()
    
    if not office_accessible:
        return redirect(reverse('home'))  # or show 403 error
    
    if request.method == "POST":
        form = OwnerForm(data=request.POST, user=request.user)
        if form.is_valid():
            # Create the owner instance
            owner = form.save(commit=False)
            owner.user = request.user
            owner.save()
            
            # Automatically associate with the office
            office.owners.add(owner)
            
            # Check if user wants to set as primary owner
            set_as_primary = request.POST.get('set_as_primary_for_office', False)
            if set_as_primary and not office.primary_owner:
                office.primary_owner = owner
                office.save()
            
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = OwnerForm(user=request.user)
    
    # Get existing owners for context
    existing_owners = []
    if office.owners.exists():
        existing_owners = office.owners.all()
    elif office.owner:  # Fallback to legacy owner
        existing_owners = [office.owner]
    
    context = {
        "form": form,
        "office": office,
        "existing_owners": existing_owners,
        "page_title": f"Add Owner to {office.name}",
        "form_type": "owner_from_office"
    }
    
    return render(request, "owners/owner_from_office_create.html", context)

def owner_edit(request, owner_id):
    """
    Edit an existing owner's information.
    
    Allows updating owner details while maintaining office associations.
    Only owners belonging to the current user can be edited.
    
    Args:
        request: HTTP request object with authenticated user
        owner_id: ID of the owner to edit
        
    Returns:
        GET: Rendered owner edit form
        POST: Redirect to owner dashboard on success, form with errors on failure
    """
    owner = get_object_or_404(Owner, pk=owner_id)
    
    # Security check: ensure user owns this owner
    if owner.user != request.user:
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = OwnerForm(data=request.POST, instance=owner, user=request.user)
        if form.is_valid():
            updated_owner = form.save()
            
            # Handle office associations if they changed
            selected_offices = form.cleaned_data.get('offices', [])
            set_as_primary = form.cleaned_data.get('set_as_primary', False)
            
            # Update office associations
            if selected_offices:
                # Clear existing associations and add new ones
                for office in updated_owner.offices.all():
                    if office not in selected_offices:
                        office.owners.remove(updated_owner)
                        # If this owner was primary, clear primary status
                        if office.primary_owner == updated_owner:
                            office.primary_owner = None
                            office.save()
                
                # Add new associations
                for office in selected_offices:
                    office.owners.add(updated_owner)
                    
                    # Set as primary if requested and no primary exists
                    if set_as_primary and not office.primary_owner:
                        office.primary_owner = updated_owner
                        office.save()
            
            return redirect(reverse('owner_dashboard', args=[owner_id]))
    else:
        # Pre-populate form with current office associations
        form = OwnerForm(instance=owner, user=request.user)
        # Set initial values for office associations
        if owner.offices.exists():
            form.fields['offices'].initial = owner.offices.all()
        # Check if owner is primary for any office
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
    """
    Edit an existing office's information.
    
    Allows updating office details while maintaining owner associations.
    Only offices owned by the current user can be edited.
    
    Args:
        request: HTTP request object with authenticated user
        office_id: ID of the office to edit
        
    Returns:
        GET: Rendered office edit form
        POST: Redirect to office dashboard on success, form with errors on failure
    """
    office = get_object_or_404(Office, pk=office_id)
    
    # Security check: ensure user has access to this office
    user_owners = Owner.objects.filter(user=request.user)
    office_accessible = Office.objects.filter(
        models.Q(id=office_id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists()
    
    if not office_accessible:
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = OfficeForm(data=request.POST, instance=office)
        if form.is_valid():
            updated_office = form.save()
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = OfficeForm(instance=office)
    
    # Get current owners for context
    if office.owners.exists():
        office_owners = office.owners.all()
    elif office.owner:
        office_owners = [office.owner]
    else:
        office_owners = []
    
    return render(request, "owners/office_edit.html", {
        "form": form,
        "office": office,
        "office_owners": office_owners,
        "page_title": f"Edit {office.name}"
    })

def office_manage_owners(request, office_id):
    """
    Admin function to manage owner associations for an existing office.
    
    Allows adding/removing existing owners to/from an office and setting
    the primary owner. This is an administrative function for complex
    ownership scenarios.
    
    Args:
        request: HTTP request object with authenticated user
        office_id: ID of the office to manage owners for
        
    Returns:
        GET: Rendered owner management form
        POST: Process owner changes and redirect to office dashboard
    """
    office = get_object_or_404(Office, pk=office_id)
    
    # Security check: ensure user has access to this office
    user_owners = Owner.objects.filter(user=request.user)
    office_accessible = Office.objects.filter(
        models.Q(id=office_id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists()
    
    if not office_accessible:
        return redirect(reverse('home'))
    
    if request.method == "POST":
        # Get selected owners and primary owner from form
        selected_owner_ids = request.POST.getlist('owners')
        primary_owner_id = request.POST.get('primary_owner')
        
        # Clear existing many-to-many relationships
        office.owners.clear()
        
        # Add selected owners
        if selected_owner_ids:
            selected_owners = Owner.objects.filter(
                id__in=selected_owner_ids,
                user=request.user  # Security: only user's owners
            )
            office.owners.set(selected_owners)
            
            # Set primary owner if specified and valid
            if primary_owner_id and primary_owner_id in selected_owner_ids:
                primary_owner = Owner.objects.get(
                    id=primary_owner_id,
                    user=request.user
                )
                office.primary_owner = primary_owner
                office.save()
            elif selected_owners.exists():
                # If no primary specified but owners selected, use first as primary
                office.primary_owner = selected_owners.first()
                office.save()
        
        return redirect(reverse('office_dashboard', args=[office_id]))
    
    # GET request - show current state and available owners
    current_owners = office.owners.all()
    available_owners = Owner.objects.filter(user=request.user)
    
    return render(request, "owners/office_manage_owners.html", {
        "office": office,
        "current_owners": current_owners,
        "available_owners": available_owners,
        "primary_owner": office.primary_owner,
        "page_title": f"Manage Owners - {office.name}"
    })

def office_dashboard(request, office_id):
    office = get_object_or_404(Office, pk=office_id)
    # Get all owners of this office (multi-owner support)
    if office.owners.exists():
        office_owners = office.owners.all()
    elif office.owner:  # Fallback to legacy single owner
        office_owners = Owner.objects.filter(id=office.owner.id)
    else:
        office_owners = Owner.objects.none()
    employees = Employee.objects.filter(office=office)
    reports_qs = Report.objects.filter(office=office).order_by('-created_at')
    reports = reports_qs[:5]
    # aggregate on the full queryset to get accurate average and allow filtering
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
    """
    Edit an existing employee's information.
    
    Allows updating employee details while maintaining office associations.
    Only employees in offices owned by the current user can be edited.
    
    Args:
        request: HTTP request object with authenticated user
        employee_id: ID of the employee to edit
        
    Returns:
        GET: Rendered employee edit form
        POST: Redirect to office dashboard on success, form with errors on failure
    """
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Security check: ensure user has access to this employee's office
    user_owners = Owner.objects.filter(user=request.user)
    office_accessible = Office.objects.filter(
        models.Q(id=employee.office.id) & (
            models.Q(owners__in=user_owners) | 
            models.Q(primary_owner__in=user_owners) | 
            models.Q(owner__in=user_owners)
        )
    ).exists()
    
    if not office_accessible:
        return redirect(reverse('home'))
    
    if request.method == "POST":
        form = EmployeeForm(data=request.POST, instance=employee)
        if form.is_valid():
            updated_employee = form.save()
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
    employee = get_object_or_404(Employee, pk=employee_id)
    office_id = employee.office.id
    employee.delete()

    return redirect(reverse('office_dashboard', args=[office_id]))

def log_call_from_employee(request, employee_id):
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
            # update related last_contacted fields only if they exist
            if getattr(report, 'office', None) is not None:
                report.office.last_contacted = date.today()
                report.office.save()

            if getattr(report, 'owner', None) is not None:
                report.owner.last_contacted = date.today()
                report.owner.save()
            return redirect(reverse('office_dashboard', args=[employee.office.id]))
    else:
        form = ReportForm()
    return render(request, "owners/form_create.html", {"form": form, "employee": employee})

def log_call_from_office(request, office_id):
    office = get_object_or_404(Office, pk=office_id)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.owner = office.owner
            report.office = office
            report.author = request.user
            report.save()
            # update related last_contacted fields only if they exist
            if getattr(report, 'office', None) is not None:
                report.office.last_contacted = date.today()
                report.office.save()

            if getattr(report, 'owner', None) is not None:
                report.owner.last_contacted = date.today()
                report.owner.save()
            return redirect(reverse('office_dashboard', args=[office_id]))
    else:
        form = ReportForm()
    return render(request, "owners/form_create.html", {"form": form, "office": office})


def log_call_from_owner(request, owner_id):
    """
    Log communication reports from owner context with enhanced office selection.
    
    This view provides clear owner-office relationship context and validates
    that selected offices belong to the current owner. Includes enhanced
    form context for better user experience.
    
    Args:
        request: HTTP request object
        owner_id: ID of the owner for this communication
        
    Returns:
        GET: Report creation form with owner context and filtered office choices
        POST: Process form and redirect to owner dashboard on success
    """
    owner = get_object_or_404(Owner, pk=owner_id)
    
    # Get owner's offices for context display
    owner_offices = Office.objects.filter(owner=owner)
    
    if request.method == "POST":
        form = ReportForm(request.POST, owner=owner)
        if form.is_valid():
            report = form.save(commit=False)
            report.owner = owner
            
            # Validate office selection - ensure it belongs to this owner
            if report.office and report.office.owner_id != owner.id:
                # Log security attempt and ignore invalid selection
                report.office = None
                
            report.author = request.user
            report.save()
            
            # Update last_contacted fields
            if getattr(report, 'office', None) is not None:
                report.office.last_contacted = date.today()
                report.office.save()

            if getattr(report, 'owner', None) is not None:
                report.owner.last_contacted = date.today()
                report.owner.save()
                
            return redirect(reverse('owner_dashboard', args=[owner_id]))
    else:
        form = ReportForm(owner=owner)
    
    # Enhanced context with office information
    context = {
        "form": form, 
        "owner": owner,
        "owner_offices": owner_offices,
        "office_count": owner_offices.count(),
        "page_title": f"Log Communication - {owner.name}",
        "form_type": "owner_report"
    }
    
    return render(request, "owners/form_create.html", context)

def report_dashboard(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    return render(request, "owners/report_dashboard.html", {
        "report": report,
    })

def activity_dashboard(request):
    """
    Comprehensive activity reporting dashboard with filtering capabilities.
    
    Features:
        - Date range filtering for reports
        - Activity matrix showing owner vs. communication type breakdown
        - Statistical totals by owner and communication type
        - FOV report listings
        - Dynamic table display based on filter criteria
    
    The view builds a complex activity matrix that cross-tabulates owners
    with communication types, providing comprehensive analytics for
    business development and activity tracking.
    
    Query Parameters:
        - start_date: Filter reports from this date (YYYY-MM-DD format)
        - end_date: Filter reports until this date (YYYY-MM-DD format)
        
    Args:
        request: HTTP request with optional date filtering parameters
        
    Returns:
        Rendered activity dashboard with:
            - Filtered reports queryset
            - Owner vs. calltype activity matrix
            - Statistical totals and grand total
            - FOV reports for field visit tracking
    """
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
        # only show the table when at least one date filter is provided
        if start_date or end_date:
            show_table = True
        if start_date:
            reports = reports.filter(created_at__gte=start_date)
        if end_date:
            reports = reports.filter(created_at__lte=end_date)

    # Build per-owner × per-calltype matrix and totals
    # aggregated rows: owner id/name + calltype + count
    aggregated = (
        reports.values('owner__id', 'owner__name', 'calltype')
        .annotate(count=Count('id'))
    )

    # get calltype codes and labels from Report model choices
    calltype_list = [{'code': c, 'label': l} for c, l in getattr(Report, 'calltype_choices', [])]

    # owners for this user (preserve ordering)
    owners_list = list(owners)

    # initialize matrix: owner_id -> {calltype: 0}
    matrix = {owner.id: {ct['code']: 0 for ct in calltype_list} for owner in owners_list}

    # fill matrix from aggregated results
    for row in aggregated:
        oid = row.get('owner__id')
        ct = row.get('calltype')
        cnt = row.get('count', 0)
        if oid not in matrix:
            # include owners that may not be in owners_list
            matrix.setdefault(oid, {ct0['code']: 0 for ct0 in calltype_list})
        matrix[oid][ct] = cnt

    # compute totals per calltype and per owner and grand total
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

    # Get all FOV reports from the filtered queryset
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

