# DevOps CRM - Office Management System# DevOps Django Application



A Django-based Customer Relationship Management (CRM) system designed for managing office buildings, tenants, and field visit activities. This application helps track owners, offices, employees, and communication reports with a focus on field operations.A modern Django web application for managing owners, offices, employees, and reports with a clean Bootstrap 5 interface.



## 🚀 Quick Start## 🚀 Quick Start



### Local Development### Development Setup

```bash

# 1. Clone and setup1. **Clone and setup**

cd devops/devops  # Navigate to the Django project folder   ```bash

pip install -r requirements.txt   git clone <your-repo>

   cd devops/devops  # Navigate to the Django project folder

# 2. Database setup   pip install -r requirements.txt

python manage.py migrate   ```

python manage.py createsuperuser

2. **Database setup**

# 3. Start development server     ```bash

python manage.py runserver   python manage.py migrate

```   python manage.py createsuperuser

   ```

Visit `http://localhost:8000`

3. **Run development server**

### Cloud Deployment (Railway)   ```bash

This application is configured for Railway cloud deployment with PostgreSQL database.   python manage.py runserver

   ```

**Environment Variables Required:**

- `SECRET_KEY`: Django secret key for securityVisit `http://localhost:8000`

- `DEBUG`: Set to 'False' for production  

- `DATABASE_URL`: Automatically provided by Railway PostgreSQL### 🚂 Railway Deployment (Recommended)



**Live Demo:** [https://devops-production-f6d1.up.railway.app](https://devops-production-f6d1.up.railway.app)**Deploy in 5 minutes:**

1. Push code to GitHub

## 📋 Features2. Connect GitHub repo to Railway

3. Add PostgreSQL database service  

### Core Functionality4. Set environment variables in Railway dashboard

- **Owner Management**: Track building/property owners with contact information5. Your app is live!

- **Office Management**: Manage individual office spaces within properties  

- **Employee Tracking**: Track employees within office spacesSee [RAILWAY.md](RAILWAY.md) for detailed Railway deployment guide.

- **Activity Reports**: Log communication and field visits with detailed reports

- **Dashboard Analytics**: View activity summaries and statistics## 📁 Project Structure



### Report Types```

- **Phone Calls**: Standard phone communicationsdevops/

- **Email**: Email correspondence tracking├── devops/

- **Field Visits (FOV)**: On-site visits and inspections│   ├── settings/

- **Teams**: Microsoft Teams/video calls  │   │   ├── base.py          # Shared settings

- **Other**: Miscellaneous communication types│   │   ├── development.py   # Dev settings

│   │   └── production.py    # Prod settings

### Key Metrics│   ├── urls.py

- Activity counts by time period (daily, weekly, monthly, quarterly, yearly)│   └── wsgi.py

- Field visit (FOV) tracking and counts├── owners/                  # Main app

- Communication "vibe" ratings (1-10 scale)│   ├── models.py           # Owner, Office, Employee, Report

- Employee potential ratings (1-10 scale)│   ├── views.py            # All business logic

│   ├── forms.py            # Custom forms

## 🏗️ Architecture│   └── templates/          # Bootstrap 5 UI

├── users/                   # User management

### Models Overview├── requirements.txt         # Production dependencies

```├── Dockerfile              # Container config

User (Django built-in)├── docker-compose.yml      # Multi-service setup

└── Owner (1:Many) - Property/building owners└── .env.template           # Environment variables template

    └── Office (1:Many) - Individual office spaces```

        └── Employee (1:Many) - People working in offices

            └── Report (1:Many) - Communication logs## 🔐 Security Features

```

- ✅ Environment variables for secrets

### Applications- ✅ Production-ready Django settings

- **owners**: Core CRM functionality (owners, offices, employees, reports)- ✅ HTTPS enforcement

- **users**: User management and authentication  - ✅ Security headers

- **devops**: Main Django project configuration- ✅ CSRF protection

- ✅ SQL injection protection (Django ORM)

### Technology Stack- ✅ XSS protection

- **Backend**: Django 4.2.24, Python 3.12

- **Database**: PostgreSQL (production), SQLite (development)## 🛠️ Features

- **Frontend**: Bootstrap 5 with Django Crispy Forms

- **Deployment**: Railway with Gunicorn and WhiteNoise- **Dashboard**: Overview of all reports and statistics

- **Static Files**: WhiteNoise for production serving- **Owner Management**: Create and manage property owners

- **Office Management**: Track office locations and details

## 📁 Project Structure- **Employee Management**: Manage employees per office

- **Report System**: Log calls and activities

```- **Activity Dashboard**: Filtered reporting and analytics

devops/- **Matrix Reporting**: Call type breakdown by owner

├── devops/                    # Django project root- **Responsive UI**: Bootstrap 5 with clean design

│   ├── settings_simple.py     # Production-ready Railway config ⭐

│   ├── settings.py           # Original Django settings  ## 🧪 Testing

│   ├── urls.py               # URL routing

│   ├── wsgi.py              # WSGI entry point```bash

│   └── middleware.py        # Custom middleware# Run tests

├── owners/                   # Main CRM applicationpython manage.py test

│   ├── models.py            # Owner, Office, Employee, Report models

│   ├── views.py             # Business logic and dashboards# Check deployment readiness

│   ├── forms.py             # Django forms for data inputpython manage.py check --deploy

│   ├── urls.py              # URL patterns```

│   └── templates/owners/    # Bootstrap 5 UI templates

├── users/                   # User management app## 📊 Monitoring

├── requirements.txt         # Python dependencies

├── manage.py               # Django management (uses settings_simple)Production apps include:

├── db.sqlite3              # Local development database- Structured logging

└── README.md               # This file- Error tracking ready (Sentry)

```- Performance monitoring

- Database query optimization

## 📊 Data Models

## 🔧 Environment Variables

### Owner Model

- **name**: Owner/company nameCopy `.env.template` to `.env` and configure:

- **email**: Contact email address  

- **last_contacted**: Date of most recent communication```bash

- **user**: Link to Django User (multi-tenant support)SECRET_KEY=your-secret-key

DEBUG=False

### Office Model  DATABASE_URL=postgresql://...

- **name**: Office identifier/nameALLOWED_HOSTS=yourdomain.com

- **number**: Office number (1-100)```

- **address**: Street address

- **city, state, zip_code**: Location details## 📝 License

- **owner**: Foreign key to Owner

- **last_contacted**: Date of most recent communicationPrivate project - All rights reserved



### Employee Model## 🤝 Support

- **name**: Employee full name

- **position**: Job title/roleFor deployment help, see [DEPLOYMENT.md](DEPLOYMENT.md) or contact the development team.
- **email**: Contact email
- **potential**: Rating of potential value (1-10 scale)
- **office**: Foreign key to Office  
- **owner**: Foreign key to Owner (for quick filtering)

### Report Model
- **subject**: Optional subject line
- **content**: Main report content/notes
- **calltype**: Communication method (phone, email, fov, teams, other)
- **vibe**: Interaction quality rating (1-10 scale)
- **transcript**: Boolean flag for transcript availability
- **created_at**: Automatic timestamp
- **author**: User who created the report
- **employee, office, owner**: Flexible relationship links

## 🎯 User Workflows

### Basic CRM Workflow
1. **Create Owner**: Add a new property owner/company
2. **Add Offices**: Create office spaces under the owner
3. **Add Employees**: Register people working in those offices
4. **Log Reports**: Record communications and field visits
5. **View Analytics**: Monitor activity through dashboards

### Field Operations Workflow  
1. **Plan Field Visits**: Review office and employee information
2. **Conduct FOV**: Visit office locations
3. **Log Field Report**: Record findings, interactions, and ratings
4. **Track Progress**: Monitor FOV counts and follow-up needs
5. **Analyze Trends**: Review vibe ratings and activity patterns

## 🧭 Navigation Structure

### Main Dashboard (`/`)
- Activity overview with counts and recent reports
- Quick access to all owners and offices
- Time-based activity summaries

### Owner Dashboard (`/owner/{id}/`)
- Owner-specific office list  
- Recent reports for this owner
- FOV count for owner's properties

### Office Dashboard (`/office/{id}/`)
- Employee list for the office
- Recent activity reports
- Average vibe rating
- Office-specific FOV count

### Activity Dashboard (`/activity/`)  
- Comprehensive activity matrix
- Date range filtering  
- Per-owner and per-calltype breakdowns
- FOV report listings

## 🔧 Configuration

### Settings Structure
- `settings.py`: Original Django settings (not used in production)
- `settings_simple.py`: **Production-ready Railway configuration** ⭐
- `settings/`: Directory with environment-specific configurations

### Key Configuration Files
- `manage.py`: Django management script (uses settings_simple)
- `wsgi.py`: WSGI application entry point (uses settings_simple)  
- `requirements.txt`: Python dependencies
- `railway.json`: Railway deployment configuration

### Environment Variables
```bash
# Required for production
SECRET_KEY=your-secret-key-here
DEBUG=False

# Automatically provided by Railway  
DATABASE_URL=postgresql://...

# Optional customization
ALLOWED_HOSTS=yourdomain.com
```

## 🔐 Security Features

- Django's built-in authentication system
- CSRF protection enabled
- Secure secret key management
- Environment-based configuration  
- Multi-tenant data isolation (users only see their own data)
- HTTPS enforcement in production
- Security headers via middleware

## 📱 Responsive Design

The application uses Bootstrap 5 for a mobile-friendly, responsive interface that works across devices:
- Desktop dashboards with full data tables
- Mobile-optimized forms and navigation
- Touch-friendly buttons and interactions

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection**: Ensure DATABASE_URL is properly set
2. **Static Files**: Run `python manage.py collectstatic` for production  
3. **Migrations**: Run `python manage.py migrate` after model changes
4. **Dependencies**: Check `pip install -r requirements.txt`

### Development Tips
- Use SQLite for local development (automatic fallback)
- Enable DEBUG=True for detailed error messages
- Use Django admin interface for data management
- Check console logs for database connection status

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Check deployment readiness  
python manage.py check --deploy

# Validate models
python manage.py check
```

## 📈 Future Enhancements

### Potential Features
- Email integration for automatic report creation
- Calendar integration for scheduling field visits
- Mobile app for field technicians
- Advanced analytics and reporting
- Export functionality (CSV, PDF)
- Document attachment support
- Automated reminder systems

### Technical Improvements
- API development for mobile integration  
- Background task processing
- Caching layer for performance
- Advanced search and filtering
- Bulk operations support

## 📝 License

This project is for internal business use. All rights reserved.

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Django Version**: 4.2.24  
**Python Version**: 3.12+