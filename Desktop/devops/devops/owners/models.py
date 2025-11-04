"""
CRM Models for DevOps Office Management System

This module defines the core data models for managing property owners,
office spaces, employees, and communication reports.

Models hierarchy:
    User (Django built-in)
    └── Owner (1:Many) - Property/building owners
        └── Office (1:Many) - Individual office spaces
            └── Employee (1:Many) - People working in offices
                └── Report (1:Many) - Communication logs
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Owner(models.Model):
    """
    Represents a property or building owner in the CRM system.
    
    Each owner can have multiple offices and is linked to a specific user
    for multi-tenant data isolation. Tracks basic contact information and
    the date of last communication for follow-up purposes.
    
    Attributes:
        user (ForeignKey): Link to Django User for data ownership
        name (CharField): Owner/company name (max 200 chars)
        email (EmailField): Contact email address (optional)
        last_contacted (DateField): Date of most recent communication (optional)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        """Return the owner name as the string representation."""
        return self.name


class Office(models.Model):
    """
    Represents an individual office space within a property.
    
    Each office belongs to an owner and can house multiple employees.
    Tracks location details and office-specific information like office
    number and contact history.
    
    Attributes:
        name (CharField): Office identifier/name (max 200 chars)
        number (IntegerField): Office number (1-100 range validation)
        address (CharField): Street address (max 200 chars)
        city (CharField): City name (max 100 chars)
        state (CharField): State/province (max 100 chars)
        zip_code (CharField): Postal/ZIP code (max 20 chars)
        owner (ForeignKey): Link to Owner (CASCADE delete)
        last_contacted (DateField): Date of most recent communication (optional)
    """
    name = models.CharField(max_length=200)
    number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        """Return the office name as the string representation."""
        return self.name


class Employee(models.Model):
    """
    Represents an employee working in an office space.
    
    Each employee is linked to both an office and an owner for efficient
    querying and reporting. Includes potential rating for tracking
    business development opportunities.
    
    Attributes:
        name (CharField): Employee full name (max 200 chars)
        position (CharField): Job title/role (max 100 chars)
        email (EmailField): Contact email address (optional)
        potential (IntegerField): Business potential rating (1-10 scale, default 5)
        office (ForeignKey): Link to Office (CASCADE delete)
        owner (ForeignKey): Link to Owner for quick filtering (CASCADE delete)
    """
    name =  models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    potential = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    office = models.ForeignKey(Office, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    def __str__(self):
        """Return the employee name as the string representation."""
        return self.name


class Report(models.Model):
    """
    Represents a communication log/report for tracking interactions.
    
    Reports can be linked to employees, offices, or owners directly, providing
    flexible reporting relationships. Includes communication type tracking,
    quality ratings, and full content logging for comprehensive CRM functionality.
    
    Key features:
    - Flexible relationships (can link to employee, office, or owner)
    - Communication type categorization 
    - Quality/vibe ratings for interaction assessment
    - Automatic timestamp tracking
    - User attribution for audit trails
    
    Attributes:
        subject (CharField): Optional subject line (max 200 chars)
        transcript (BooleanField): Whether transcript is available (default False)
        content (TextField): Main report content/notes (unlimited length)
        created_at (DateTimeField): Automatic creation timestamp
        employee (ForeignKey): Optional link to Employee (CASCADE delete)
        owner (ForeignKey): Optional link to Owner (CASCADE delete)
        office (ForeignKey): Optional link to Office (CASCADE delete)  
        author (ForeignKey): User who created the report (CASCADE delete)
        vibe (IntegerField): Interaction quality rating (1-10 scale, default 5)
        calltype (CharField): Communication method type (see choices below)
    """

    # Communication type choices for calltype field
    calltype_choices = [
        ('phone', 'Phone'),       # Standard phone calls
        ('email', 'Email'),       # Email correspondence  
        ('fov', 'Field Visit'),   # Field operations visits (FOV)
        ('teams', 'Teams'),       # Microsoft Teams/video calls
        ('other', 'Other'),       # Miscellaneous communication types
    ]

    subject = models.CharField(max_length=200, null=True, blank=True)
    transcript = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vibe = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    calltype = models.CharField(max_length=20, choices=calltype_choices, default='email')

    def __str__(self):
        """Return the report creation timestamp as the string representation."""
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        """Meta options for the Report model."""
        ordering = ['-created_at']  # Most recent reports first
        verbose_name = 'Communication Report'
        verbose_name_plural = 'Communication Reports'