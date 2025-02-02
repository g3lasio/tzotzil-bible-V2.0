import React from 'react';
import { Modal, Portal, Button, Text, Surface } from 'react-native-paper';
import { View, StyleSheet } from 'react-native';
import { createPaymentLink } from '../services/PaymentService';

interface DonationModalProps {
  visible: boolean;
  onDismiss: () => void;
  onDonationComplete: () => void;
}

export default function DonationModal({ visible, onDismiss, onDonationComplete }: DonationModalProps) {
  const handleDonation = async () => {
    try {
      const paymentLink = await createPaymentLink();
      window.open(paymentLink, '_blank');
      onDonationComplete();
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

          <Text style={styles.description}>
            Tu donación nos ayuda a seguir compartiendo la Palabra de Dios
          </Text>

          <Button
            mode="contained"
            onPress={handleDonation}
            style={styles.donationButton}
          >
            Donar con Square
          </Button>

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
  description: {
    textAlign: 'center',
    marginBottom: 20,
    color: '#666',
  },
  donationButton: {
    marginVertical: 8,
    backgroundColor: '#006aff',
  },
  cancelButton: {
    marginTop: 16,
  },
});