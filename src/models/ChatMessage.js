/**
 * ChatMessage model representing a single message in the conversation
 * Based on data-model.md specification
 */
export class ChatMessage {
  /**
   * Creates a ChatMessage object
   * @param {string} id - Unique identifier for the message
   * @param {string} sessionId - The session ID this message belongs to
   * @param {string} senderType - The sender of the message ('user' or 'assistant')
   * @param {string} content - The text content of the message
   * @param {Date} timestamp - Date when the message was sent/received
   * @param {string} [status='sent'] - Message status ('sending', 'sent', 'delivered', 'error')
   * @param {Array} [sources=[]] - Array of context sources associated with AI responses
   */
  constructor(id, sessionId, senderType, content, timestamp, status = 'sent', sources = []) {
    // Validate required fields
    if (!id || typeof id !== 'string') {
      throw new Error('ChatMessage id is required and must be a string');
    }

    if (!sessionId || typeof sessionId !== 'string') {
      throw new Error('ChatMessage sessionId is required and must be a string');
    }

    if (!senderType || typeof senderType !== 'string' || !['user', 'assistant'].includes(senderType)) {
      throw new Error('ChatMessage senderType is required and must be "user" or "assistant"');
    }

    if (!content || typeof content !== 'string') {
      throw new Error('ChatMessage content is required and must be a string');
    }

    if (!(timestamp instanceof Date)) {
      throw new Error('ChatMessage timestamp must be a Date object');
    }

    if (status && typeof status !== 'string') {
      throw new Error('ChatMessage status must be a string');
    }

    this.messageId = id;
    this.sessionId = sessionId;
    this.senderType = senderType;
    this.content = content;
    this.timestamp = timestamp;
    this.status = status;
    this.sources = sources || [];
  }

  /**
   * Creates a ChatMessage from a plain object (e.g., from API response)
   * @param {Object} obj - Plain object to convert to ChatMessage
   * @returns {ChatMessage} Validated ChatMessage instance
   */
  static fromObject(obj) {
    if (!obj || typeof obj !== 'object') {
      throw new Error('Input must be a valid object');
    }

    const {
      id,
      session_id,
      role,
      content,
      timestamp,
      status = 'sent',
      sources = []
    } = obj;

    // Convert timestamp string to Date if it's a string
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;

    return new ChatMessage(
      id || `msg_${Date.now()}`,
      session_id,
      role, // role from API often maps to senderType
      content,
      date,
      status,
      sources
    );
  }

  /**
   * Validates this ChatMessage instance
   * @returns {boolean} Whether the message is valid
   */
  validate() {
    try {
      if (!this.messageId || typeof this.messageId !== 'string') {
        return false;
      }

      if (!this.sessionId || typeof this.sessionId !== 'string') {
        return false;
      }

      if (!this.senderType || typeof this.senderType !== 'string' || !['user', 'assistant'].includes(this.senderType)) {
        return false;
      }

      if (!this.content || typeof this.content !== 'string') {
        return false;
      }

      if (!(this.timestamp instanceof Date)) {
        return false;
      }

      if (this.status && typeof this.status !== 'string') {
        return false;
      }

      if (this.sources && !Array.isArray(this.sources)) {
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error validating ChatMessage:', error);
      return false;
    }
  }

  /**
   * Converts this ChatMessage instance to a plain object
   * @returns {Object} Plain object representation
   */
  toObject() {
    return {
      id: this.messageId,
      session_id: this.sessionId,
      role: this.senderType,
      content: this.content,
      timestamp: this.timestamp.toISOString(),
      status: this.status,
      sources: this.sources
    };
  }
}

/**
 * Creates a ChatMessage object (function for backward compatibility)
 * @param {string} id - Unique identifier for the message
 * @param {string} sessionId - The session ID this message belongs to
 * @param {string} senderType - The sender of the message ('user' or 'assistant')
 * @param {string} content - The text content of the message
 * @param {Date} timestamp - Date when the message was sent/received
 * @param {string} [status='sent'] - Message status ('sending', 'sent', 'delivered', 'error')
 * @param {Array} [sources=[]] - Array of context sources associated with AI responses
 * @returns {ChatMessage} ChatMessage instance
 */
export const createChatMessage = (id, sessionId, senderType, content, timestamp, status = 'sent', sources = []) => {
  return new ChatMessage(id, sessionId, senderType, content, timestamp, status, sources);
};

/**
 * Validates a ChatMessage object
 * @param {ChatMessage} message - The ChatMessage object to validate
 * @returns {boolean} Whether the message is valid
 */
export const validateChatMessage = (message) => {
  if (!message || typeof message !== 'object') {
    return false;
  }

  if (message instanceof ChatMessage) {
    return message.validate();
  }

  // If it's a plain object, create a ChatMessage and validate
  try {
    const chatMessage = ChatMessage.fromObject(message);
    return chatMessage.validate();
  } catch (error) {
    console.error('Error validating ChatMessage:', error);
    return false;
  }
};