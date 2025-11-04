"""
DevOps CRM - Views Documentation

This document provides detailed information about the views and business logic
in the DevOps CRM system. The application follows Django's MVT (Model-View-Template)
pattern with a focus on dashboard-style interfaces and comprehensive activity tracking.

## View Categories

### 1. Dashboard Views
- **index()**: Simple health check endpoint
- **home()**: Main dashboard with activity summaries and recent reports
- **owner_dashboard()**: Owner-specific dashboard with offices and activity
- **office_dashboard()**: Office-specific dashboard with employees and reports
- **activity_dashboard()**: Comprehensive activity reporting with filtering

### 2. CRUD Views (Create, Read, Update, Delete)
- **owner_create()**: Create new property owners
- **owner_delete()**: Delete owners (with confirmation)
- **office_create()**: Create offices under specific owners
- **employee_create()**: Create employees within offices
- **employee_delete()**: Remove employees

### 3. Report Logging Views
- **log_call_from_employee()**: Log reports linked to specific employees
- **log_call_from_office()**: Log reports linked to office (no specific employee)
- **log_call_from_owner()**: Log reports linked to owner (flexible office selection)
- **report_dashboard()**: View individual report details

## Key Business Logic

### Multi-Tenant Data Isolation
All views implement proper data isolation by filtering based on `request.user`:
- Users only see owners they created
- Offices are filtered by user's owners
- Employees and reports follow the same ownership hierarchy

### Automatic Timestamp Updates
When reports are created, the system automatically updates:
- `owner.last_contacted` date
- `office.last_contacted` date (if office is linked)
- `report.created_at` timestamp (automatic)

### Activity Metrics Calculation
The dashboard views calculate various metrics:
- Report counts by time period (today, week, month, quarter, year)
- Field Visit (FOV) counts specifically tracked
- Average vibe ratings per office
- Activity matrix breakdowns by owner and communication type

### Dynamic Form Filtering
Report forms include intelligent filtering:
- Office choices limited to current user's owners
- Invalid office selections are ignored to prevent data leakage
- Forms adapt based on the creation context (employee, office, or owner level)

## URL Pattern Structure

### Dashboard URLs
- `/` - Main dashboard (home view)
- `/owner/{id}/` - Owner-specific dashboard
- `/office/{id}/` - Office-specific dashboard  
- `/activity/` - Activity reporting dashboard
- `/report/{id}/` - Individual report view

### Creation URLs
- `/owner/create/` - Create new owner
- `/owner/{id}/office/create/` - Create office under owner
- `/office/{id}/employee/create/` - Create employee in office

### Reporting URLs
- `/employee/{id}/log/` - Log report for specific employee
- `/office/{id}/log/` - Log report for office
- `/owner/{id}/log/` - Log report for owner

### Management URLs
- `/owner/{id}/delete/` - Delete owner (with confirmation)
- `/employee/{id}/delete/` - Delete employee

## Template Context Variables

### Common Context (Available in Most Views)
- `request.user`: Current authenticated user
- `current_date`: Today's date for time-based calculations

### Home Dashboard Context
- `owners`: QuerySet of user's owners
- `offices`: QuerySet of user's offices
- `reports`: 5 most recent reports
- `*_reports_count`: Report counts by time period
- `*_fovs`: FOV counts by time period

### Owner Dashboard Context
- `owner`: Specific owner instance
- `offices`: Offices belonging to this owner
- `reports`: 5 most recent reports for this owner
- `fovs`: Total FOV count for this owner

### Office Dashboard Context
- `office`: Specific office instance
- `employees`: Employees in this office
- `reports`: 5 most recent reports for this office
- `average_vibe`: Average vibe rating for office reports
- `fovs`: Total FOV count for this office

### Activity Dashboard Context
- `form`: DateRangeForm for filtering
- `show_table`: Boolean to control table display
- `owners`: User's owners list
- `calltype_list`: Available communication types
- `matrix`: Owner x CallType activity matrix
- `totals_by_calltype`: Column totals
- `totals_by_owner`: Row totals
- `grand_total`: Overall total
- `fov_reports`: Filtered FOV reports QuerySet

## Security Considerations

### Data Access Controls
1. **Owner Filtering**: All data access filtered by `Owner.objects.filter(user=request.user)`
2. **Cascading Security**: Offices, employees, and reports inherit security through relationships
3. **Form Validation**: Office selections validated against user ownership
4. **URL Parameter Validation**: get_object_or_404 ensures proper object access

### Authentication Requirements
- All views require user authentication (enforced at URL level)
- No anonymous access to any CRM functionality
- User context automatically available in all views

### Input Validation
- All forms use Django's built-in validation
- Model field constraints enforced (email validation, number ranges, etc.)
- CSRF protection enabled on all POST requests

## Performance Optimizations

### Database Query Efficiency  
- Use of select_related() and prefetch_related() for related objects
- Filtered querysets to reduce data transfer
- Aggregate queries for statistical calculations
- Limited result sets (recent reports sliced to 5 items)

### Caching Opportunities
- Dashboard statistics could be cached for high-traffic scenarios
- Owner/office lists rarely change and could benefit from caching
- Report counts by time period are good caching candidates

## Error Handling

### Standard Django Patterns
- Use of get_object_or_404() for safe object retrieval
- Form validation with error display in templates
- Redirect after successful POST operations (PRG pattern)

### User-Friendly Fallbacks
- Empty state handling in templates when no data exists
- Graceful degradation for missing relationships
- Default values for optional fields

## Integration Points

### External Systems
- Ready for email integration (email fields in models)
- Calendar integration potential (date fields for scheduling)
- Export functionality extensible (QuerySet structure supports CSV/PDF)

### API Development
- Views structured for easy API conversion
- Clear separation of data logic and presentation
- JSON-serializable context data

## Testing Considerations

### Unit Test Coverage
- Model validation and relationships
- Form validation and security
- View access controls and data filtering
- Business logic calculations (metrics, averages)

### Integration Test Scenarios  
- Complete user workflows (create owner → office → employee → report)
- Multi-tenant data isolation verification
- Permission and access control validation
- Form submission and redirect flows

This documentation provides the foundation for understanding, maintaining, and extending the DevOps CRM view layer.
"""