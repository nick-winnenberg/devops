#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('C:/Users/Nick/Desktop/devops/devops')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings_simple')
django.setup()

from owners.models import Office, Owner
from django.contrib.auth.models import User
from django.db import models

print("=== Office Ownership Debug ===")
for office in Office.objects.all():
    owner_info = "None"
    user_info = "None"
    
    if office.owner:
        owner_info = office.owner.name
        if office.owner.user:
            user_info = office.owner.user.username
    
    print(f"Office: {office.name}")
    print(f"  Legacy Owner: {owner_info}")
    print(f"  Owner's User: {user_info}")
    print(f"  Primary Owner: {office.primary_owner}")
    print()

print("=== Testing Form Query for Each User ===")
for user in User.objects.all():
    offices = Office.objects.filter(
        models.Q(primary_owner__user=user) | 
        models.Q(owner__user=user)
    ).distinct()
    print(f"User: {user.username} -> Offices: {offices.count()}")
    for office in offices:
        print(f"  - {office.name}")