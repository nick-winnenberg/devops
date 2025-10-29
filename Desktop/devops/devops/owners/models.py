from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 

class Owner (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Office (models.Model):
    name = models.CharField(max_length=200)
    number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    last_contacted = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Employee (models.Model):
    name =  models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    potential = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    office = models.ForeignKey(Office, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

class Report (models.Model):

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
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vibe = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    calltype = models.CharField(max_length=20, choices=calltype_choices, default='email')

    def __str__(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")