from django.core.management.base import BaseCommand
from django.conf import settings
import stripe


class Command(BaseCommand):
    help = 'Check for a Stripe customer by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to search for')

    def handle(self, *args, **options):
        email = options['email']
        
        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        self.stdout.write(f"Searching for Stripe customer with email: {email}")
        self.stdout.write(f"Using Stripe key: {settings.STRIPE_SECRET_KEY[:12]}...")
        
        try:
            # Search for customers with this email
            customers = stripe.Customer.list(email=email, limit=10)
            
            if not customers.data:
                self.stdout.write(
                    self.style.WARNING(f"No Stripe customers found with email: {email}")
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f"Found {len(customers.data)} customer(s):")
            )
            
            for customer in customers.data:
                self.stdout.write("\n" + "="*50)
                self.stdout.write(f"Customer ID: {customer.id}")
                self.stdout.write(f"Email: {customer.email}")
                self.stdout.write(f"Name: {customer.name}")
                self.stdout.write(f"Created: {customer.created}")
                self.stdout.write(f"Description: {customer.description}")
                
                # Get subscriptions for this customer
                try:
                    subscriptions = stripe.Subscription.list(customer=customer.id, limit=5)
                    if subscriptions.data:
                        self.stdout.write(f"\nSubscriptions ({len(subscriptions.data)}):")
                        for sub in subscriptions.data:
                            self.stdout.write(f"  - ID: {sub.id}")
                            self.stdout.write(f"    Status: {sub.status}")
                            self.stdout.write(f"    Current period: {sub.current_period_start} - {sub.current_period_end}")
                            self.stdout.write(f"    Cancel at period end: {sub.cancel_at_period_end}")
                            if sub.items.data:
                                item = sub.items.data[0]
                                price = item.price
                                self.stdout.write(f"    Plan: ${price.unit_amount/100:.2f}/{price.recurring.interval}")
                    else:
                        self.stdout.write("\nNo subscriptions found")
                except stripe.error.StripeError as e:
                    self.stdout.write(f"Error fetching subscriptions: {str(e)}")
                
                # Get recent invoices
                try:
                    invoices = stripe.Invoice.list(customer=customer.id, limit=3)
                    if invoices.data:
                        self.stdout.write(f"\nRecent invoices ({len(invoices.data)}):")
                        for invoice in invoices.data:
                            self.stdout.write(f"  - ID: {invoice.id}")
                            self.stdout.write(f"    Amount: ${invoice.amount_paid/100:.2f}")
                            self.stdout.write(f"    Status: {invoice.status}")
                            self.stdout.write(f"    Date: {invoice.created}")
                    else:
                        self.stdout.write("\nNo invoices found")
                except stripe.error.StripeError as e:
                    self.stdout.write(f"Error fetching invoices: {str(e)}")
                
        except stripe.error.StripeError as e:
            self.stdout.write(
                self.style.ERROR(f"Stripe API error: {str(e)}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error: {str(e)}")
            )