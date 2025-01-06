import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Card, Text, ActivityIndicator } from 'react-native-paper';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BIBLE_API_URL } from '@env';

type Message = {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
};

type NevinChatScreenProps = NativeStackScreenProps<any, 'NevinChat'>;

export default function NevinChatScreen({ navigation }: NevinChatScreenProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${BIBLE_API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
        }),
      });

      if (!response.ok) {
        throw new Error('Error al procesar el mensaje');
      }

      const data = await response.json();
      const nevinResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, nevinResponse]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <Card
      style={[
        styles.messageCard,
        item.isUser ? styles.userMessage : styles.nevinMessage,
      ]}
    >
      <Card.Content>
        <Text>{item.content}</Text>
      </Card.Content>
    </Card>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 100 : 0}
    >
      <View style={styles.chatContainer}>
        {error && (
          <Text style={styles.errorText}>{error}</Text>
        )}
        <FlatList
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.messagesList}
          inverted={false}
        />
      </View>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Escribe tu mensaje..."
          disabled={loading}
          multiline
        />
        <Button
          mode="contained"
          onPress={sendMessage}
          loading={loading}
          disabled={loading || !input.trim()}
          style={styles.sendButton}
        >
          Enviar
        </Button>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  chatContainer: {
    flex: 1,
    padding: 10,
  },
  messagesList: {
    paddingBottom: 10,
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
    backgroundColor: '#fff',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  input: {
    flex: 1,
    marginRight: 10,
    backgroundColor: '#fff',
  },
  sendButton: {
    justifyContent: 'center',
  },
  errorText: {
    color: 'red',
    textAlign: 'center',
    marginVertical: 10,
  },
});
