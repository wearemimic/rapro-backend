"""
Django management command for GDPR-compliant user data deletion

Usage:
    python manage.py gdpr_user_delete <user_id> [--anonymize]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import CustomUser
from core.pii_protection import SecureDataDeletion
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Securely delete or anonymize user data for GDPR compliance'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            type=int,
            help='ID of the user to delete'
        )
        parser.add_argument(
            '--anonymize',
            action='store_true',
            help='Anonymize data instead of deleting (keeps records for audit)'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        anonymize = options.get('anonymize', False)
        confirm = options.get('confirm', False)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise CommandError(f'User with ID {user_id} does not exist')

        # Show user information
        self.stdout.write(f"\nUser Information:")
        self.stdout.write(f"  ID: {user.id}")
        self.stdout.write(f"  Email: {user.email}")
        self.stdout.write(f"  Name: {user.first_name} {user.last_name}")
        self.stdout.write(f"  Joined: {user.date_joined}")

        # Get confirmation
        if not confirm:
            action = "anonymize" if anonymize else "permanently delete"
            response = input(f"\nAre you sure you want to {action} this user? (yes/no): ")
            if response.lower() != 'yes':
                self.stdout.write(self.style.WARNING("Operation cancelled"))
                return

        try:
            with transaction.atomic():
                if anonymize:
                    # Anonymize user data
                    SecureDataDeletion.anonymize_user_data(user_id)
                    self.stdout.write(
                        self.style.SUCCESS(f"User {user_id} data has been anonymized")
                    )
                    logger.info(f"GDPR: User {user_id} data anonymized by management command")
                else:
                    # Securely delete user
                    SecureDataDeletion.secure_delete_model(
                        user,
                        overwrite_fields=['email', 'first_name', 'last_name']
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"User {user_id} has been securely deleted")
                    )
                    logger.info(f"GDPR: User {user_id} securely deleted by management command")

        except Exception as e:
            raise CommandError(f"Failed to process user deletion: {str(e)}")