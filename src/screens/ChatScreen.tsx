import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Card, Title, Paragraph } from 'react-native-paper';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type ChatScreenProps = {
  navigation: NativeStackNavigationProp<any, 'Chat'>;
};

export default function ChatScreen({ navigation }: ChatScreenProps) {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{type: string, content: string}>>([]);

  const sendMessage = () => {
    if (message.trim()) {
      // Aquí implementaremos la lógica de chat con Nevin
      setChatHistory(prev => [...prev, { type: 'user', content: message }]);
      setMessage('');
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.chatContainer}>
        {chatHistory.map((msg, index) => (
          <Card 
            key={index} 
            style={[
              styles.messageCard,
              msg.type === 'user' ? styles.userMessage : styles.nevinMessage
            ]}
          >
            <Card.Content>
              <Paragraph>{msg.content}</Paragraph>
            </Card.Content>
          </Card>
        ))}
      </ScrollView>
      
      <View style={styles.inputContainer}>
        <TextInput
          value={message}
          onChangeText={setMessage}
          placeholder="Escribe tu mensaje..."
          style={styles.input}
        />
        <Button 
          mode="contained" 
          onPress={sendMessage}
          disabled={!message.trim()}
        >
          Enviar
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  chatContainer: {
    flex: 1,
    padding: 16,
  },
  messageCard: {
    marginVertical: 8,
  },
  userMessage: {
    backgroundColor: '#e3f2fd',
    marginLeft: 40,
  },
  nevinMessage: {
    backgroundColor: '#f5f5f5',
    marginRight: 40,
  },
  inputContainer: {
    padding: 16,
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    marginRight: 8,
  },
});
