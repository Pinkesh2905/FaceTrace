from django import forms
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

class CompanyRegistrationForm(forms.Form):
    """
    Professional Company Registration Form
    """
    # Company Details
    company_name = forms.CharField(max_length=100, label="Company Name")
    registration_number = forms.CharField(max_length=50, label="Registration / Tax ID")
    contact_email = forms.EmailField(label="Official Email")
    contact_phone = forms.CharField(max_length=15, label="Phone Number")
    website = forms.URLField(required=False, label="Website (Optional)")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    proof_document = forms.FileField(label="Business Proof Document", help_text="Upload Certificate of Incorporation, GST, or Tax Document (PDF/Image).")
    
    # Admin User Details
    username = forms.CharField(max_length=150, help_text="Admin Username")
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        username = cleaned_data.get("username")
        company_name = cleaned_data.get("company_name")

        if password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")
        
        if User.objects.filter(username=username).exists():
            self.add_error('username', "Username already taken")
            
        if Company.objects.filter(name=company_name).exists():
            self.add_error('company_name', "Company already registered")
            
        return cleaned_data

class CompanyUserForm(forms.ModelForm):
    """Form to add additional admins/managers for a company"""
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password']
        widgets = {
            'role': forms.Select(choices=[
                ('employer_admin', 'Admin (Full Access)'),
                ('manager', 'Manager (Read Only)')
            ])
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user