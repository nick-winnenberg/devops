"""CRM Models for DevOps Office Management System with Multi-Owner Support."""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Owner(models.Model):
    """Property/building owner with user association and contact tracking."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Office(models.Model):
    """Office space with multi-owner support and primary contact designation."""
    name = models.CharField(max_length=200)
    number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    # Multi-owner support
    owners = models.ManyToManyField(
        Owner, 
        related_name='offices',
        blank=True,
        help_text="All owners of this office (can select multiple)"
    )
    
    # Primary owner for main contact
    primary_owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE,
        related_name='primary_offices',
        null=True,  # Allow null during migration
        blank=True,
        help_text="Main owner who serves as primary contact"
    )
    
    # Deprecated: single owner (kept for migration compatibility)
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE,
        null=True,  # Made nullable for migration
        blank=True,
        help_text="DEPRECATED: Single owner (being migrated to multi-owner support)"
    )
    
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.primary_owner:
            owner_count = self.owners.count()
            if owner_count > 1:
                return f"{self.name} (Primary: {self.primary_owner.name}, +{owner_count-1} others)"
            else:
                return f"{self.name} ({self.primary_owner.name})"
        elif self.owner:  # Fallback to old single owner during migration
            return f"{self.name} ({self.owner.name})"
        else:
            return f"{self.name} (No Owner Assigned)"
    
    def get_owner_names(self):
        if self.owners.exists():
            return ", ".join([owner.name for owner in self.owners.all()])
        elif self.owner:  # Fallback during migration
            return self.owner.name
        else:
            return "No Owners"
    
    def get_primary_owner(self):
        """Get the primary owner, with fallback to single owner during migration."""
        return self.primary_owner or self.owner
    
    def is_owner(self, owner_obj):
        """Check if the given owner is an owner of this office."""
        if self.owners.exists():
            return self.owners.filter(id=owner_obj.id).exists()
        elif self.owner:  # Fallback during migration
            return self.owner.id == owner_obj.id
        return False
    
    def get_owners_for_user(self, user):
        """Get all owners of this office that belong to the specified user."""
        if self.owners.exists():
            return self.owners.filter(user=user)
        elif self.owner and self.owner.user == user:  # Fallback during migration
            return Owner.objects.filter(id=self.owner.id)
        return Owner.objects.none()
    
    def add_owner(self, owner_obj, set_as_primary=False):
        """Add an owner to this office, optionally setting as primary."""
        self.owners.add(owner_obj)
        if set_as_primary or not self.primary_owner:
            self.primary_owner = owner_obj
            self.save()
    
    def remove_owner(self, owner_obj):
        """Remove an owner from this office, handling primary owner reassignment."""
        if self.is_owner(owner_obj):
            self.owners.remove(owner_obj)
            
            # If removing primary owner, assign new primary from remaining owners
            if self.primary_owner == owner_obj:
                remaining_owners = self.owners.all()
                if remaining_owners.exists():
                    self.primary_owner = remaining_owners.first()
                    self.save()
                else:
                    # No owners left - this might be an error condition
                    self.primary_owner = None
                    self.save()
    
    def migrate_single_owner_to_multi(self):
        """Helper method to migrate from single owner to multi-owner structure."""
        if self.owner and not self.primary_owner:
            self.primary_owner = self.owner
            self.save()
            self.owners.add(self.owner)
            return True
        return False

    class Meta:
        ordering = ['name']
        verbose_name = 'Office Space'
        verbose_name_plural = 'Office Spaces'


class Employee(models.Model):
    """
    Enhanced employee model supporting multi-owner office relationships.
    
    Each employee is linked to an office (which may have multiple owners) and 
    includes efficient querying methods for all ownership relationships.
    Includes potential rating for tracking business development opportunities.
    
    Enhanced Attributes:
        name (CharField): Employee full name (max 200 chars)
        position (CharField): Job title/role (max 100 chars)
        email (EmailField): Contact email address (optional)
        potential (IntegerField): Business potential rating (1-10 scale, default 5)
        office (ForeignKey): Link to Office (CASCADE delete)
        
        # DEPRECATED (kept for migration compatibility):
        owner (ForeignKey): Single owner link (will be computed from office)
    """
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    potential = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='employees')
    
    # DEPRECATED: Keep during migration, but make nullable
    # TODO: Remove this field after migration - use office relationships instead
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="DEPRECATED: Use office.primary_owner or office.owners instead"
    )

    def __str__(self):
        """Return the employee name with office context."""
        return f"{self.name} ({self.office.name})"
    
    def get_primary_owner(self):
        """Get the primary owner of this employee's office."""
        if self.office:
            return self.office.get_primary_owner()
        return self.owner  # Fallback during migration
    
    def get_all_owners(self):
        """Get all owners of this employee's office."""
        if self.office and self.office.owners.exists():
            return self.office.owners.all()
        elif self.owner:  # Fallback during migration
            return Owner.objects.filter(id=self.owner.id)
        return Owner.objects.none()
    
    def is_owned_by(self, owner_obj):
        """Check if this employee's office is owned by the specified owner."""
        if self.office:
            return self.office.is_owner(owner_obj)
        return self.owner == owner_obj  # Fallback during migration
    
    def get_owners_for_user(self, user):
        """Get all owners of this employee's office that belong to the specified user."""
        if self.office:
            return self.office.get_owners_for_user(user)
        elif self.owner and self.owner.user == user:
            return Owner.objects.filter(id=self.owner.id)
        return Owner.objects.none()
    
    def migrate_owner_relationship(self):
        if self.owner and self.office:
            # Ensure the office has this owner
            if not self.office.is_owner(self.owner):
                self.office.add_owner(self.owner, set_as_primary=True)
            return True
        elif self.office and self.office.get_primary_owner():
            # Set owner based on office's primary owner
            self.owner = self.office.get_primary_owner()
            self.save()
            return True
        return False

    class Meta:
        ordering = ['name']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'


class Report(models.Model):
    """Communication report with multi-owner support and flexible relationships."""

    # Communication type choices
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
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, null=True, blank=True)
    
    # Enhanced owner relationships
    primary_owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE,
        related_name='primary_reports',
        null=True,  # Allow null during migration
        blank=True,
        help_text="Main owner contact for this communication"
    )
    
    additional_owners = models.ManyToManyField(
        Owner,
        related_name='secondary_reports',
        blank=True,
        help_text="Additional owners involved in this communication"
    )
    
    # Deprecated: single owner (kept for migration)
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='legacy_reports',
        help_text="DEPRECATED: Single owner (being migrated to primary_owner)"
    )
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vibe = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    calltype = models.CharField(max_length=20, choices=calltype_choices, default='email')

    def __str__(self):
        timestamp = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        owner_info = self.get_primary_owner_name()
        if owner_info:
            return f"{timestamp} - {owner_info}"
        return timestamp
    
    def get_primary_owner(self):
        """Get the primary owner for this report, with migration fallback."""
        return self.primary_owner or self.owner
    
    def get_primary_owner_name(self):
        """Get the primary owner name for display purposes."""
        primary = self.get_primary_owner()
        return primary.name if primary else "No Owner"
    
    def get_all_involved_owners(self):
        """Get all owners involved in this report (primary + additional)."""
        owners = []
        
        # Add primary owner
        primary = self.get_primary_owner()
        if primary:
            owners.append(primary)
        
        # Add additional owners (avoiding duplicates)
        for additional_owner in self.additional_owners.all():
            if additional_owner not in owners:
                owners.append(additional_owner)
        
        return owners
    
    def get_office_owners(self):
        """Get all owners of the associated office (if office is linked)."""
        if self.office:
            return self.office.owners.all()
        return Owner.objects.none()
    
    def is_owner_involved(self, owner_obj):
        """Check if the specified owner is involved in this report."""
        return (
            self.get_primary_owner() == owner_obj or
            self.additional_owners.filter(id=owner_obj.id).exists()
        )
    
    def add_additional_owner(self, owner_obj):
        """Add an owner to the additional owners list."""
        if owner_obj != self.get_primary_owner():  # Don't duplicate primary owner
            self.additional_owners.add(owner_obj)
    
    def get_relationship_context(self):
        """Get a description of what this report relates to."""
        contexts = []
        
        if self.employee:
            contexts.append(f"Employee: {self.employee.name}")
        if self.office:
            contexts.append(f"Office: {self.office.name}")
        
        primary = self.get_primary_owner()
        if primary:
            contexts.append(f"Primary Owner: {primary.name}")
        
        additional_count = self.additional_owners.count()
        if additional_count > 0:
            contexts.append(f"+{additional_count} additional owners")
        
        return " | ".join(contexts) if contexts else "General Communication"
    
    def migrate_owner_relationships(self):
        """Helper method to migrate from single owner to enhanced owner structure."""
        if self.owner and not self.primary_owner:
            self.primary_owner = self.owner
            self.save()
            return True
        return False

    class Meta:
        ordering = ['-created_at']  # Most recent reports first
        verbose_name = 'Communication Report'
        verbose_name_plural = 'Communication Reports'
        
    def save(self, *args, **kwargs):
        # Auto-set primary owner from employee or office if not set
        if not self.primary_owner and not self.owner:
            if self.employee and self.employee.office:
                self.primary_owner = self.employee.office.get_primary_owner()
            elif self.office:
                self.primary_owner = self.office.get_primary_owner()
        
        super().save(*args, **kwargs)