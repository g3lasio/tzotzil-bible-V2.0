import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  Portal,
  Modal,
  ActivityIndicator,
  useTheme,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { nevinService } from '../services/NevinService';
import { ChatMessage } from '../types/nevin';
import { VerseBox } from '../components/VerseBox';
import { QuoteBox } from '../components/QuoteBox';
import HTML from 'react-native-render-html';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const NevinChatScreen = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const theme = useTheme();

  const parseNevinResponse = (htmlContent: string) => {
    // Implementar el parser de HTML para convertir el formato de Nevin a componentes nativos
    return htmlContent;
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const newUserMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputText,
      type: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const context = messages
        .map(msg => `${msg.type === 'user' ? 'Usuario' : 'Nevin'}: ${msg.content}`)
        .join('\n');

      const response = await nevinService.getAIResponse(inputText, context);

      if (response.success && response.response) {
        const newAssistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: response.response,
          type: 'assistant',
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, newAssistantMessage]);
      } else {
        // Manejar error
        console.error('Error en la respuesta de Nevin:', response.error);
      }
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
    } finally {
      setIsLoading(false);
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }
  };

  const renderMessage = (message: ChatMessage) => {
    const isAssistant = message.type === 'assistant';
    
    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isAssistant ? styles.assistantMessage : styles.userMessage,
        ]}
      >
        {isAssistant ? (
          <HTML
            source={{ html: parseNevinResponse(message.content) }}
            // Configurar estilos y renderizadores personalizados
          />
        ) : (
          <Text style={styles.messageText}>{message.content}</Text>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
        >
          {messages.map(renderMessage)}
          {isLoading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color={theme.colors.primary} />
            </View>
          )}
        </ScrollView>

        <View style={styles.inputContainer}>
          <TextInput
            mode="outlined"
            value={inputText}
            onChangeText={setInputText}
            placeholder="Escribe tu pregunta..."
            style={styles.input}
            multiline
            onSubmitEditing={handleSend}
          />
          <Button
            mode="contained"
            onPress={handleSend}
            disabled={isLoading || !inputText.trim()}
            style={styles.sendButton}
          >
            Enviar
          </Button>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  messageContainer: {
    maxWidth: '80%',
    marginVertical: 8,
    padding: 12,
    borderRadius: 12,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#E9ECEF',
  },
  messageText: {
    color: '#fff',
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    alignItems: 'center',
  },
  input: {
    flex: 1,
    marginRight: 8,
  },
  sendButton: {
    marginLeft: 8,
  },
  loadingContainer: {
    padding: 16,
    alignItems: 'center',
  },
});

export default NevinChatScreen;
