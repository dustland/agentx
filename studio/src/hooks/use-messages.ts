import { useState, useCallback, useEffect } from 'react';
import { Message, MessageContent, getMessageText, getToolCalls } from '@/types/agentx';
import { nanoid } from 'nanoid';

interface UseMessagesOptions {
  initialMessages?: Message[];
  onMessagesChange?: (messages: Message[]) => void;
}

export function useMessages(options: UseMessagesOptions = {}) {
  const [messages, setMessages] = useState<Message[]>(options.initialMessages || []);

  // Notify parent component of changes
  useEffect(() => {
    if (options.onMessagesChange) {
      options.onMessagesChange(messages);
    }
  }, [messages, options.onMessagesChange]);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: nanoid(),
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  }, []);

  const updateMessage = useCallback((messageId: string, updates: Partial<Message>) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, ...updates } : msg
    ));
  }, []);

  const appendToMessage = useCallback((
    messageId: string, 
    content: string | MessageContent
  ) => {
    setMessages(prev => prev.map(msg => {
      if (msg.id !== messageId) return msg;
      
      // Handle string content
      if (typeof msg.content === 'string' && typeof content === 'string') {
        return { ...msg, content: msg.content + content };
      }
      
      // Convert to array if needed
      const currentContent = Array.isArray(msg.content) 
        ? msg.content 
        : typeof msg.content === 'string' 
          ? [{ type: 'text', text: msg.content } as MessageContent]
          : [msg.content];
      
      const newContent = typeof content === 'string'
        ? { type: 'text', text: content } as MessageContent
        : content;
      
      return { ...msg, content: [...currentContent, newContent] };
    }));
  }, []);

  const removeMessage = useCallback((messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const getLastMessage = useCallback((): Message | undefined => {
    return messages[messages.length - 1];
  }, [messages]);

  const getMessagesByRole = useCallback((role: Message['role']): Message[] => {
    return messages.filter(msg => msg.role === role);
  }, [messages]);

  const getTextContent = useCallback((message: Message): string => {
    return getMessageText(message);
  }, []);

  const getMessageToolCalls = useCallback((message: Message) => {
    return getToolCalls(message);
  }, []);

  return {
    messages,
    setMessages,
    addMessage,
    updateMessage,
    appendToMessage,
    removeMessage,
    clearMessages,
    getLastMessage,
    getMessagesByRole,
    getTextContent,
    getMessageToolCalls,
  };
}