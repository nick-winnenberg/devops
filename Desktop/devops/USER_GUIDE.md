# DevOps CRM - User Guide

This comprehensive user guide will walk you through all the features and functionality of the DevOps CRM system.

## 🚀 Getting Started

### First Login
1. **Access the Application**: Visit the live application or run locally
2. **Create Account**: Register with your email and create a password
3. **Login**: Use your credentials to access the dashboard

### Initial Setup
Once logged in, you'll see the main dashboard. To get started:
1. **Create Your First Owner**: Click "Create Owner" to add a property owner
2. **Add Offices**: Under each owner, create office spaces
3. **Add Employees**: Within offices, register employees
4. **Log Activities**: Start recording communications and field visits

## 📊 Dashboard Overview

### Main Dashboard
The home dashboard provides a comprehensive overview of your CRM activity:

- **Activity Summary**: Counts of reports by time period
  - Today's reports and field visits
  - Weekly, monthly, quarterly, and yearly totals
- **Recent Reports**: 5 most recent communication logs
- **Quick Access**: Direct links to all your owners and offices
- **Field Visit Tracking**: FOV (Field of Visit) counts for operational tracking

### Navigation Structure
- **Home** (`/`): Main dashboard with activity overview  
- **Owner Dashboards**: Individual owner details and office listings
- **Office Dashboards**: Employee listings and office-specific activity
- **Activity Dashboard**: Comprehensive reporting and analytics
- **Report Views**: Individual communication log details

## 🏢 Managing Owners

### Creating Owners
Owners represent property owners or companies you work with:

1. **Click "Create Owner"** from the main dashboard
2. **Fill Owner Information**:
   - **Name**: Company or individual name (required)
   - **Email**: Contact email address (optional)
3. **Submit** to create the owner

### Owner Dashboard Features
Each owner has their own dashboard showing:
- **Office Listings**: All offices owned by this entity
- **Recent Activity**: Latest reports for this owner
- **FOV Count**: Field visits conducted for this owner
- **Quick Actions**: Create new offices or log communications

### Managing Owner Data
- **View Details**: Click on owner name to access their dashboard
- **Delete Owner**: Use delete button (⚠️ **Warning**: Deletes all associated data)
- **Contact Tracking**: Last contacted date automatically updated when reports are logged

## 🏬 Managing Offices

### Creating Offices
Offices represent individual spaces within properties:

1. **From Owner Dashboard**: Click "Create Office"
2. **Fill Office Information**:
   - **Name**: Office identifier or tenant name (required)
   - **Number**: Office number 1-100 (required)
   - **Address**: Full street address (required)  
   - **City**: City name (required)
   - **State**: State or province (required)
   - **ZIP Code**: Postal code (required)
3. **Submit** to create the office

### Office Dashboard Features
Each office has detailed information including:
- **Employee Directory**: List of people working in this office
- **Recent Reports**: Latest communications for this office
- **Average Vibe**: Quality rating average for interactions
- **FOV Tracking**: Field visits specific to this office
- **Location Details**: Full address and contact information

### Office Management
- **Add Employees**: Register people working in the office
- **Log Reports**: Record communications at office level
- **Track Activity**: Monitor interaction history and quality ratings

## 👥 Managing Employees

### Adding Employees
Employees are individuals working within office spaces:

1. **From Office Dashboard**: Click "Create Employee" 
2. **Fill Employee Information**:
   - **Name**: Full name (required)
   - **Position**: Job title or role (required)
   - **Email**: Contact email (optional)
   - **Potential**: Business potential rating 1-10 (default: 5)
3. **Submit** to add the employee

### Employee Features
- **Contact Information**: Name, position, and email
- **Potential Rating**: Track business development opportunities (1-10 scale)
- **Report Linking**: Communications can be linked directly to specific employees
- **Office Association**: Each employee belongs to a specific office

### Employee Management
- **Edit Information**: Update employee details as needed
- **Delete Employees**: Remove employees when they leave (reports remain)
- **Track Interactions**: Log communications specific to individual employees

## 📝 Communication Reports

### Report Types
The system supports five communication types:
- **Phone**: Standard telephone conversations
- **Email**: Email correspondence  
- **FOV (Field Visit)**: On-site visits and inspections
- **Teams**: Microsoft Teams or video calls
- **Other**: Miscellaneous communication methods

### Creating Reports
Reports can be created at three levels:

#### Employee-Level Reports
1. **From Office Dashboard**: Click "Log Call" next to an employee
2. **Best For**: Specific interactions with individual people
3. **Auto-Links**: Connects to employee, office, and owner automatically

#### Office-Level Reports  
1. **From Office Dashboard**: Click "Log Call for Office"
2. **Best For**: General office communications not tied to specific employees
3. **Auto-Links**: Connects to office and owner

#### Owner-Level Reports
1. **From Owner Dashboard**: Click "Log Call for Owner"  
2. **Best For**: High-level owner communications
3. **Features**: Optional office selection from dropdown
4. **Auto-Links**: Connects to owner, optionally to specific office

### Report Fields
When creating any report, you'll fill out:

- **Subject**: Optional subject line for easy identification
- **Content**: Main report body with details (required)
- **Call Type**: Select from phone, email, FOV, teams, other (required)
- **Vibe**: Rate interaction quality 1-10 (required, default: 5)
- **Transcript**: Check if transcript is available (optional)
- **Office**: Select specific office (owner-level reports only)

### Report Features
- **Automatic Timestamps**: Created date/time automatically recorded
- **Last Contacted Updates**: Owner and office last_contacted dates updated automatically
- **User Attribution**: Reports tagged with creating user for audit trails
- **Rich Content**: Support for detailed notes and observations

## 📈 Analytics and Reporting

### Activity Dashboard
Access comprehensive analytics via the Activity Dashboard:

#### Date Range Filtering
- **Start Date**: Filter reports from specific date
- **End Date**: Filter reports until specific date  
- **Dynamic Display**: Table shows only when filters are applied

#### Activity Matrix
The system generates a detailed matrix showing:
- **Rows**: Your property owners
- **Columns**: Communication types (phone, email, FOV, teams, other)
- **Data**: Count of reports for each owner/type combination
- **Totals**: Row and column totals plus grand total

#### FOV Tracking
Special focus on Field Visits:
- **FOV Report List**: All field visits within date range
- **FOV Counts**: Dedicated tracking in all dashboards
- **Performance Metrics**: Field visit frequency and patterns

### Report Quality Tracking
- **Vibe Ratings**: Track interaction quality on 1-10 scale
- **Average Calculations**: Office-level average vibe scores
- **Trend Analysis**: Monitor relationship quality over time

### Time-Based Analytics
All dashboards include activity metrics for:
- **Today**: Current day activity
- **This Week**: Last 7 days
- **This Month**: Last 30 days  
- **This Quarter**: Last 90 days
- **This Year**: Last 365 days

## 🔍 Advanced Features

### Multi-Tenant Security
- **Data Isolation**: You only see your own owners, offices, and reports
- **User-Based Filtering**: All data automatically filtered by ownership
- **Access Controls**: No access to other users' information

### Automatic Updates
- **Last Contacted Tracking**: Dates updated when reports are created
- **Relationship Maintenance**: Foreign key relationships automatically managed
- **Data Consistency**: Cascade deletes maintain data integrity

### Responsive Design
- **Mobile Friendly**: Bootstrap 5 responsive interface
- **Touch Optimized**: Works well on tablets and phones
- **Desktop Features**: Full functionality on all screen sizes

## 🎯 Best Practices

### Data Organization
1. **Consistent Naming**: Use clear, consistent names for owners and offices
2. **Complete Information**: Fill in all relevant fields for better tracking
3. **Regular Updates**: Keep employee and contact information current
4. **Detailed Reports**: Write comprehensive report content for future reference

### Activity Tracking
1. **Timely Logging**: Log communications promptly for accuracy
2. **Appropriate Vibe Ratings**: Use the 1-10 scale consistently
3. **FOV Documentation**: Thoroughly document field visits
4. **Regular Reviews**: Use activity dashboard to review patterns

### Relationship Management
1. **Employee Potential**: Rate and track business development opportunities
2. **Follow-up Tracking**: Use last contacted dates for follow-up planning
3. **Quality Monitoring**: Track vibe ratings to identify relationship health
4. **Comprehensive Logging**: Document all significant interactions

## 🚨 Troubleshooting

### Common Issues

**Can't Find an Owner/Office**
- Verify you're logged in as the correct user
- Check that you created the owner (multi-tenant isolation)
- Use search functionality if available

**Report Not Saving**
- Ensure all required fields are filled
- Check content field has detailed information
- Verify office selection matches owner (if applicable)

**Dashboard Not Loading**
- Refresh the page
- Check internet connection
- Verify you're still logged in

**Missing Data**
- Confirm you're looking at the right time period
- Check date range filters on activity dashboard
- Verify data was saved successfully

### Getting Help
1. **Check This Guide**: Review relevant sections
2. **Test Functionality**: Try creating sample data
3. **Review Logs**: Check for error messages
4. **Contact Support**: Reach out to system administrator

## 📱 Mobile Usage

### Mobile Features
- **Responsive Interface**: Adapts to phone screen sizes
- **Touch Navigation**: Easy navigation on touch devices
- **Quick Entry**: Streamlined forms for mobile data entry
- **Dashboard Access**: Full dashboard functionality on mobile

### Mobile Best Practices
- **Portrait Orientation**: Recommended for forms and dashboards
- **WiFi Connection**: Better performance for data-heavy dashboards
- **Regular Sync**: Ensure data is saved before closing browser

---

**Need Help?** This guide covers the core functionality of the DevOps CRM system. For additional questions or feature requests, contact your system administrator.

**Last Updated**: December 2024  
**Version**: 1.0.0