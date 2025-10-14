"""
Stripe-related API views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .stripe_utils import (
    get_subscription_prices,
    get_products_with_prices,
    get_price_details
)
import stripe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['GET'])
@permission_classes([AllowAny])
def get_subscription_plans(request):
    """
    Get available subscription plans dynamically from Stripe
    This endpoint can be called by the frontend to display pricing options
    """
    try:
        # Get all products with prices
        products = get_products_with_prices()
        
        # Get subscription price IDs
        subscription_prices = get_subscription_prices()
        
        # Format response for frontend
        plans = []
        
        # Look for subscription product
        for product in products:
            # Check if this is a subscription product
            is_subscription = False
            for price in product.get("prices", []):
                if price.get("recurring"):
                    is_subscription = True
                    break
            
            if is_subscription:
                # Format prices for this product
                monthly_price = None
                annual_price = None
                
                for price in product["prices"]:
                    if not price.get("recurring"):
                        continue
                    
                    interval = price["recurring"]["interval"]
                    if interval == "month" and not monthly_price:
                        monthly_price = {
                            "id": price["id"],
                            "amount": price["unit_amount"],
                            "currency": price["currency"],
                            "interval": "monthly"
                        }
                    elif interval == "year" and not annual_price:
                        annual_price = {
                            "id": price["id"],
                            "amount": price["unit_amount"],
                            "currency": price["currency"],
                            "interval": "annual"
                        }
                
                if monthly_price or annual_price:
                    plans.append({
                        "product_id": product["id"],
                        "name": product["name"],
                        "description": product.get("description", ""),
                        "monthly": monthly_price,
                        "annual": annual_price
                    })
        
        # If no plans found, use fallback from settings
        if not plans and (subscription_prices["monthly"] or subscription_prices["annual"]):
            fallback_plan = {
                "product_id": "default",
                "name": "RetirementAdvisorPro Subscription",
                "description": "Full access to all features",
                "monthly": None,
                "annual": None
            }
            
            if subscription_prices["monthly"]:
                details = get_price_details(subscription_prices["monthly"])
                if details:
                    fallback_plan["monthly"] = {
                        "id": details["id"],
                        "amount": details["unit_amount"],
                        "currency": details["currency"],
                        "interval": "monthly"
                    }
            
            if subscription_prices["annual"]:
                details = get_price_details(subscription_prices["annual"])
                if details:
                    fallback_plan["annual"] = {
                        "id": details["id"],
                        "amount": details["unit_amount"],
                        "currency": details["currency"],
                        "interval": "annual"
                    }
            
            if fallback_plan["monthly"] or fallback_plan["annual"]:
                plans.append(fallback_plan)
        
        return Response({
            "success": True,
            "plans": plans,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY
        })
        
    except Exception as e:
        logger.error(f"Failed to get subscription plans: {e}")
        return Response({
            "success": False,
            "message": "Failed to retrieve subscription plans",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_coupon_dynamic(request):
    """
    Validate a coupon code with dynamic price retrieval
    """
    try:
        coupon_code = request.data.get('coupon_code', '').strip()
        plan_type = request.data.get('plan', 'monthly')  # 'monthly' or 'annual'
        
        if not coupon_code:
            return Response({
                'valid': False,
                'message': 'Coupon code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get dynamic price IDs
        subscription_prices = get_subscription_prices()
        price_id = subscription_prices.get(plan_type)
        
        if not price_id:
            return Response({
                'valid': False,
                'message': f'No {plan_type} plan available'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get price details
        price_details = get_price_details(price_id)
        if not price_details:
            return Response({
                'valid': False,
                'message': 'Invalid price configuration'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the coupon
        try:
            # First try to retrieve by ID
            try:
                coupon = stripe.Coupon.retrieve(coupon_code)
                logger.info(f"Coupon found by ID: {coupon.id}")
            except stripe.StripeError:
                # If not found by ID, search by name (case-insensitive)
                logger.info(f"Coupon not found by ID, searching by name...")
                all_coupons = stripe.Coupon.list(limit=100)
                coupon = None
                for c in all_coupons.auto_paging_iter():
                    if c.name and c.name.upper() == coupon_code.upper():
                        coupon = c
                        logger.info(f"Coupon found by name: {c.id} (name: {c.name})")
                        break

                if not coupon:
                    # Also check promotion codes
                    logger.info(f"Checking promotion codes...")
                    promo_codes = stripe.PromotionCode.list(code=coupon_code, active=True, limit=1)
                    if promo_codes.data:
                        coupon = stripe.Coupon.retrieve(promo_codes.data[0].coupon.id)
                        logger.info(f"Coupon found via promotion code: {coupon.id}")
                    else:
                        raise stripe.StripeError(f"No coupon or promotion code found for: {coupon_code}")

            if not coupon.valid:
                return Response({
                    'valid': False,
                    'message': 'This coupon is no longer valid'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if coupon is restricted to specific products/prices
            # First check the applies_to field (if available from Stripe API)
            applies_to_products = []
            if hasattr(coupon, 'applies_to') and coupon.applies_to:
                applies_to_products = coupon.applies_to.get('products', [])

            # If applies_to is not available, check metadata for product restrictions
            # This is a workaround since Stripe API doesn't always return applies_to field
            if not applies_to_products and coupon.metadata:
                metadata_products = coupon.metadata.get('applies_to_products', '')
                if metadata_products:
                    # Support comma-separated list of product IDs in metadata
                    applies_to_products = [p.strip() for p in metadata_products.split(',')]

            # If coupon is restricted to specific products, verify the current price's product is in the list
            if applies_to_products:
                product_info = price_details.get("product")
                # Extract product ID from dict if necessary
                if isinstance(product_info, dict):
                    product_id = product_info.get("id")
                else:
                    product_id = product_info

                if product_id not in applies_to_products:
                    logger.info(f"Coupon {coupon.id} does not apply to product {product_id}. Applies to: {applies_to_products}")
                    return Response({
                        'valid': False,
                        'message': f'This coupon is not valid for the {plan_type} plan'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate discount
            original_price = price_details["unit_amount"] / 100  # Convert from cents
            
            if coupon.percent_off:
                discount_amount = original_price * (coupon.percent_off / 100)
                discounted_price = original_price - discount_amount
                discount_type = 'percentage'
                discount_value = coupon.percent_off
            elif coupon.amount_off:
                discount_amount = coupon.amount_off / 100
                discounted_price = max(0, original_price - discount_amount)
                discount_type = 'fixed'
                discount_value = coupon.amount_off / 100
            else:
                discount_amount = 0
                discounted_price = original_price
                discount_type = 'none'
                discount_value = 0
            
            return Response({
                'valid': True,
                'coupon_id': coupon.id,
                'name': coupon.name or f'Coupon {coupon.id}',
                'description': f'Save {coupon.percent_off}%' if coupon.percent_off else f'Save ${coupon.amount_off/100}',
                'discount_type': discount_type,
                'discount_value': discount_value,
                'original_price': original_price,
                'discounted_price': discounted_price,
                'currency': price_details["currency"],
                'duration': coupon.duration,
                'duration_in_months': getattr(coupon, 'duration_in_months', None)
            })
            
        except stripe.InvalidRequestError:
            # Coupon doesn't exist
            return Response({
                'valid': False,
                'message': 'Invalid coupon code'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Coupon validation error: {e}")
        return Response({
            'valid': False,
            'message': 'Unable to validate coupon. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)