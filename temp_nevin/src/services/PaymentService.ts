
import { loadSquareSdk } from '@square/web-sdk';

const SQUARE_LOCATION_ID = process.env.SQUARE_LOCATION_ID;
const SQUARE_APP_ID = process.env.SQUARE_APP_ID;

export async function initializePayments() {
  const payments = await loadSquareSdk();
  await payments.initialize({
    applicationId: SQUARE_APP_ID,
    locationId: SQUARE_LOCATION_ID
  });
  return payments;
}

export async function createPaymentLink(description: string = 'Donación a Sistema Nevin') {
  const response = await fetch('/api/create-payment-link', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description })
  });
  
  const data = await response.json();
  return data.paymentLink;
}
