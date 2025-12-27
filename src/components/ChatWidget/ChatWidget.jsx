import React, { useState, useEffect, useRef } from 'react';
import FloatingButton from './FloatingButton';
import ChatWindow from './ChatWindow';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingIndicator from './LoadingIndicator';
import ModeIndicator from '../ModeIndicator';
import { SessionManager } from './SessionManager';
import { StorageManager } from '../../utils/storage';
import textSelectionManager from '../../utils/textSelection';
import ChatbotMode from '../../models/ChatbotMode';

/**
 * Main ChatWidget component that manages state and coordinates sub-components
 */
const ChatWidget = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [chatMode, setChatMode] = useState(new ChatbotMode('DEFAULT', null, true));
  const [selectedTextPreview, setSelectedTextPreview] = useState('');

  const messagesEndRef = useRef(null);
  const sessionManager = new SessionManager();

  // Initialize with session data from localStorage or create new session
  useEffect(() => {
    (async () => {
      try {
        // Check if there's an existing session in localStorage
        const existingSessionId = StorageManager.getSessionId();

        if (existingSessionId) {
          // Load existing session
          try {
            const { session, messages: sessionMessages } = await sessionManager.getSession(existingSessionId);
            setSessionId(session.sessionId);
            setMessages(sessionMessages.map(msg => ({
              id: msg.messageId,
              message: msg.content,
              senderType: msg.senderType,
              timestamp: msg.timestamp,
              status: msg.status
            })));
          } catch (error) {
            // If session retrieval fails, create a new session
            console.error('Error loading existing session:', error);
            // Create new session fallback
            try {
              const session = await sessionManager.createSession('Documentation Chat');
              setSessionId(session.sessionId);
              setMessages([{
                id: '1',
                message: 'Hello! How can I help you with the documentation today?',
                senderType: 'assistant',
                timestamp: new Date(),
                status: 'delivered'
              }]);
            } catch (createError) {
              console.error('Error creating fallback session:', createError);
              setMessages([{
                id: '1',
                message: 'Hello! How can I help you with the documentation today?',
                senderType: 'assistant',
                timestamp: new Date(),
                status: 'delivered'
              }]);
            }
          }
        } else {
          // Create new session
          try {
            const session = await sessionManager.createSession('Documentation Chat');
            setSessionId(session.sessionId);
            setMessages([{
              id: '1',
              message: 'Hello! How can I help you with the documentation today?',
              senderType: 'assistant',
              timestamp: new Date(),
              status: 'delivered'
            }]);
          } catch (error) {
            console.error('Error creating new session:', error);
            setMessages([{
              id: '1',
              message: 'Hello! How can I help you with the documentation today?',
              senderType: 'assistant',
              timestamp: new Date(),
              status: 'delivered'
            }]);
          }
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        // Fallback to initial welcome message
        setMessages([{
          id: '1',
          message: 'Hello! How can I help you with the documentation today?',
          senderType: 'assistant',
          timestamp: new Date(),
          status: 'delivered'
        }]);
      }
    })();

    // Set up text selection manager callbacks
    textSelectionManager.setOnModeChange((mode, selection) => {
      setChatMode(new ChatbotMode(mode, selection?.content || null, true));
      if (selection) {
        setSelectedTextPreview(textSelectionManager.getTextPreview(selection.content));
      } else {
        setSelectedTextPreview('');
      }
    });

    textSelectionManager.setOnTextSelection((selection) => {
      console.log('Text selected:', selection);
    });

    textSelectionManager.setOnTextDeselection(() => {
      console.log('Text deselected');
    });
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
    if (!isVisible) {
      setIsMinimized(false);
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    setIsMinimized(false);
  };

  const handleMinimize = () => {
    setIsMinimized(true);
    setIsVisible(false);
  };

  const handleExpand = () => {
    setIsMinimized(false);
    setIsVisible(true);
  };

  const handleSend = async (messageText) => {
    if (!sessionId) {
      console.error('No session ID available');
      return;
    }

    // Add user message to the conversation
    const userMessage = {
      id: `local_${Date.now()}`,
      message: messageText,
      senderType: 'user',
      timestamp: new Date(),
      status: 'sent'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Get selected text if in selected text mode
      let selectedText = null;
      if (chatMode.isSelectedTextMode()) {
        selectedText = chatMode.getSelectedText();
      }

      // Send message via API with selected text and mode
      const { response: aiResponse } = await sessionManager.sendMessage(
        sessionId,
        messageText,
        selectedText,
        chatMode.getCurrentMode()
      );

      // Add AI response to messages
      setMessages(prev => [...prev, {
        id: aiResponse.messageId,
        message: aiResponse.content,
        senderType: aiResponse.senderType,
        timestamp: aiResponse.timestamp,
        status: aiResponse.status
      }]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the conversation
      setMessages(prev => [...prev, {
        id: `error_${Date.now()}`,
        message: 'Sorry, I encountered an error processing your message. Please try again.',
        senderType: 'assistant',
        timestamp: new Date(),
        status: 'error'
      }]);
    } finally {
      // Clear the text selection after sending the message to avoid confusion
      // The context has been sent to the AI, so the selection is no longer needed
      textSelectionManager.clearSelection();

      // Reset the chat mode back to DEFAULT after sending the message
      // This ensures the mode doesn't stay stuck in SELECTED_TEXT mode
      setChatMode(new ChatbotMode('DEFAULT', null, true));

      setIsLoading(false);
    }
  };

  const handleClear = async () => {
    if (!sessionId) {
      console.error('No session ID available');
      return;
    }

    try {
      // Delete the session from the backend
      await sessionManager.deleteSession(sessionId);

      // Create a new session
      const newSession = await sessionManager.createSession('New Documentation Chat');
      setSessionId(newSession.sessionId);

      // Reset to welcome message
      setMessages([{
        id: '1',
        message: 'Hello! How can I help you with the documentation today?',
        senderType: 'assistant',
        timestamp: new Date(),
        status: 'delivered'
      }]);
    } catch (error) {
      console.error('Error clearing session:', error);

      // Fallback: just reset to welcome message
      setMessages([{
        id: '1',
        message: 'Hello! How can I help you with the documentation today?',
        senderType: 'assistant',
        timestamp: new Date(),
        status: 'delivered'
      }]);
    }
  };

  return (
    <>
      <FloatingButton
        isVisible={!isVisible && !isMinimized}
        onClick={toggleVisibility}
      />

      <ChatWindow
        isVisible={isVisible}
        isMinimized={isMinimized}
        onClose={handleClose}
        onMinimize={handleMinimize}
        title="AI Assistant"
      >
        <div className="flex-1 overflow-y-auto p-4 bg-white/30 backdrop-blur-sm" ref={messagesEndRef}>
          <ModeIndicator
            mode={chatMode.getCurrentMode()}
            selectedTextPreview={selectedTextPreview}
            onSwitchToDefault={chatMode.isSelectedTextMode() ? () => setChatMode(new ChatbotMode('DEFAULT', null, true)) : null}
          />
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg.message}
              senderType={msg.senderType}
              timestamp={msg.timestamp}
              status={msg.status}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 text-gray-800 rounded-lg p-3 rounded-bl-none max-w-[85%]">
                <LoadingIndicator message="Thinking..." />
              </div>
            </div>
          )}
        </div>

        <ChatInput
          onSend={handleSend}
          onClear={handleClear}
          disabled={isLoading}
        />
      </ChatWindow>

      {isMinimized && (
        <button
          onClick={handleExpand}
          className={`
            fixed bottom-6 right-6 z-[9999]
            px-4 py-2 rounded-full shadow-xl
            bg-white text-blue-500
            transition-all duration-300 ease-in-out
            hover:bg-gray-50
            border border-gray-200
            chat-widget
          `}
        >
          Chat
        </button>
      )}
    </>
  );
};

export default ChatWidget;