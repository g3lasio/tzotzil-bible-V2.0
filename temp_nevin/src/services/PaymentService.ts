
import { payments } from '@square/web-sdk';

const SQUARE_APP_ID = process.env.SQUARE_APP_ID || 'your_square_app_id';

export const loadSquareSdk = async () => {
  await payments.initialize(SQUARE_APP_ID);
  return payments;
};
