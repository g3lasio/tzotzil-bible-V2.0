import React, { useState, useRef } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, Card, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { api } from '../services/api';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export default function NevinScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const [showDonationModal, setShowDonationModal] = useState(false);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await api.post('/nevin/chat', {
        message: newUserMessage.content,
        conversation_history: messages.map(msg => ({
          role: msg.isUser ? 'user' : 'assistant',
          content: msg.content,
        })),
      });

      const nevinResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, nevinResponse]);

      // Scroll al último mensaje
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoid}
      >
        <Text variant="headlineMedium" style={styles.title}>
          Nevin AI
        </Text>

        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
        >
          {messages.map((message) => (
            <Card
              key={message.id}
              style={[
                styles.messageCard,
                message.isUser ? styles.userMessage : styles.nevinMessage,
              ]}
            >
              <Card.Content>
                <Text>{message.content}</Text>
              </Card.Content>
            </Card>
          ))}
        </ScrollView>

        <View style={styles.inputContainer}>
          <TextInput
            value={inputMessage}
            onChangeText={setInputMessage}
            placeholder="Escribe tu mensaje..."
            mode="outlined"
            multiline
            style={styles.input}
            disabled={loading}
            right={
              <TextInput.Icon
                icon="send"
                onPress={handleSendMessage}
                disabled={loading || !inputMessage.trim()}
              />
            }
          />
          <Button style={styles.donateButton} onPress={() => setShowDonationModal(true)}>Donate</Button>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoid: {
    flex: 1,
  },
  title: {
    textAlign: 'center',
    padding: 20,
  },
  messagesContainer: {
    flex: 1,
    padding: 10,
  },
  messagesContent: {
    paddingBottom: 20,
  },
  messageCard: {
    marginVertical: 5,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#e3f2fd',
  },
  nevinMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f5f5f5',
  },
  inputContainer: {
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  input: {
    maxHeight: 100,
  },
  donateButton: {
    margin: 16,
    backgroundColor: '#4caf50',
  },
});