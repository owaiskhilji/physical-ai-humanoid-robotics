import React, { createContext, useContext, useReducer } from 'react';
import { createNewConversation, addMessageToConversation } from '../models/Conversation.js';
import { createChatMessage } from '../models/ChatMessage.js';

// Define initial state
const initialState = {
  currentConversation: null,
  isWidgetOpen: false,
  isLoading: false,
  error: null,
};

// Define action types
const actionTypes = {
  SET_CONVERSATION: 'SET_CONVERSATION',
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_WIDGET_OPEN: 'SET_WIDGET_OPEN',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  RESET_CONVERSATION: 'RESET_CONVERSATION',
};

// Reducer function
const chatReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_CONVERSATION:
      return {
        ...state,
        currentConversation: action.payload,
        error: null,
      };

    case actionTypes.ADD_MESSAGE:
      if (!state.currentConversation) {
        return state;
      }
      return {
        ...state,
        currentConversation: addMessageToConversation(
          state.currentConversation,
          action.payload
        ),
      };

    case actionTypes.SET_WIDGET_OPEN:
      return {
        ...state,
        isWidgetOpen: action.payload,
      };

    case actionTypes.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };

    case actionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case actionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    case actionTypes.RESET_CONVERSATION:
      return {
        ...state,
        currentConversation: null,
        error: null,
      };

    default:
      return state;
  }
};

// Create context
const ChatContext = createContext();

// Provider component
export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Actions
  const setConversation = (conversation) => {
    dispatch({ type: actionTypes.SET_CONVERSATION, payload: conversation });
  };

  const addMessage = (message) => {
    dispatch({ type: actionTypes.ADD_MESSAGE, payload: message });
  };

  const setWidgetOpen = (isOpen) => {
    dispatch({ type: actionTypes.SET_WIDGET_OPEN, payload: isOpen });
  };

  const setLoading = (isLoading) => {
    dispatch({ type: actionTypes.SET_LOADING, payload: isLoading });
  };

  const setError = (error) => {
    dispatch({ type: actionTypes.SET_ERROR, payload: error });
  };

  const clearError = () => {
    dispatch({ type: actionTypes.CLEAR_ERROR });
  };

  const resetConversation = () => {
    dispatch({ type: actionTypes.RESET_CONVERSATION });
  };

  const startNewConversation = () => {
    const newConversation = createNewConversation();
    setConversation(newConversation);
    return newConversation;
  };

  const sendMessage = async (messageText, sender = 'user') => {
    if (!messageText || !messageText.trim()) {
      throw new Error('Message text is required');
    }

    if (messageText.length > 2000) {
      throw new Error('Message must be between 1 and 2000 characters');
    }

    try {
      setLoading(true);
      setError(null);

      // Create and add user message to conversation
      const userMessage = createChatMessage(
        `msg_${Date.now()}`,
        sender,
        messageText,
        new Date().toISOString(),
        'sent'
      );

      if (state.currentConversation) {
        addMessage(userMessage);
      } else {
        // Start new conversation if none exists
        const newConversation = startNewConversation();
        addMessage(userMessage);
      }

      return userMessage;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    ...state,
    actions: {
      setConversation,
      addMessage,
      setWidgetOpen,
      setLoading,
      setError,
      clearError,
      resetConversation,
      startNewConversation,
      sendMessage,
    },
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

// Custom hook to use the chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// Export action types for use elsewhere if needed
export { actionTypes };