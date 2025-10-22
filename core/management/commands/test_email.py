from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send a test email to verify SMTP configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            default=settings.ADMIN_EMAIL,
            help='Email address to send test email to'
        )

    def handle(self, *args, **options):
        to_email = options['to']

        try:
            self.stdout.write(f'Attempting to send test email to {to_email}...')
            self.stdout.write(f'Using EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
            self.stdout.write(f'Using EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Not set")}')
            self.stdout.write(f'Using FROM: {settings.DEFAULT_FROM_EMAIL}')

            subject = 'RAPRO Test Email - SMTP Configuration'
            message = '''This is a test email from Retirement Advisor Pro.

If you received this email, your AWS SES SMTP configuration is working correctly!

Configuration details:
- Environment: {env}
- Email Backend: {backend}
- From Address: {from_addr}

This email was sent using Django's send_mail() function.
'''.format(
                env=settings.ENVIRONMENT,
                backend=settings.EMAIL_BACKEND,
                from_addr=settings.DEFAULT_FROM_EMAIL
            )

            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )

            if result == 1:
                self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {to_email}'))
                self.stdout.write(self.style.SUCCESS('AWS SES SMTP is configured correctly!'))
            else:
                self.stdout.write(self.style.WARNING(f'send_mail returned {result}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {str(e)}'))
            raise
