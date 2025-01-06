import React from 'react';
import { Modal, Portal, Button, Text, Surface } from 'react-native-paper';
import { View, StyleSheet, ScrollView } from 'react-native';
import * as InAppPurchases from 'expo-in-app-purchases';

interface DonationModalProps {
  visible: boolean;
  onDismiss: () => void;
  onDonationComplete: () => void;
}

const DONATION_ITEMS = [
  { amount: '5.00', sku: 'donation_5' },
  { amount: '10.00', sku: 'donation_10' },
  { amount: '20.00', sku: 'donation_20' },
];

export default function DonationModal({ visible, onDismiss, onDonationComplete }: DonationModalProps) {
  const handleDonation = async (sku: string) => {
    try {
      // Conectar con el servicio de pagos
      await InAppPurchases.connectAsync();
      
      // Obtener productos disponibles
      const { responseCode, results } = await InAppPurchases.getProductsAsync([sku]);
      
      if (responseCode === InAppPurchases.IAPResponseCode.OK && results.length > 0) {
        // Iniciar la compra
        await InAppPurchases.purchaseItemAsync(sku);
        
        // Escuchar el evento de compra completada
        InAppPurchases.setPurchaseListener(({ responseCode, results }) => {
          if (responseCode === InAppPurchases.IAPResponseCode.OK) {
            onDonationComplete();
          }
        });
      }
    } catch (error) {
      console.error('Error procesando donación:', error);
    }
  };

  return (
    <Portal>
      <Modal visible={visible} onDismiss={onDismiss} contentContainerStyle={styles.container}>
        <Surface style={styles.surface}>
          <Text style={styles.title}>Apoya Nuestro Ministerio</Text>
          <Text style={styles.description}>
            Tu donación nos ayuda a continuar compartiendo la Palabra de Dios en español y tzotzil.
          </Text>
          
          <ScrollView style={styles.optionsContainer}>
            {DONATION_ITEMS.map((item) => (
              <Button
                key={item.sku}
                mode="contained"
                onPress={() => handleDonation(item.sku)}
                style={styles.donationButton}
              >
                Donar ${item.amount} USD
              </Button>
            ))}
          </ScrollView>
          
          <Button onPress={onDismiss} style={styles.cancelButton}>
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
  },
  surface: {
    padding: 20,
    borderRadius: 10,
    backgroundColor: 'white',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: '#666',
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
