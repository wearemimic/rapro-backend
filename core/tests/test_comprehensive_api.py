"""
Test Comprehensive Financial Summary API
=========================================
Tests for the comprehensive financial summary API endpoint
Based on Phase VII of Comprehensive Financial Summary PRD
"""

import json
from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Client, Scenario, IncomeSource

User = get_user_model()


class TestComprehensiveFinancialSummaryAPI(TestCase):
    """Test suite for comprehensive financial summary API endpoint"""

    def setUp(self):
        """Set up test data"""
        # Create test user (advisor)
        self.user = User.objects.create_user(
            username='testadvisor',
            email='advisor@test.com',
            password='testpass123'
        )

        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test client
        self.test_client = Client.objects.create(
            advisor=self.user,
            first_name="Test",
            last_name="Client",
            email="client@test.com",
            birthdate=date(1959, 1, 1),
            gender="Male",
            tax_status="Single"
        )

        # Create test scenario
        self.scenario = Scenario.objects.create(
            client=self.test_client,
            name="Test Comprehensive Scenario",
            retirement_age=65,
            mortality_age=90
        )

        # Create income sources
        self.ss = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="social_security",
            income_name="Social Security",
            monthly_amount=2000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        self.qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=3000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

    def test_comprehensive_summary_endpoint_exists(self):
        """Test that the comprehensive summary endpoint exists"""
        url = f'/api/scenarios/{self.scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        # Should not be 404
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                            "Endpoint should exist")

    def test_comprehensive_summary_returns_data(self):
        """Test that the endpoint returns comprehensive data"""
        url = f'/api/scenarios/{self.scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Check top-level fields
        self.assertIn('scenario_id', data)
        self.assertIn('scenario_name', data)
        self.assertIn('client_id', data)
        self.assertIn('client_name', data)
        self.assertIn('years', data)
        self.assertIn('summary', data)

        # Verify scenario information
        self.assertEqual(data['scenario_id'], self.scenario.id)
        self.assertEqual(data['scenario_name'], self.scenario.name)
        self.assertEqual(data['client_id'], self.test_client.id)

        # Check that years array has data
        self.assertIsInstance(data['years'], list)
        self.assertGreater(len(data['years']), 0, "Should have calculation results")

        # Check summary metadata
        summary = data['summary']
        self.assertIn('total_years', summary)
        self.assertIn('start_year', summary)
        self.assertIn('end_year', summary)
        self.assertIn('start_age', summary)
        self.assertIn('end_age', summary)

    def test_comprehensive_summary_year_structure(self):
        """Test that each year has the PRD-required fields"""
        url = f'/api/scenarios/{self.scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        years = data['years']

        # Check first year structure
        first_year = years[0]

        # PRD-required fields
        required_fields = [
            # Demographics
            'year', 'primary_age',

            # Income dictionaries
            'income_by_source', 'asset_balances', 'rmd_required', 'rmd_total',

            # Tax fields
            'agi', 'magi', 'taxable_income', 'federal_tax', 'state_tax',
            'marginal_rate', 'effective_rate',

            # Medicare/IRMAA
            'irmaa_bracket_number', 'part_b', 'part_d', 'total_medicare',

            # Net income
            'gross_income_total', 'after_tax_income', 'after_medicare_income', 'remaining_income'
        ]

        for field in required_fields:
            self.assertIn(field, first_year, f"Year data missing required field: {field}")

    def test_income_by_source_has_correct_ids(self):
        """Test that income_by_source uses IncomeSource IDs as keys"""
        url = f'/api/scenarios/{self.scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        data = response.json()
        first_year = data['years'][0]

        income_by_source = first_year['income_by_source']

        # Should have our income source IDs as keys
        self.assertIn(str(self.ss.id), income_by_source,
                      f"Social Security ID {self.ss.id} should be in income_by_source")
        self.assertIn(str(self.qualified.id), income_by_source,
                      f"401k ID {self.qualified.id} should be in income_by_source")

    def test_authentication_required(self):
        """Test that authentication is required"""
        # Create unauthenticated client
        unauth_client = APIClient()

        url = f'/api/scenarios/{self.scenario.id}/comprehensive-summary/'
        response = unauth_client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         "Should require authentication")

    def test_ownership_validation(self):
        """Test that users can only access their own scenarios"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='otherpass123'
        )

        # Create client and scenario for other user
        other_client = Client.objects.create(
            advisor=other_user,
            first_name="Other",
            last_name="Client",
            email="otherclient@test.com",
            birthdate=date(1960, 1, 1)
        )

        other_scenario = Scenario.objects.create(
            client=other_client,
            name="Other Scenario",
            retirement_age=65,
            mortality_age=90
        )

        # Try to access other user's scenario
        url = f'/api/scenarios/{other_scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         "Should not allow access to other user's scenario")

    def test_nonexistent_scenario(self):
        """Test handling of nonexistent scenario"""
        url = '/api/scenarios/999999/comprehensive-summary/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Scenario not found")

    def test_error_handling(self):
        """Test that errors are properly handled and logged"""
        # Create a scenario with invalid data that might cause calculation errors
        bad_scenario = Scenario.objects.create(
            client=self.test_client,
            name="Bad Scenario",
            retirement_age=200,  # Invalid age
            mortality_age=10     # Invalid mortality age
        )

        url = f'/api/scenarios/{bad_scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        # Should handle error gracefully
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            data = response.json()
            self.assertIn('error', data)
            self.assertIn('details', data)

    def test_backward_compatibility(self):
        """Test that legacy fields are still present"""
        url = f'/api/scenarios/{self.scenario.id}/comprehensive-summary/'
        response = self.client.get(url)

        data = response.json()
        first_year = data['years'][0]

        # Check legacy fields
        legacy_fields = ['asset_incomes', 'rmd_amount', 'net_income']
        for field in legacy_fields:
            self.assertIn(field, first_year, f"Legacy field {field} should be present")


class TestAPIDocumentation(TestCase):
    """Documentation test case showing API usage examples"""

    def test_api_usage_example(self):
        """
        Example of how to use the comprehensive financial summary API

        Endpoint: GET /api/scenarios/{scenario_id}/comprehensive-summary/

        Headers:
            Authorization: Bearer {jwt_token}

        Response Structure:
        {
            "scenario_id": 123,
            "scenario_name": "Retirement Plan A",
            "client_id": 456,
            "client_name": "John Doe",
            "retirement_age": 65,
            "mortality_age": 90,
            "summary": {
                "total_years": 25,
                "start_year": 2024,
                "end_year": 2049,
                "start_age": 65,
                "end_age": 90
            },
            "years": [
                {
                    "year": 2024,
                    "primary_age": 65,
                    "income_by_source": {
                        "29": 24000,  // Social Security
                        "30": 36000   // 401k
                    },
                    "asset_balances": {
                        "30": 464000  // 401k balance after withdrawal
                    },
                    "rmd_required": {},
                    "rmd_total": 0,
                    "agi": 51000,
                    "magi": 51000,
                    "taxable_income": 36000,
                    "federal_tax": 4100,
                    "state_tax": 0,
                    "marginal_rate": 12,
                    "effective_rate": 6.8,
                    "irmaa_bracket_number": 0,
                    "part_b": 2220,
                    "part_d": 852,
                    "total_medicare": 3072,
                    "gross_income_total": 60000,
                    "after_tax_income": 55900,
                    "after_medicare_income": 52828,
                    "remaining_income": 52828
                },
                // ... more years
            ]
        }
        """
        pass  # This is documentation only


if __name__ == '__main__':
    import unittest
    unittest.main()