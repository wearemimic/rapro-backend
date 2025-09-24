from django.core.management.base import BaseCommand
#from django.contrib.auth import get_user_model
from core.models import CustomUser as User

# User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with an initial user"

    def handle(self, *args, **kwargs):
        email = "mannese@wearemimic.com"
        password = "$Arizona123"

        if not User.objects.filter(email=email).exists():
            advisor = User.objects.create_user(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"User {email} created"))
        else:
            advisor = User.objects.get(email=email)
            self.stdout.write(self.style.WARNING(f"User {email} already exists"))

        # Always ensure this user is a super admin
        advisor.is_platform_admin = True
        advisor.is_staff = True
        advisor.is_superuser = True
        advisor.admin_role = 'super_admin'
        advisor.subscription_status = 'active'
        advisor.subscription_plan = 'monthly'
        advisor.save()
        self.stdout.write(self.style.SUCCESS(f"User {email} configured as super admin with active subscription"))

        # Seed clients for this advisor
        from core.models import Client, Scenario, IncomeSource
        client_data = [
            {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "birthdate": "1980-05-01", "tax_status": "Single", "gender": "Female"},
            {"first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "birthdate": "1975-09-15", "tax_status": "Single", "gender": "Male"},
            {"first_name": "Carol", "last_name": "Williams", "email": "carol@example.com", "birthdate": "1990-12-22", "tax_status": "Married Filing Jointly", "gender": "Female"},
        ]

        for data in client_data:
            if not Client.objects.filter(email=data["email"]).exists():
                client = Client.objects.create(advisor=advisor, **data)
                self.stdout.write(self.style.SUCCESS(f"Client {data['email']} created"))
            else:
                client = Client.objects.get(email=data["email"])
                self.stdout.write(self.style.WARNING(f"Client {data['email']} already exists"))

            # Seed a scenario for each client
            scenario, created = Scenario.objects.get_or_create(
                client=client,
                name="Base Scenario",
                defaults={
                    "retirement_age": 65,
                    "medicare_age": 65,
                    "mortality_age": 90,
                    "retirement_year": 2030,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Scenario for {client.email} created"))
            else:
                self.stdout.write(self.style.WARNING(f"Scenario for {client.email} already exists"))

            # Add Social Security IncomeSource
            if not scenario.income_sources.filter(income_type="social_security").exists():
                IncomeSource.objects.create(
                    scenario=scenario,
                    owned_by="primary",
                    income_type="social_security",
                    income_name="Social Security",
                    monthly_amount=2000,
                    age_to_begin_withdrawal=67,
                    age_to_end_withdrawal=90,
                    cola=2.0,
                    tax_rate=0,
                )
                self.stdout.write(self.style.SUCCESS(f"Social Security income for {client.email} created"))
            else:
                self.stdout.write(self.style.WARNING(f"Social Security income for {client.email} already exists"))

            # Add 401k IncomeSource
            if not scenario.income_sources.filter(income_type="Traditional_401k").exists():
                IncomeSource.objects.create(
                    scenario=scenario,
                    owned_by="primary",
                    income_type="Traditional_401k",
                    income_name="401k",
                    current_asset_balance=100000,
                    monthly_contribution=500,
                    age_to_begin_withdrawal=67,
                    age_to_end_withdrawal=90,
                    rate_of_return=5.0,
                    tax_rate=15.0,
                )
                self.stdout.write(self.style.SUCCESS(f"401k income for {client.email} created"))
            else:
                self.stdout.write(self.style.WARNING(f"401k income for {client.email} already exists"))