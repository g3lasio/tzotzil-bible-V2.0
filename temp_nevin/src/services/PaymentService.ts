
import { Platform } from 'react-native';
import { Linking } from 'react-native';

const SQUARE_PAYMENT_LINK = 'https://square.link/u/ZbdMAkZv';

export interface PaymentResponse {
  paymentUrl: string;
  amount: number;
}

export class PaymentService {
  static async createPaymentLink(): Promise<string> {
    return SQUARE_PAYMENT_LINK;
  }
  
  static async processPayment(amount: number): Promise<void> {
    try {
      const paymentUrl = await this.createPaymentLink();
      
      if (Platform.OS === 'web') {
        window.open(paymentUrl, '_blank');
      } else {
        await Linking.openURL(paymentUrl);
      }
    } catch (error) {
      console.error('Error processing payment:', error);
      throw new Error('Failed to process payment');
    }
  }
}
