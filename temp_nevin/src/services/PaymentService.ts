
const SQUARE_PAYMENT_LINK = process.env.SQUARE_PAYMENT_LINK || 'https://square.link/u/your-link-here';

export async function createPaymentLink() {
  return SQUARE_PAYMENT_LINK;
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
