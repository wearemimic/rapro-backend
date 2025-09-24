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

    def test_create_scenario_with_all_income_types(self):
        scenario = Scenario.objects.create(
            client=self.client,
            name="All Income Types",
            retirement_age=65,
            medicare_age=65,
            mortality_age=90
        )

        income_types = [
            "social_security",
            "Roth_IRA",
            "Traditional_IRA",
            "Roth_401k",
            "Traditional_401k",
            "Other"
        ]

        for income_type in income_types:
            scenario.incomes.create(
                income_type=income_type,
                income_name=income_type.replace("_", " "),
                owned_by="primary",
                start_age=65,
                end_age=90,
                current_balance=100000,
                monthly_contribution=1000,
                growth_rate=5,
                withdrawal_amount=1500,
                amount_at_fra=3000 if income_type == "social_security" else None,
                cola=2 if income_type == "social_security" else 0,
                tax_rate=15
            )

        self.assertEqual(scenario.incomes.count(), 6)
        self.assertEqual(
            set(s.income_type for s in scenario.incomes.all()),
            set(income_types)
        )