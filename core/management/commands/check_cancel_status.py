from django.core.management.base import BaseCommand
from django.conf import settings
import stripe
from datetime import datetime


class Command(BaseCommand):
    help = 'Check cancel_at_period_end status for a Stripe customer'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to search for')

    def handle(self, *args, **options):
        email = options['email']
        
        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        self.stdout.write(f"Checking cancel status for: {email}")
        
        try:
            # Search for customers with this email
            customers = stripe.Customer.list(email=email, limit=10)
            
            if not customers.data:
                self.stdout.write(
                    self.style.WARNING(f"No Stripe customers found with email: {email}")
                )
                return
            
            for customer in customers.data:
                self.stdout.write(f"\nCustomer ID: {customer.id}")
                self.stdout.write(f"Email: {customer.email}")
                
                # Get subscriptions for this customer
                try:
                    subscriptions = stripe.Subscription.list(customer=customer.id, limit=5)
                    if subscriptions.data:
                        self.stdout.write(f"\nSubscriptions ({len(subscriptions.data)}):")
                        for sub in subscriptions.data:
                            self.stdout.write(f"\n--- Subscription Details ---")
                            self.stdout.write(f"ID: {sub.id}")
                            self.stdout.write(f"Status: {sub.status}")
                            self.stdout.write(f"Cancel at period end: {sub.cancel_at_period_end}")
                            self.stdout.write(f"Current period start: {datetime.fromtimestamp(sub.current_period_start)}")
                            self.stdout.write(f"Current period end: {datetime.fromtimestamp(sub.current_period_end)}")
                            self.stdout.write(f"Canceled at: {sub.canceled_at}")
                            
                            # Determine effective status
                            effective_status = sub.status
                            if sub.status == 'active' and sub.cancel_at_period_end:
                                effective_status = 'canceled_pending'
                            
                            self.stdout.write(f"Effective status: {effective_status}")
                            
                            if sub.items.data:
                                item = sub.items.data[0]
                                price = item.price
                                self.stdout.write(f"Plan: ${price.unit_amount/100:.2f}/{price.recurring.interval}")
                    else:
                        self.stdout.write("\nNo subscriptions found")
                except stripe.error.StripeError as e:
                    self.stdout.write(f"Error fetching subscriptions: {str(e)}")
                
        except stripe.error.StripeError as e:
            self.stdout.write(
                self.style.ERROR(f"Stripe API error: {str(e)}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error: {str(e)}")
            )