
import React, { useState, useEffect } from 'react';
import { Modal, Portal, Button, Text, Surface } from 'react-native-paper';
import { View, StyleSheet, ScrollView } from 'react-native';
import { loadSquareSdk } from '../services/PaymentService';

interface DonationModalProps {
  visible: boolean;
  onDismiss: () => void;
  onDonationComplete: () => void;
}

const DONATION_ITEMS = [
  { amount: '5.00', id: 'donation_5' },
  { amount: '10.00', id: 'donation_10' },
  { amount: '20.00', id: 'donation_20' },
] as const;

export default function DonationModal({ visible, onDismiss, onDonationComplete }: DonationModalProps) {
  const [card, setCard] = useState(null);

  useEffect(() => {
    if (visible) {
      initializeSquare();
    }
  }, [visible]);

  const initializeSquare = async () => {
    const payments = await loadSquareSdk();
    const card = await payments.card();
    await card.attach('#card-container');
    setCard(card);
  };

  const handleDonation = async () => {
    try {
      const paymentLink = await createPaymentLink();
      window.open(paymentLink, '_blank');
      onDonationComplete();
    }
    } catch (error) {
      console.error('Error procesando donación:', error);
    }
  };

  return (
    <Portal>
      <Modal visible={visible} onDismiss={onDismiss} contentContainerStyle={styles.container}>
        <Surface style={styles.surface}>
          <Text variant="headlineMedium" style={styles.title}>
            Apoya Nuestro Ministerio
          </Text>
          
          <View id="card-container" style={styles.cardContainer} />
          
          <ScrollView style={styles.optionsContainer}>
            {DONATION_ITEMS.map((item) => (
              <Button
                key={item.id}
                mode="contained"
                onPress={() => handleDonation(item.amount)}
                style={styles.donationButton}
              >
                Donar ${item.amount} USD
              </Button>
            ))}
          </ScrollView>

          <Button mode="text" onPress={onDismiss} style={styles.cancelButton}>
            Cancelar
          </Button>
        </Surface>
      </Modal>
    </Portal>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    margin: 20,
  },
  surface: {
    padding: 20,
    borderRadius: 10,
    backgroundColor: 'white',
  },
  title: {
    textAlign: 'center',
    marginBottom: 20,
  },
  cardContainer: {
    minHeight: 100,
    marginBottom: 20,
  },
  optionsContainer: {
    maxHeight: 200,
  },
  donationButton: {
    marginVertical: 8,
  },
  cancelButton: {
    marginTop: 16,
  },
});
