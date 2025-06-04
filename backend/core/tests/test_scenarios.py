from django.test import TestCase
from core.models import Client, Scenario
from django.contrib.auth import get_user_model

class ScenarioModelTest(TestCase):
    def setUp(self):
        self.advisor = get_user_model().objects.create_user(
            email="advisor@example.com", password="testpass123"
        )
        self.client = Client.objects.create(
            advisor=self.advisor,
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            tax_status="single",
            birthdate="1980-01-01",
            gender="female"
        )

    def test_create_scenario(self):
        scenario = Scenario.objects.create(
            client=self.client,
            name="Base Case",
            retirement_age=65,
            medicare_age=65,
            mortality_age=90
        )
        self.assertEqual(scenario.name, "Base Case")