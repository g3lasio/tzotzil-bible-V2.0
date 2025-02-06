
import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Card, Text, ActivityIndicator } from 'react-native-paper';
import { NevinAIService } from '../services/NevinAIService';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { ChatMessage } from '../types/nevin';

type NevinChatScreenProps = NativeStackScreenProps<any, 'NevinChat'>;

export default function NevinChatScreen({ navigation }: NevinChatScreenProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const flatListRef = useRef<FlatList>(null);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: input.trim(),
      type: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await NevinAIService.processQuery(
        userMessage.content,
        '',
        messages
      );

      if (response.success) {
        const nevinResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: response.response,
          type: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, nevinResponse]);
      } else {
        setError(response.error || 'Error procesando tu mensaje');
      }
    } catch (err) {
      setError('Error de conexión');
      console.error('Error in chat:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => (
    <Card
      style={[
        styles.messageCard,
        item.type === 'user' ? styles.userMessage : styles.nevinMessage,
      ]}
    >
      <Card.Content>
        <Text>{item.content}</Text>
      </Card.Content>
    </Card>
  );

  useEffect(() => {
    if (messages.length > 0) {
      flatListRef.current?.scrollToEnd();
    }
  }, [messages]);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View style={styles.chatContainer}>
        {error && (
          <Text style={styles.errorText}>{error}</Text>
        )}
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.messagesList}
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
