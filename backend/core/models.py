# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.utils import timezone



# Custom user manager to use email instead of username
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    white_label_company_name = models.CharField(max_length=100, blank=True)
    white_label_support_email = models.EmailField(blank=True)
    primary_color = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    # Stripe related fields
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    subscription_status = models.CharField(max_length=50, blank=True)
    subscription_plan = models.CharField(max_length=20, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email

    @property
    def is_subscription_active(self):
        return self.subscription_status == 'active' and (
            self.subscription_end_date is None or 
            self.subscription_end_date > timezone.now()
        )
    
class Client(models.Model):
    # advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients'
    )
    
    # Identifying information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    birthdate = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    tax_status = models.CharField(max_length=50, choices=[
        ('Single', 'Single'),
        ('Married Filing Jointly', 'Married Filing Jointly'),
        ('Married Filing Separately', 'Married Filing Separately'),
        ('Head of Household', 'Head of Household'),
        ('Qualifying Widow(er)', 'Qualifying Widow(er)')
    ])

    # Timestamps and notes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('reviewed', 'Reviewed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')


class Spouse(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='spouse')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    def __str__(self):
        return f"Spouse of {self.client.first_name} {self.client.last_name}"
    
class Scenario(models.Model):
    client = models.ForeignKey(Client, related_name='scenarios', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    retirement_age = models.PositiveIntegerField(default=65)
    medicare_age = models.PositiveIntegerField(default=65)
    spouse_retirement_age = models.PositiveIntegerField(blank=True, null=True, default=65)
    spouse_medicare_age = models.PositiveIntegerField(blank=True, null=True, default=65)
    mortality_age = models.PositiveIntegerField(default=90)
    spouse_mortality_age = models.PositiveIntegerField(blank=True, null=True, default=90)
    retirement_year = models.PositiveIntegerField(default=2025)
    share_with_client = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    part_b_inflation_rate = models.FloatField(default=6.0)
    part_d_inflation_rate = models.FloatField(default=6.0)
    FRA_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roth_conversion_start_year = models.PositiveIntegerField(null=True, blank=True)
    roth_conversion_duration = models.PositiveIntegerField(null=True, blank=True)
    roth_conversion_annual_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.client.first_name})"


# IncomeSource model
class IncomeSource(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='income_sources')
    OWNED_BY_CHOICES = [
        ('primary', 'Primary'),
        ('spouse', 'Spouse')
    ]
    owned_by = models.CharField(max_length=10, choices=OWNED_BY_CHOICES)
    income_type = models.CharField(max_length=200)
    income_name = models.CharField(max_length=50)
    current_asset_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    age_to_begin_withdrawal = models.PositiveIntegerField(null=True, blank=True)
    age_to_end_withdrawal = models.PositiveIntegerField()
    rate_of_return = models.FloatField(default=0)
    cola = models.FloatField(default=0)
    exclusion_ratio = models.FloatField(default=0)
    tax_rate = models.FloatField(default=0)

    def __str__(self):
        return f"{self.income_type} for {self.scenario.name}"


# YearlyCalculation model
class YearlyCalculation(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='yearly_calculations')
    year = models.PositiveIntegerField()
    age = models.PositiveIntegerField()
    spouse_age = models.PositiveIntegerField(null=True, blank=True)
    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2)
    federal_tax = models.DecimalField(max_digits=12, decimal_places=2)
    medicare_base = models.DecimalField(max_digits=12, decimal_places=2)
    irmaa_surcharge = models.DecimalField(max_digits=12, decimal_places=2)
    net_income = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.year} - {self.scenario.name}"