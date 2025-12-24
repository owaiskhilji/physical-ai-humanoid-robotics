/**
 * Conversation model representing a collection of related chat messages
 * Based on data-model.md specification
 */

import { validateChatMessage, chatMessageFromObject } from './ChatMessage.js';

/**
 * Creates a Conversation object
 * @param {string} id - Unique identifier for the conversation
 * @param {Array} messages - Array of ChatMessage objects in chronological order
 * @param {string} createdAt - ISO 8601 datetime when the conversation was started
 * @param {string} updatedAt - ISO 8601 datetime when the conversation was last updated
 * @param {boolean} [isActive=true] - Whether the conversation is currently active
 * @returns {Object} Conversation object
 */
export const createConversation = (id, messages = [], createdAt, updatedAt, isActive = true) => {
  // Validate required fields
  if (!id || typeof id !== 'string') {
    throw new Error('Conversation id is required and must be a string');
  }

  if (!Array.isArray(messages)) {
    throw new Error('Conversation messages must be an array');
  }

  // Validate messages array - each should be a valid ChatMessage
  for (const message of messages) {
    if (!validateChatMessage(message)) {
      throw new Error('All messages in conversation must be valid ChatMessage objects');
    }
  }

  if (!createdAt || typeof createdAt !== 'string') {
    throw new Error('Conversation createdAt is required and must be a string (ISO 8601)');
  }

  if (!updatedAt || typeof updatedAt !== 'string') {
    throw new Error('Conversation updatedAt is required and must be a string (ISO 8601)');
  }

  // Validate datetime formats
  const createdAtDate = new Date(createdAt);
  const updatedAtDate = new Date(updatedAt);
  if (isNaN(createdAtDate.getTime()) || isNaN(updatedAtDate.getTime())) {
    throw new Error('Conversation createdAt and updatedAt must be valid ISO 8601 datetime strings');
  }

  // Validate that createdAt is before or equal to updatedAt
  if (createdAtDate > updatedAtDate) {
    throw new Error('Conversation createdAt must be before or equal to updatedAt');
  }

  // Validate maximum message count
  if (messages.length > 50) {
    throw new Error('Conversation must not exceed 50 messages');
  }

  return {
    id,
    messages,
    createdAt,
    updatedAt,
    isActive
  };
};

/**
 * Validates a Conversation object
 * @param {Object} conversation - The Conversation object to validate
 * @returns {boolean} Whether the conversation is valid
 */
export const validateConversation = (conversation) => {
  try {
    if (!conversation || typeof conversation !== 'object') {
      return false;
    }

    // Check required fields
    if (!conversation.id || typeof conversation.id !== 'string') {
      return false;
    }

    if (!Array.isArray(conversation.messages)) {
      return false;
    }

    if (!conversation.createdAt || typeof conversation.createdAt !== 'string') {
      return false;
    }

    if (!conversation.updatedAt || typeof conversation.updatedAt !== 'string') {
      return false;
    }

    // Validate datetime formats
    const createdAtDate = new Date(conversation.createdAt);
    const updatedAtDate = new Date(conversation.updatedAt);
    if (isNaN(createdAtDate.getTime()) || isNaN(updatedAtDate.getTime())) {
      return false;
    }

    // Validate that createdAt is before or equal to updatedAt
    if (createdAtDate > updatedAtDate) {
      return false;
    }

    // Validate message array
    for (const message of conversation.messages) {
      if (!validateChatMessage(message)) {
        return false;
      }
    }

    // Validate optional fields if present
    if (conversation.isActive !== undefined && typeof conversation.isActive !== 'boolean') {
      return false;
    }

    // Validate maximum message count
    if (conversation.messages.length > 50) {
      return false;
    }

    return true;
  } catch (error) {
    console.error('Error validating Conversation:', error);
    return false;
  }
};

/**
 * Creates a Conversation from a plain object (e.g., from API response)
 * @param {Object} obj - Plain object to convert to Conversation
 * @returns {Object} Validated Conversation object
 */
export const conversationFromObject = (obj) => {
  if (!obj || typeof obj !== 'object') {
    throw new Error('Input must be a valid object');
  }

  const {
    id,
    messages = [],
    createdAt,
    updatedAt,
    isActive = true
  } = obj;

  // Convert message objects to ChatMessage objects
  const chatMessages = messages.map(msg => chatMessageFromObject(msg));

  return createConversation(id, chatMessages, createdAt, updatedAt, isActive);
};

/**
 * Adds a message to a conversation and returns a new conversation object
 * @param {Object} conversation - The conversation to add the message to
 * @param {Object} message - The ChatMessage to add
 * @returns {Object} New conversation object with the added message
 */
export const addMessageToConversation = (conversation, message) => {
  if (!validateConversation(conversation)) {
    throw new Error('Invalid conversation provided');
  }

  if (!validateChatMessage(message)) {
    throw new Error('Invalid message provided');
  }

  // Create new messages array with the new message
  const updatedMessages = [...conversation.messages, message];

  // Validate maximum message count
  if (updatedMessages.length > 50) {
    throw new Error('Conversation must not exceed 50 messages');
  }

  // Update the updatedAt timestamp
  const now = new Date().toISOString();

  return createConversation(
    conversation.id,
    updatedMessages,
    conversation.createdAt,
    now,
    conversation.isActive
  );
};

/**
 * Creates a new conversation
 * @param {string} id - Conversation ID (if not provided, one will be generated)
 * @returns {Object} New conversation object
 */
export const createNewConversation = (id = null) => {
  const conversationId = id || `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const now = new Date().toISOString();

  return createConversation(conversationId, [], now, now, true);
};