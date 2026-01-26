from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.text import slugify
from django.contrib import messages
from .forms import CompanyRegistrationForm, CompanyUserForm
from .models import Company, User

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def register_company(request):
    """
    Public view for new companies to sign up.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Create Company (Unverified)
                    company = Company.objects.create(
                        name=form.cleaned_data['company_name'],
                        slug=slugify(form.cleaned_data['company_name']),
                        registration_number=form.cleaned_data['registration_number'],
                        contact_email=form.cleaned_data['contact_email'],
                        contact_phone=form.cleaned_data['contact_phone'],
                        website=form.cleaned_data.get('website', ''),
                        address=form.cleaned_data['address'],
                        proof_document=form.cleaned_data['proof_document'],
                        is_verified=False, # Wait for admin approval
                        is_active=True     # Account exists, but blocked by logic until verified
                    )
                    
                    # 2. Create Admin User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['contact_email'],
                        password=form.cleaned_data['password'],
                        company=company,
                        role='employer_admin'
                    )
                    
                    # Redirect to pending page (Do not login yet)
                    return render(request, 'accounts/pending_approval.html')
                    
            except Exception as e:
                form.add_error(None, f"Registration failed: {str(e)}")
    else:
        form = CompanyRegistrationForm()

    return render(request, 'accounts/register_company.html', {'form': form})

@login_required
def company_users_list(request):
    """List and manage company users (Multiple Admins)"""
    if not request.user.company or request.user.role != 'employer_admin':
        messages.error(request, "Access denied. Only Company Admins can manage users.")
        return redirect('dashboard')
        
    users = User.objects.filter(company=request.user.company)
    
    if request.method == 'POST':
        form = CompanyUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.company = request.user.company
            user.save()
            messages.success(request, f"User {user.username} added successfully.")
            return redirect('company_users_list')
    else:
        form = CompanyUserForm()
        
    return render(request, 'accounts/company_users.html', {'users': users, 'form': form})