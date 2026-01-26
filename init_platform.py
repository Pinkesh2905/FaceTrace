import os
import django
import uuid

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceCognitionPlatform.settings')
django.setup()

from accounts.models import Company, User
from employees.models import Department, Designation
from cameras.models import Location

def init_platform():
    print("--------------------------------------")
    print("Initializing FaceTrace Platform (Multi-Tenant)")
    print("--------------------------------------")

    # 1. Create a Company (Tenant)
    print("\n1. Creating Tenant (Company)...")
    company, created = Company.objects.get_or_create(
        name="Varsha Irons Pvt Ltd",
        defaults={
            'slug': 'varsha-irons',
            'contact_email': 'hr@varshairons.com'
        }
    )
    if created:
        print(f"   [Created] {company.name}")
    else:
        print(f"   [Exists] {company.name}")

    # 2. Create Departments for this Company
    print("\n2. Creating Departments...")
    departments = ['Engineering', 'HR', 'Production', 'Assembly']
    for name in departments:
        code = name[:3].upper()
        Department.objects.get_or_create(
            company=company,
            code=code,
            defaults={'name': name}
        )
        print(f"   - {name}")

    # 3. Create Designations for this Company
    print("\n3. Creating Designations...")
    designations = ['Operator', 'Supervisor', 'Plant Head', 'Worker']
    for name in designations:
        code = name[:3].upper()
        Designation.objects.get_or_create(
            company=company,
            code=code,
            defaults={'name': name}
        )
        print(f"   - {name}")

    # 4. Create Locations
    print("\n4. Creating Locations...")
    Location.objects.get_or_create(
        company=company,
        code='GATE1',
        defaults={'name': 'Main Gate'}
    )
    print(f"   - Main Gate")

    # 5. Create Employer Admin (The User)
    print("\n5. Creating Employer Login...")
    username = "varsha_admin"
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email="admin@varshairons.com",
            password="admin", # Simple pass for demo
            company=company,
            role='employer_admin'
        )
        print(f"   [Created] User: {username} (Pass: admin)")
    else:
        print(f"   [Exists] User: {username}")

    print("\n--------------------------------------")
    print("Platform Initialized!")
    print(f"Log in as '{username}' to see the Employer Dashboard.")
    print("--------------------------------------")

if __name__ == '__main__':
    init_platform()