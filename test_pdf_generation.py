#!/usr/bin/env python
"""
Test script for PDF generation with actual data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.pdf_generator import ScenarioPDFGenerator
from core.models import Scenario

def test_pdf_generation():
    """Test PDF generation for a scenario"""
    try:
        # Get a test scenario
        scenario = Scenario.objects.first()
        if not scenario:
            print("No scenarios found in database")
            return
        
        print(f"Testing PDF generation for scenario: {scenario.id} - {scenario.name}")
        print(f"Client: {scenario.client.first_name} {scenario.client.last_name}")
        
        # Get a real auth token for testing
        # First, get or create a test user
        from core.models import CustomUser
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Try to get the first user or create a test user
        user = CustomUser.objects.first()
        if not user:
            user = CustomUser.objects.create_user(
                username='test_pdf_user',
                email='test@example.com',
                password='test_password'
            )
        
        # Generate JWT token for this user
        refresh = RefreshToken.for_user(user)
        auth_token = str(refresh.access_token)
        
        print(f"Using auth token for user: {user.username}")
        
        # Initialize generator
        generator = ScenarioPDFGenerator()
        
        # Generate PDF with all tabs
        tabs = ['overview', 'financial', 'socialSecurity', 'medicare']
        pdf_content = generator.generate_scenario_pdf(
            client_id=scenario.client.id,
            scenario_id=scenario.id,
            tabs=tabs,
            auth_token=auth_token  # Use real JWT token
        )
        
        # Save to file for inspection
        output_file = f"/tmp/scenario_{scenario.id}_test.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✓ PDF generated successfully!")
        print(f"✓ PDF size: {len(pdf_content):,} bytes")
        print(f"✓ PDF saved to: {output_file}")
        
        # You can open this file to verify content
        print(f"\nTo view the PDF, run:")
        print(f"  open {output_file}")
        
    except Exception as e:
        print(f"✗ Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()