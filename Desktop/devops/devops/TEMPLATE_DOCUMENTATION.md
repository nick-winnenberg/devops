# Template Structure Documentation

## Overview
The Django CRM now uses two separate templates for form handling to provide better user experiences based on context.

## Template Files

### 1. `owners/create.html` - Owner-Specific Template
**Purpose**: Used exclusively for creating owners with office association functionality
**Used by**: `owner_create` view
**Features**:
- Custom multi-owner office association interface
- Office selection with checkboxes
- Primary owner designation options
- Enhanced visual layout specific to owner creation
- Dynamic help text based on available offices

### 2. `owners/form_create.html` - Generic Form Template  
**Purpose**: Used for all other forms (offices, employees, reports)
**Used by**:
- `office_create` - Creating new offices
- `employee_create` - Adding employees to offices
- `log_call_from_employee` - Logging communication from employee context
- `log_call_from_office` - Logging communication from office context
- `log_call_from_owner` - Logging communication from owner context

**Features**:
- Uses crispy forms for clean, consistent styling
- Dynamic titles and context based on form type
- Context-aware navigation buttons
- Information panels showing relevant context
- Responsive Bootstrap 5 design

## Template Logic

### Dynamic Content in `form_create.html`

#### Title Generation
```html
{% if owner %}
    <h2>Create New Office</h2>
{% elif office and employee %}
    <h2>Create New Employee</h2>
{% elif office or employee %}
    <h2>Log Communication</h2>
{% endif %}
```

#### Navigation Buttons
- Automatically generates appropriate "Back" buttons based on context
- Creates context-specific action buttons (Create Office, Add Employee, Save Communication)

#### Context Information Panel
Shows relevant details about:
- Owner information when creating offices
- Office and owner details when creating employees or logging calls
- Employee details when logging calls from employee context

## Form Context Variables

### Office Creation
```python
{"form": form, "owner": owner}
```

### Employee Creation  
```python
{"form": form, "office": office, "employee": True}
```

### Communication Logging
```python
# From Employee
{"form": form, "employee": employee}

# From Office  
{"form": form, "office": office}

# From Owner
{
    "form": form, 
    "owner": owner,
    "owner_offices": owner_offices,
    "office_count": office_count,
    "page_title": f"Log Communication - {owner.name}",
    "form_type": "owner_report"
}
```

## Benefits of Separation

### 1. **Maintainability**
- Owner template can be customized for complex multi-owner logic
- Generic template provides consistent experience for standard forms
- Changes to one don't affect the other

### 2. **User Experience**
- Owner creation gets specialized interface for office association
- Other forms get clean, crispy forms styling
- Context-appropriate help text and navigation

### 3. **Extensibility** 
- Easy to add new form types using the generic template
- Owner template can be enhanced with more complex features
- Clear separation of concerns

## Usage Guidelines

### When to Use `owners/create.html`
- Only for owner creation functionality
- When you need custom multi-owner interface elements
- When implementing owner-specific business logic

### When to Use `owners/form_create.html`
- For all other model creation/editing forms
- When you want consistent crispy forms styling
- For communication logging and standard CRUD operations
- When context-aware navigation is needed

## Template Customization

### Adding New Form Types
1. Update the view to pass appropriate context variables
2. Add conditional logic to `form_create.html` if needed
3. Test the dynamic title and navigation generation

### Enhancing Context Panels
The information panel in `form_create.html` can be extended by:
1. Adding new conditional blocks for your model type
2. Including relevant relationship data in view context
3. Using Bootstrap classes for consistent styling