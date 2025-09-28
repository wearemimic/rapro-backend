from django.core.management.base import BaseCommand
from ltc_planning.services.data_loader import CostDataLoader


class Command(BaseCommand):
    help = 'Validate LTC cost data CSV files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Validating LTC cost data files...'))
        self.stdout.write('')

        loader = CostDataLoader()
        results = loader.validate_data_files()

        if results['valid']:
            self.stdout.write(self.style.SUCCESS('✓ All data files are valid!'))
        else:
            self.stdout.write(self.style.ERROR('✗ Validation failed!'))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Statistics:'))
        for key, value in results['stats'].items():
            self.stdout.write(f"  - {key}: {value}")

        if results['errors']:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Errors:'))
            for error in results['errors']:
                self.stdout.write(self.style.ERROR(f"  ✗ {error}"))

        if results['warnings']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Warnings:'))
            for warning in results['warnings']:
                self.stdout.write(self.style.WARNING(f"  ⚠ {warning}"))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Available Care Types:'))
        try:
            care_types = loader.get_available_care_types()
            for care_type in care_types:
                self.stdout.write(f"  - {care_type}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error loading care types: {str(e)}"))

        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Sample Regional Costs:'))
        try:
            sample_states = ['CA', 'NY', 'TX', 'FL', 'MS']
            states_info = {s['state_code']: s for s in loader.get_available_states()}

            for state_code in sample_states:
                if state_code in states_info:
                    info = states_info[state_code]
                    self.stdout.write(
                        f"  - {info['state']} ({state_code}): "
                        f"{info['multiplier']}x (Region: {info['region']})"
                    )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error loading regional data: {str(e)}"))

        if results['valid']:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Data validation complete!'))
            return 0
        else:
            return 1