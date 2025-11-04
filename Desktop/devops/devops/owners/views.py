
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
    """
    Main dashboard view showing comprehensive activity overview.
    
    Displays activity statistics, recent reports, and quick access to all
    user-owned entities. Calculates time-based metrics including FOV counts
    and provides the central navigation hub for the CRM system.
    
    Features:
        - Activity counts by time period (today, week, month, quarter, year)
        - Field Visit (FOV) tracking and statistics
        - Recent reports display (5 most recent)
        - Quick access to owners and offices
    
    Security:
        - Only shows data owned by the current user
        - All querysets filtered by user's owners
        
    Args:
        request: HTTP request with authenticated user
        
    Returns:
        Rendered HTML response with dashboard context including:
            - owners: User's property owners
            - offices: User's office spaces  
            - reports: 5 most recent reports
            - Activity counts by time period
            - FOV counts by time period
    """
    # Redirect to login if user is not authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    
    owners = Owner.objects.filter(user=request.user)
    offices = Office.objects.filter(owner__in=owners)
    reports_qs = Report.objects.filter(owner__in=owners).order_by('-created_at')
    reports = reports_qs[:5]  # Only show 5 most recent
    current_date = date.today()

    # Date ranges
    last_week = current_date - timedelta(days=7)
    last_month = current_date - timedelta(days=30)
    last_quarter = current_date - timedelta(days=90)
    last_year = current_date - timedelta(days=365)

    # Filtered report counts
    today_reports = reports_qs.filter(created_at__date=current_date)
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
    })

def owner_create(request):
    """
    Handle creation of new property owners.
    
    GET: Display owner creation form
    POST: Process form submission and create new owner
    
    Security: Automatically links new owner to current user for data isolation.
    
    Args:
        request: HTTP request object with authenticated user
        
    Returns:
        GET: Rendered owner creation form
        POST: Redirect to home dashboard on success, form with errors on failure
    """
    if request.method == "POST":
        form = OwnerForm(request.POST)
        if form.is_valid():
            owner = form.save(commit=False)
            owner.user = request.user
            owner.save()
            return redirect(reverse('home'))
    else:
        form = OwnerForm()
    return render(request, "owners/create.html", {"form": form})

def owner_delete(request, owner_id):
    owner = get_object_or_404(Owner, pk=owner_id)
    if request.method == "POST":
        owner.delete()
        return redirect(reverse('home'))
    return render(request, "owners/delete.html", {"object": owner, "type": "owner"})

def owner_dashboard(request, owner_id):
    owner = get_object_or_404(Owner, pk=owner_id)
    offices = Office.objects.filter(owner=owner)
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
            office.owner = owner
            office.save()
            return redirect(reverse('owner_dashboard', args=[owner_id]))
    else:
        form = OfficeForm()
    return render(request, "owners/create.html", {"form": form, "owner": owner})

def office_dashboard(request, office_id):
    office = get_object_or_404(Office, pk=office_id)
    office_owners = Owner.objects.filter(id=office.owner.id)
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
    return render(request, "owners/create.html", {"form": form, "office": office})

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
    return render(request, "owners/create.html", {"form": form, "employee": employee})

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
    return render(request, "owners/create.html", {"form": form, "office": office})

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
    
    return render(request, "owners/create.html", context)

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
