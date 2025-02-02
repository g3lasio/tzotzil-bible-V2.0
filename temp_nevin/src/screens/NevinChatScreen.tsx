
import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Text,
  TextInput,
  Button,
  IconButton,
  Card,
  ActivityIndicator,
  useTheme,
  Menu,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NevinService } from '../services/NevinService';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { ChatMessage } from '../types/nevin';

export default function NevinChatScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [menuVisible, setMenuVisible] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<ChatMessage | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const theme = useTheme();

  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await AsyncStorage.getItem('chat_history');
      if (history) {
        setMessages(JSON.parse(history));
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const saveChatHistory = async (newMessages: ChatMessage[]) => {
    try {
      await AsyncStorage.setItem('chat_history', JSON.stringify(newMessages));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const newUserMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputText.trim(),
      type: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await NevinService.getResponse(inputText.trim(), messages);
      
      if (response.success && response.message) {
        const newNevinMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: response.message,
          type: 'assistant',
          timestamp: new Date(),
        };

        const updatedMessages = [...messages, newUserMessage, newNevinMessage];
        setMessages(updatedMessages);
        saveChatHistory(updatedMessages);
      } else {
        Alert.alert('Error', 'No pude procesar tu mensaje. Por favor, intenta de nuevo.');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      Alert.alert('Error', 'Hubo un problema al comunicarse con Nevin.');
    } finally {
      setIsLoading(false);
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }
  };

  const handleClearChat = () => {
    Alert.alert(
      'Limpiar Chat',
      '¿Estás seguro que deseas borrar todo el historial?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Limpiar',
          onPress: async () => {
            setMessages([]);
            await AsyncStorage.removeItem('chat_history');
          },
          style: 'destructive'
        }
      ]
    );
  };

  const handleCopyMessage = (message: ChatMessage) => {
    // Implementar la copia al portapapeles
    setSelectedMessage(null);
    setMenuVisible(false);
  };

  const renderMessage = (message: ChatMessage) => {
    const isAssistant = message.type === 'assistant';
    
    return (
      <Card
        key={message.id}
        style={[
          styles.messageCard,
          isAssistant ? styles.assistantMessage : styles.userMessage,
        ]}
        onLongPress={() => {
          setSelectedMessage(message);
          setMenuVisible(true);
        }}
      >
        <Card.Content>
          <Text style={styles.messageText}>{message.content}</Text>
          <Text style={styles.timestamp}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </Text>
        </Card.Content>
      </Card>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <View style={styles.header}>
          <Text style={styles.title}>Nevin AI</Text>
          <IconButton
            icon="delete"
            onPress={handleClearChat}
            disabled={messages.length === 0}
          />
        </View>

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
            maxLength={500}
            right={<TextInput.Icon icon="send" onPress={handleSend} disabled={isLoading || !inputText.trim()} />}
          />
        </View>

        <Menu
          visible={menuVisible}
          onDismiss={() => {
            setMenuVisible(false);
            setSelectedMessage(null);
          }}
          anchor={{ x: 0, y: 0 }}
        >
          <Menu.Item 
            onPress={() => handleCopyMessage(selectedMessage!)}
            title="Copiar mensaje"
            icon="content-copy"
          />
        </Menu>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  messageCard: {
    marginVertical: 4,
    maxWidth: '80%',
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
    fontSize: 16,
  },
  timestamp: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'right',
  },
  inputContainer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  input: {
    maxHeight: 100,
  },
  loadingContainer: {
    padding: 16,
    alignItems: 'center',
  },
});
