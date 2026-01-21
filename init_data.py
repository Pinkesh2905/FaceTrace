import os
import django

# Setup Django Environment to allow database access
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceCognitionPlatform.settings')
django.setup()

from employees.models import Department, Designation
from cameras.models import Location, Camera

def populate_data():
    print("--------------------------------------")
    print("Initializing FaceCognition Master Data")
    print("--------------------------------------")

    # 1. Create Departments
    departments = [
        ('Engineering', 'ENG'),
        ('Human Resources', 'HR'),
        ('Sales', 'SAL'),
        ('Marketing', 'MKT'),
        ('Operations', 'OPS'),
        ('Management', 'MGMT'),
    ]

    print("\nCreating Departments...")
    for name, code in departments:
        obj, created = Department.objects.get_or_create(
            code=code,
            defaults={'name': name}
        )
        status = "Created" if created else "Already Exists"
        print(f"  [{status}] {name}")

    # 2. Create Designations
    designations = [
        ('Intern', 'INT'),
        ('Junior Developer', 'JRDEV'),
        ('Software Engineer', 'SE'),
        ('Senior Engineer', 'SSE'),
        ('Team Lead', 'TL'),
        ('Project Manager', 'PM'),
        ('HR Manager', 'HRM'),
        ('Director', 'DIR'),
        ('CEO', 'CEO'),
    ]

    print("\nCreating Designations...")
    for name, code in designations:
        obj, created = Designation.objects.get_or_create(
            code=code,
            defaults={'name': name}
        )
        status = "Created" if created else "Already Exists"
        print(f"  [{status}] {name}")

    # 3. Create Default Location (Required for Cameras)
    print("\nCreating Default Location...")
    loc, created = Location.objects.get_or_create(
        code='MAIN',
        defaults={'name': 'Main Office', 'address': 'Corporate Headquarters'}
    )
    status = "Created" if created else "Already Exists"
    print(f"  [{status}] {loc.name}")

    print("\n--------------------------------------")
    print("Success! Data populated.")
    print("You can now register employees with these options.")
    print("--------------------------------------")

if __name__ == '__main__':
    populate_data()