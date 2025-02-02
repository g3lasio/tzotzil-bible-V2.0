
import { api } from './api';

const SQUARE_PAYMENT_LINK = 'https://square.link/u/ZbdMAkZv';

export interface PaymentResponse {
  paymentUrl: string;
  amount: number;
}

export class PaymentService {
  static async createPaymentLink(description: string = 'Donación a Sistema Nevin'): Promise<string> {
    return SQUARE_PAYMENT_LINK;
  }
  
  static async processPayment(amount: number): Promise<void> {
    try {
      const paymentUrl = await this.createPaymentLink();
      if (typeof window !== 'undefined') {
        window.open(paymentUrl, '_blank');
      }
    } catch (error) {
      console.error('Error processing payment:', error);
      throw error;
    }
  }
}
