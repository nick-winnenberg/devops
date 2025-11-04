"""
DevOps CRM - Application Programming Interface (API) Documentation

This document outlines the current web interface endpoints and provides
a foundation for future REST API development.

## Current Web Interface Endpoints

### Authentication Required
All endpoints require user authentication. Unauthenticated requests are
redirected to the login page.

### Response Formats
Current endpoints return HTML responses rendered through Django templates.
All forms use POST method with CSRF protection enabled.

## Endpoint Reference

### Dashboard Endpoints

#### GET /
**Main Dashboard**
- Returns: HTML dashboard with activity overview
- Context: User's owners, offices, recent reports, activity metrics
- Purpose: Central hub for CRM activity monitoring

#### GET /owner/{owner_id}/
**Owner Dashboard** 
- Parameters: owner_id (integer) - Must belong to current user
- Returns: HTML dashboard for specific owner
- Context: Owner details, associated offices, recent reports, FOV count
- Error: 404 if owner not found or doesn't belong to user

#### GET /office/{office_id}/
**Office Dashboard**
- Parameters: office_id (integer) - Must belong to user's owner
- Returns: HTML dashboard for specific office  
- Context: Office details, employees, recent reports, average vibe, FOV count
- Error: 404 if office not found or user lacks access

#### GET /report/{report_id}/  
**Report Details**
- Parameters: report_id (integer) - Must belong to user's data
- Returns: HTML view of individual report
- Context: Full report details and metadata
- Error: 404 if report not found or user lacks access

#### GET /activity/
**Activity Dashboard**
- Query Parameters: 
  - start_date (YYYY-MM-DD, optional)
  - end_date (YYYY-MM-DD, optional) 
- Returns: HTML activity matrix and filtered reports
- Context: Activity breakdown by owner/calltype, date filtering
- Purpose: Comprehensive reporting and analytics

### Creation Endpoints

#### GET/POST /owner/create/
**Create Owner**
- GET: Returns owner creation form
- POST: Creates new owner linked to current user
  - Body: name (required), email (optional)
  - Redirect: Home dashboard on success
  - Error: Form validation errors displayed

#### GET/POST /owner/{owner_id}/office/create/  
**Create Office**
- Parameters: owner_id (integer) - Must belong to current user
- GET: Returns office creation form
- POST: Creates new office under specified owner
  - Body: name, number (1-100), address, city, state, zip_code (all required)
  - Redirect: Owner dashboard on success
  - Error: Form validation errors or 404 if owner not accessible

#### GET/POST /office/{office_id}/employee/create/
**Create Employee**
- Parameters: office_id (integer) - Must belong to user's owner
- GET: Returns employee creation form  
- POST: Creates new employee in specified office
  - Body: name, position (required), email (optional), potential (1-10, default 5)
  - Redirect: Office dashboard on success
  - Error: Form validation errors or 404 if office not accessible

### Report Logging Endpoints

#### GET/POST /employee/{employee_id}/log/
**Log Report for Employee**
- Parameters: employee_id (integer) - Must belong to user's data
- GET: Returns report creation form
- POST: Creates report linked to employee, office, and owner
  - Body: subject (optional), transcript (boolean), content (required), vibe (1-10), calltype (choice)
  - Side Effect: Updates last_contacted dates for owner and office
  - Redirect: Office dashboard on success

#### GET/POST /office/{office_id}/log/
**Log Report for Office** 
- Parameters: office_id (integer) - Must belong to user's owner
- GET: Returns report creation form
- POST: Creates report linked to office and owner (no specific employee)
  - Body: Same as employee report
  - Side Effect: Updates last_contacted dates for owner and office
  - Redirect: Office dashboard on success

#### GET/POST /owner/{owner_id}/log/
**Log Report for Owner**
- Parameters: owner_id (integer) - Must belong to current user  
- GET: Returns report creation form with office dropdown
- POST: Creates report linked to owner (optional office selection)
  - Body: Same as employee report + office (optional, validated against owner)
  - Side Effect: Updates last_contacted dates for owner and office (if selected)
  - Redirect: Owner dashboard on success

### Management Endpoints

#### GET/POST /owner/{owner_id}/delete/
**Delete Owner**
- Parameters: owner_id (integer) - Must belong to current user
- GET: Returns deletion confirmation page
- POST: Deletes owner and all associated data (CASCADE)
  - Redirect: Home dashboard on success
  - Warning: Irreversible operation, deletes offices, employees, and reports

#### POST /employee/{employee_id}/delete/
**Delete Employee**
- Parameters: employee_id (integer) - Must belong to user's data
- POST: Deletes employee immediately (no confirmation page)
  - Redirect: Office dashboard for employee's office
  - Note: Associated reports remain but employee link becomes null

## Data Security Model

### Access Control Rules
1. **User Isolation**: Users can only access their own owners and related data
2. **Ownership Hierarchy**: Access flows down the ownership chain (User → Owner → Office → Employee)
3. **Cross-Reference Validation**: Office selections in forms validated against user ownership
4. **URL Parameter Security**: All ID parameters validated through get_object_or_404 with proper filtering

### Data Integrity
- Foreign key constraints ensure referential integrity
- CASCADE deletes maintain data consistency  
- Last_contacted fields automatically updated on report creation
- Transaction integrity maintained through Django ORM

## Future REST API Considerations

### Proposed REST Endpoints
```
GET    /api/owners/                    # List user's owners
POST   /api/owners/                    # Create owner
GET    /api/owners/{id}/               # Owner details
PUT    /api/owners/{id}/               # Update owner
DELETE /api/owners/{id}/               # Delete owner

GET    /api/owners/{id}/offices/       # List owner's offices  
POST   /api/owners/{id}/offices/       # Create office
GET    /api/offices/{id}/              # Office details
PUT    /api/offices/{id}/              # Update office
DELETE /api/offices/{id}/              # Delete office

GET    /api/offices/{id}/employees/    # List office employees
POST   /api/offices/{id}/employees/    # Create employee
GET    /api/employees/{id}/            # Employee details  
PUT    /api/employees/{id}/            # Update employee
DELETE /api/employees/{id}/            # Delete employee

GET    /api/reports/                   # List user's reports (filtered)
POST   /api/reports/                   # Create report
GET    /api/reports/{id}/              # Report details
PUT    /api/reports/{id}/              # Update report  
DELETE /api/reports/{id}/              # Delete report

GET    /api/dashboard/stats/           # Dashboard statistics
GET    /api/activity/matrix/           # Activity matrix data
```

### Authentication for API
- Token-based authentication (DRF TokenAuthentication)
- JWT tokens for stateless API access
- API key authentication for external integrations

### Response Format Standards
```json
{
  "success": true,
  "data": { ... },
  "pagination": {
    "page": 1,
    "per_page": 20, 
    "total": 100,
    "pages": 5
  },
  "meta": {
    "timestamp": "2024-12-19T10:30:00Z",
    "version": "1.0.0"
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Enter a valid email address"]
    }
  },
  "meta": {
    "timestamp": "2024-12-19T10:30:00Z",
    "request_id": "abc-123-def"
  }
}
```

## Integration Capabilities

### Webhook Support (Future)
- Report creation notifications
- Owner/office updates  
- Activity threshold alerts
- Export completion notifications

### Bulk Operations (Future)
- Bulk report imports from CSV
- Batch employee updates
- Mass communication logging
- Data export operations

### Real-time Features (Future)
- WebSocket connections for live updates
- Real-time dashboard metrics
- Collaborative report editing
- Activity feed notifications

This API documentation provides the foundation for both current web interface
usage and future REST API development.
"""