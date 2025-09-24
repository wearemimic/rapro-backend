"""
Stripe utility functions for dynamic price and product management
"""
import stripe
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def get_active_prices(product_id: Optional[str] = None) -> List[Dict]:
    """
    Fetch all active prices from Stripe, optionally filtered by product
    Results are cached for 1 hour to reduce API calls
    """
    cache_key = f"stripe_prices_{product_id or 'all'}"
    cached_prices = cache.get(cache_key)
    
    if cached_prices:
        return cached_prices
    
    try:
        # Fetch prices from Stripe
        params = {"active": True, "limit": 100}
        if product_id:
            params["product"] = product_id
        
        prices = stripe.Price.list(**params)
        
        # Format price data
        formatted_prices = []
        for price in prices.data:
            formatted_prices.append({
                "id": price.id,
                "product_id": price.product,
                "unit_amount": price.unit_amount,
                "currency": price.currency,
                "recurring": {
                    "interval": price.recurring.interval if price.recurring else None,
                    "interval_count": price.recurring.interval_count if price.recurring else None
                } if price.recurring else None,
                "nickname": price.nickname,
                "active": price.active,
                "type": price.type
            })
        
        # Cache for 1 hour
        cache.set(cache_key, formatted_prices, 3600)
        return formatted_prices
        
    except stripe.error.StripeError as e:
        logger.error(f"Failed to fetch Stripe prices: {e}")
        return []


def get_subscription_prices() -> Dict[str, Optional[str]]:
    """
    Get monthly and annual subscription price IDs dynamically from Stripe
    This looks for prices with specific nicknames or intervals
    """
    cache_key = "stripe_subscription_prices"
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    prices = get_active_prices()
    
    monthly_price = None
    annual_price = None
    
    for price in prices:
        if not price.get("recurring"):
            continue
            
        # Check by nickname first (most reliable if set)
        nickname = (price.get("nickname") or "").lower()
        if "monthly" in nickname and not monthly_price:
            monthly_price = price["id"]
        elif "annual" in nickname or "yearly" in nickname and not annual_price:
            annual_price = price["id"]
        
        # Fallback to interval checking
        elif price["recurring"]["interval"] == "month" and not monthly_price:
            monthly_price = price["id"]
        elif price["recurring"]["interval"] == "year" and not annual_price:
            annual_price = price["id"]
    
    # If we still don't have prices, use the configured ones as fallback
    result = {
        "monthly": monthly_price or settings.STRIPE_MONTHLY_PRICE_ID,
        "annual": annual_price or settings.STRIPE_ANNUAL_PRICE_ID
    }
    
    # Cache for 1 hour
    cache.set(cache_key, result, 3600)
    return result


def get_products_with_prices() -> List[Dict]:
    """
    Get all active products with their associated prices
    Useful for displaying pricing options dynamically
    """
    cache_key = "stripe_products_with_prices"
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    try:
        # Fetch all active products
        products = stripe.Product.list(active=True, limit=100)
        
        result = []
        for product in products.data:
            # Get prices for this product
            prices = get_active_prices(product.id)
            
            if prices:  # Only include products with prices
                result.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "metadata": product.metadata,
                    "prices": prices
                })
        
        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        return result
        
    except stripe.error.StripeError as e:
        logger.error(f"Failed to fetch Stripe products: {e}")
        return []


def validate_price_id(price_id: str) -> bool:
    """
    Validate if a price ID exists and is active in Stripe
    """
    try:
        price = stripe.Price.retrieve(price_id)
        return price.active
    except stripe.error.StripeError:
        return False


def get_price_details(price_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific price
    """
    cache_key = f"stripe_price_details_{price_id}"
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    try:
        price = stripe.Price.retrieve(price_id, expand=["product"])
        
        result = {
            "id": price.id,
            "unit_amount": price.unit_amount,
            "currency": price.currency,
            "nickname": price.nickname,
            "recurring": {
                "interval": price.recurring.interval,
                "interval_count": price.recurring.interval_count
            } if price.recurring else None,
            "product": {
                "id": price.product.id,
                "name": price.product.name,
                "description": price.product.description
            } if hasattr(price.product, 'id') else None
        }
        
        # Cache for 1 hour
        cache.set(cache_key, result, 3600)
        return result
        
    except stripe.error.StripeError as e:
        logger.error(f"Failed to fetch price details for {price_id}: {e}")
        return None


def clear_stripe_cache():
    """
    Clear all Stripe-related cache entries
    Call this when prices or products are updated
    """
    cache_keys = [
        "stripe_subscription_prices",
        "stripe_products_with_prices"
    ]
    
    # Also clear individual price caches
    for key in cache.keys("stripe_price*"):
        cache.delete(key)
    
    for key in cache_keys:
        cache.delete(key)
    
    logger.info("Stripe cache cleared")