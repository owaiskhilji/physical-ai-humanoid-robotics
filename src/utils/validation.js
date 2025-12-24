/**
 * Validation functions for ChatSession, ChatMessage, and WidgetState entities
 */

/**
 * Validates a ChatSession entity
 * @param {Object} session - The session object to validate
 * @returns {Array} Array of validation errors
 */
export function validateChatSession(session) {
  const errors = [];

  if (!session.sessionId) {
    errors.push('sessionId must be provided');
  }

  if (!session.title) {
    errors.push('title must be provided');
  }

  if (session.createdAt) {
    const createdAtDate = new Date(session.createdAt);
    if (isNaN(createdAtDate.getTime()) || createdAtDate > new Date()) {
      errors.push('createdAt must be a valid past date');
    }
  }

  if (session.status && !['active', 'inactive', 'archived'].includes(session.status)) {
    errors.push('status must be one of: active, inactive, archived');
  }

  return errors;
}

/**
 * Validates a ChatMessage entity
 * @param {Object} message - The message object to validate
 * @returns {Array} Array of validation errors
 */
export function validateChatMessage(message) {
  const errors = [];

  if (!message.messageId) {
    errors.push('messageId must be provided');
  }

  if (!message.sessionId) {
    errors.push('sessionId must be provided');
  }

  if (!message.senderType) {
    errors.push('senderType must be provided');
  } else if (!['user', 'assistant'].includes(message.senderType)) {
    errors.push('senderType must be user or assistant');
  }

  if (!message.content || message.content.trim() === '') {
    errors.push('content must not be empty');
  }

  if (message.timestamp) {
    const timestampDate = new Date(message.timestamp);
    if (isNaN(timestampDate.getTime())) {
      errors.push('timestamp must be a valid date');
    }
  }

  if (message.status && !['sent', 'delivered', 'error'].includes(message.status)) {
    errors.push('status must be one of: sent, delivered, error');
  }

  return errors;
}

/**
 * Validates a WidgetState entity
 * @param {Object} widgetState - The widget state object to validate
 * @returns {Array} Array of validation errors
 */
export function validateWidgetState(widgetState) {
  const errors = [];

  if (typeof widgetState.isVisible !== 'boolean') {
    errors.push('isVisible must be a boolean');
  }

  if (typeof widgetState.isMinimized !== 'boolean') {
    errors.push('isMinimized must be a boolean');
  }

  if (typeof widgetState.isLoading !== 'boolean') {
    errors.push('isLoading must be a boolean');
  }

  if (typeof widgetState.hasError !== 'boolean') {
    errors.push('hasError must be a boolean');
  }

  if (widgetState.hasError && (!widgetState.errorMessage || typeof widgetState.errorMessage !== 'string')) {
    errors.push('errorMessage must be provided when hasError is true');
  }

  if (widgetState.isVisible && widgetState.isMinimized) {
    errors.push('Only one of visible/minimized states should be true');
  }

  return errors;
}

/**
 * Validates an APIConfig entity
 * @param {Object} apiConfig - The API config object to validate
 * @returns {Array} Array of validation errors
 */
export function validateAPIConfig(apiConfig) {
  const errors = [];

  if (apiConfig.baseUrl) {
    try {
      new URL(apiConfig.baseUrl);
    } catch (e) {
      errors.push('baseUrl must be a valid URL');
    }
  }

  if (apiConfig.healthEndpoint && !apiConfig.healthEndpoint.startsWith('/')) {
    errors.push('healthEndpoint must start with forward slash');
  }

  if (apiConfig.chatStartEndpoint && !apiConfig.chatStartEndpoint.startsWith('/')) {
    errors.push('chatStartEndpoint must start with forward slash');
  }

  if (apiConfig.messageEndpoint && !apiConfig.messageEndpoint.startsWith('/')) {
    errors.push('messageEndpoint must start with forward slash');
  }

  if (apiConfig.sessionEndpoint && !apiConfig.sessionEndpoint.startsWith('/')) {
    errors.push('sessionEndpoint must start with forward slash');
  }

  if (apiConfig.deleteEndpoint && !apiConfig.deleteEndpoint.startsWith('/')) {
    errors.push('deleteEndpoint must start with forward slash');
  }

  return errors;
}

/**
 * Generic validation helper that returns true if valid, false otherwise
 * @param {Function} validator - The specific validator function to use
 * @param {Object} entity - The entity to validate
 * @returns {boolean} True if valid, false otherwise
 */
export function isValid(validator, entity) {
  const errors = validator(entity);
  return errors.length === 0;
}