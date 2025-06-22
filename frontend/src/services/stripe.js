import { loadStripe } from '@stripe/stripe-js';

let stripePromise;
const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);
  }
  return stripePromise;
};

export const createSubscription = async (customerId, priceId) => {
  try {
    const response = await fetch('/api/create-subscription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customerId,
        priceId,
      }),
    });
    return await response.json();
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};

export const createPaymentMethod = async (cardElement) => {
  try {
    const stripe = await getStripe();
    const { paymentMethod, error } = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
    });

    if (error) {
      throw error;
    }

    return paymentMethod;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};

export default {
  getStripe,
  createSubscription,
  createPaymentMethod,
}; 