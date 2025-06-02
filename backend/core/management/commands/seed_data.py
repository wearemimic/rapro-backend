from django.core.management.base import BaseCommand
#from django.contrib.auth import get_user_model
from core.models import CustomUser as User

# User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with an initial user"

    def handle(self, *args, **kwargs):
        email = "mannese@wearemimic.com"
        password = "password"

        if not User.objects.filter(email=email).exists():
            advisor = User.objects.create_user(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"User {email} created"))
        else:
            advisor = User.objects.get(email=email)
            self.stdout.write(self.style.WARNING(f"User {email} already exists"))

        # Seed clients for this advisor
        from core.models import Client
        client_data = [
            {"first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "birthdate": "1980-05-01", "tax_status": "single"},
            {"first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "birthdate": "1975-09-15", "tax_status": "married"},
            {"first_name": "Carol", "last_name": "Williams", "email": "carol@example.com", "birthdate": "1990-12-22", "tax_status": "head_of_household"},
        ]

        for data in client_data:
            if not Client.objects.filter(email=data["email"]).exists():
                Client.objects.create(advisor=advisor, **data)
                self.stdout.write(self.style.SUCCESS(f"Client {data['email']} created"))
            else:
                self.stdout.write(self.style.WARNING(f"Client {data['email']} already exists"))