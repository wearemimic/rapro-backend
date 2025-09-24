from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Client

class ClientModelTest(TestCase):
    def setUp(self):
        self.advisor = get_user_model().objects.create_user(
            email="advisor@example.com", password="testpass123"
        )

    def test_create_client(self):
        client = Client.objects.create(
            advisor=self.advisor,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            tax_status="single",
            birthdate="1980-01-01",
            gender="male"
        )
        self.assertEqual(client.first_name, "John")