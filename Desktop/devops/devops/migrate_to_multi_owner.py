"""
Multi-Owner Migration Helper Script

This script helps migrate your existing single-owner data to the new multi-owner structure.
Run this after the Django migration completes to ensure all data relationships are properly set up.

Usage:
    python manage.py shell
    >>> exec(open('migrate_to_multi_owner.py').read())
"""

from owners.models import Owner, Office, Employee, Report

def migrate_all_data():
    """
    Migrate all existing single-owner relationships to multi-owner structure.
    """
    print("🚀 Starting migration to multi-owner support...")
    
    # Statistics
    offices_migrated = 0
    employees_migrated = 0
    reports_migrated = 0
    
    # Step 1: Migrate Offices
    print("\n📋 Step 1: Migrating Office ownership...")
    for office in Office.objects.all():
        if office.migrate_single_owner_to_multi():
            offices_migrated += 1
            print(f"  ✅ Migrated office: {office.name} -> Primary: {office.primary_owner.name}")
    
    print(f"📊 Migrated {offices_migrated} offices to multi-owner structure")
    
    # Step 2: Migrate Employees
    print("\n👥 Step 2: Migrating Employee relationships...")
    for employee in Employee.objects.all():
        if employee.migrate_owner_relationship():
            employees_migrated += 1
            print(f"  ✅ Migrated employee: {employee.name} -> Office: {employee.office.name}")
    
    print(f"📊 Migrated {employees_migrated} employee relationships")
    
    # Step 3: Migrate Reports  
    print("\n📝 Step 3: Migrating Report ownership...")
    for report in Report.objects.all():
        if report.migrate_owner_relationships():
            reports_migrated += 1
            print(f"  ✅ Migrated report: {report.created_at} -> Primary: {report.primary_owner.name}")
    
    print(f"📊 Migrated {reports_migrated} report relationships")
    
    # Step 4: Verification
    print("\n🔍 Step 4: Verifying migration results...")
    
    offices_with_primary = Office.objects.filter(primary_owner__isnull=False).count()
    offices_total = Office.objects.count()
    
    reports_with_primary = Report.objects.filter(primary_owner__isnull=False).count()
    reports_total = Report.objects.count()
    
    print(f"📋 Offices with primary owner: {offices_with_primary}/{offices_total}")
    print(f"📝 Reports with primary owner: {reports_with_primary}/{reports_total}")
    
    if offices_with_primary == offices_total and reports_with_primary == reports_total:
        print("\n✅ SUCCESS: All data successfully migrated to multi-owner structure!")
    else:
        print("\n⚠️  WARNING: Some records may need manual review")
    
    return {
        'offices_migrated': offices_migrated,
        'employees_migrated': employees_migrated, 
        'reports_migrated': reports_migrated,
        'offices_with_primary': offices_with_primary,
        'reports_with_primary': reports_with_primary
    }

def verify_data_integrity():
    """
    Verify that all relationships are properly set up after migration.
    """
    print("\n🔍 Verifying data integrity...")
    
    issues = []
    
    # Check offices
    for office in Office.objects.all():
        if not office.primary_owner:
            issues.append(f"Office '{office.name}' has no primary owner")
        
        if not office.owners.exists() and office.primary_owner:
            office.owners.add(office.primary_owner)
            print(f"  🔧 Fixed: Added primary owner to owners list for '{office.name}'")
    
    # Check reports
    for report in Report.objects.all():
        if not report.primary_owner and not report.owner:
            issues.append(f"Report {report.id} has no owner relationship")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issues:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("\n✅ Data integrity check passed!")
    
    return issues

def create_sample_multi_owner_office():
    """
    Create a sample office with multiple owners to test the new functionality.
    """
    print("\n🏢 Creating sample multi-owner office...")
    
    # Find existing owners or create test ones
    owners = list(Owner.objects.all()[:2])  # Get up to 2 existing owners
    
    if len(owners) < 2:
        print("  Need at least 2 owners to demonstrate multi-owner functionality")
        print("  Create additional owners through the web interface first")
        return None
    
    # Create sample office
    sample_office = Office.objects.create(
        name="Multi-Owner Demo Office",
        number=99,
        address="123 Partnership Plaza",
        city="Demo City",
        state="Test State",
        zip_code="12345",
        primary_owner=owners[0]
    )
    
    # Add multiple owners
    sample_office.owners.add(owners[0])  # Primary owner
    sample_office.owners.add(owners[1])  # Additional owner
    
    print(f"  ✅ Created sample office: {sample_office.name}")
    print(f"     Primary Owner: {owners[0].name}")
    print(f"     Additional Owner: {owners[1].name}")
    
    return sample_office

def show_migration_summary():
    """
    Show a summary of the current multi-owner setup.
    """
    print("\n📊 MULTI-OWNER MIGRATION SUMMARY")
    print("=" * 50)
    
    total_offices = Office.objects.count()
    multi_owner_offices = Office.objects.annotate(
        owner_count=models.Count('owners')
    ).filter(owner_count__gt=1).count()
    
    total_reports = Report.objects.count()
    multi_owner_reports = Report.objects.filter(
        additional_owners__isnull=False
    ).distinct().count()
    
    print(f"📋 Total Offices: {total_offices}")
    print(f"🤝 Multi-Owner Offices: {multi_owner_offices}")
    print(f"📝 Total Reports: {total_reports}")
    print(f"👥 Reports with Additional Owners: {multi_owner_reports}")
    
    if multi_owner_offices > 0:
        print(f"\n🎉 Multi-owner functionality is active!")
        print("   You can now:")
        print("   - Add multiple owners to existing offices")
        print("   - Create reports involving multiple owners")
        print("   - Track complex ownership relationships")
    else:
        print(f"\n📝 Ready for multi-owner functionality!")
        print("   Add additional owners to offices through the web interface")

# Main migration execution
if __name__ == "__main__":
    print("🚀 MULTI-OWNER MIGRATION UTILITY")
    print("=" * 50)
    
    # Run migration
    results = migrate_all_data()
    
    # Verify integrity
    issues = verify_data_integrity()
    
    # Show summary
    show_migration_summary()
    
    print(f"\n✅ Migration completed successfully!")
    print(f"   Next steps:")
    print(f"   1. Test the web interface with your migrated data")
    print(f"   2. Try adding additional owners to offices")
    print(f"   3. Create reports with multiple owner involvement")
    
else:
    # When imported in Django shell
    print("Multi-owner migration helper loaded!")
    print("Available functions:")
    print("  - migrate_all_data()          # Migrate existing data")
    print("  - verify_data_integrity()     # Check for issues")
    print("  - create_sample_multi_owner_office()  # Test functionality")
    print("  - show_migration_summary()    # View current status")