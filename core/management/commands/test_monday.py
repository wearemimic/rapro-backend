from django.core.management.base import BaseCommand
import os
import requests
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Test Monday.com integration by adding a test pulse'

    def handle(self, *args, **options):
        # Get credentials from environment
        api_token = os.environ.get('MONDAY_API_TOKEN')
        board_id = os.environ.get('MONDAY_BOARD_ID')
        api_url = os.environ.get('MONDAY_API_URL', 'https://api.monday.com/v2')
        
        if not api_token or not board_id:
            self.stdout.write(self.style.ERROR('Missing Monday.com credentials in environment variables'))
            return
        
        self.stdout.write(f'Connecting to Monday.com board: {board_id}')
        
        # Headers for Monday.com API
        headers = {
            'Authorization': api_token,
            'Content-Type': 'application/json',
            'API-Version': '2023-10'
        }
        
        # Create a test item
        item_name = f"Test Item from RetirementAdvisorPro - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        query = '''
        mutation ($boardId: ID!, $itemName: String!) {
            create_item (
                board_id: $boardId,
                item_name: $itemName
            ) {
                id
                name
            }
        }
        '''
        
        variables = {
            'boardId': board_id,
            'itemName': item_name
        }
        
        data = {
            'query': query,
            'variables': variables
        }
        
        try:
            # Make the API request
            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if 'errors' in result:
                self.stdout.write(self.style.ERROR(f'Monday.com API errors: {result["errors"]}'))
                return
            
            if 'data' in result and result['data'].get('create_item'):
                item = result['data']['create_item']
                self.stdout.write(self.style.SUCCESS(f'✅ Successfully created test item!'))
                self.stdout.write(f'   Item ID: {item["id"]}')
                self.stdout.write(f'   Item Name: {item["name"]}')
            else:
                self.stdout.write(self.style.WARNING('Unexpected response format:'))
                self.stdout.write(json.dumps(result, indent=2))
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Request failed: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {e}'))