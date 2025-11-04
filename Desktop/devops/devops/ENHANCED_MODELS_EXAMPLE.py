"""
Enhanced Models with Many-to-Many Office Ownership

This shows how to modify the models to support multiple owners per office,
which would address the "office has two owners" scenario.

IMPORTANT: This would require database migrations and updates to all related views/forms.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Owner(models.Model):
    """
    Represents a property or building owner in the CRM system.
    
    With many-to-many relationship, owners can share ownership of offices.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Office(models.Model):
    """
    Represents an individual office space that can have multiple owners.
    
    CHANGED: Using ManyToManyField instead of ForeignKey for owners
    """
    name = models.CharField(max_length=200)
    number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    # CHANGED: Multiple owners per office
    owners = models.ManyToManyField(Owner, related_name='offices')
    
    # NEW: Primary owner for default relationships
    primary_owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='primary_offices')
    
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Owners: {', '.join([o.name for o in self.owners.all()])})"


class Employee(models.Model):
    """
    Employee model updated to work with multiple office owners.
    """
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    potential = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    office = models.ForeignKey(Office, on_delete=models.CASCADE)
    
    # CHANGED: Link to primary owner by default
    primary_owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_all_owners(self):
        """Get all owners of this employee's office."""
        return self.office.owners.all()


class Report(models.Model):
    """
    Enhanced Report model to handle multiple ownership scenarios.
    """
    
    calltype_choices = [
        ('phone', 'Phone'),
        ('email', 'Email'), 
        ('fov', 'Field Visit'),
        ('teams', 'Teams'),
        ('other', 'Other'),
    ]

    subject = models.CharField(max_length=200, null=True, blank=True)
    transcript = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relationships
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, null=True, blank=True)
    
    # CHANGED: Primary owner (main contact) 
    primary_owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='primary_reports')
    
    # NEW: Additional owners involved in this communication
    additional_owners = models.ManyToManyField(Owner, blank=True, related_name='secondary_reports')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vibe = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    calltype = models.CharField(max_length=20, choices=calltype_choices, default='email')

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.primary_owner.name}"

    def get_all_involved_owners(self):
        """Get all owners involved in this report."""
        owners = [self.primary_owner]
        owners.extend(list(self.additional_owners.all()))
        return owners

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Communication Report'
        verbose_name_plural = 'Communication Reports'