
import React from 'react';
import { Modal, Portal, Button, Text, Surface, List } from 'react-native-paper';
import { View, StyleSheet, Platform } from 'react-native';
import { PaymentService } from '../services/PaymentService';

interface DonationModalProps {
  visible: boolean;
  onDismiss: () => void;
  onDonationComplete: () => void;
}

const DONATION_AMOUNTS = [5, 10, 20];

export default function DonationModal({ visible, onDismiss, onDonationComplete }: DonationModalProps) {
  const handleDonation = async (amount?: number) => {
    try {
      await PaymentService.processPayment(amount || 0);
      onDonationComplete();
    } catch (error) {
      console.error('Error procesando donación:', error);
      Alert.alert(
        'Error',
        'Hubo un problema procesando tu donación. Por favor intenta nuevamente.'
      );
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

          {DONATION_AMOUNTS.map((amount) => (
            <Button
              key={amount}
              mode="contained"
              onPress={() => handleDonation(amount)}
              style={styles.donationButton}
            >
              Donar ${amount}
            </Button>
          ))}

          <Button
            mode="contained"
            onPress={() => handleDonation()}
            style={styles.donationButton}
          >
            Otra Cantidad
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
