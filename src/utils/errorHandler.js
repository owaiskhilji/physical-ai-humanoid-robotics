/**
 * Error handling utilities for the chat widget
 */

/**
 * Standardized error object for the chat system
 */
export class ChatError extends Error {
  constructor(message, code, status = null) {
    super(message);
    this.name = 'ChatError';
    this.code = code;
    this.status = status;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Error codes for the chat system
 */
export const ERROR_CODES = {
  // Backend/API related errors
  API_CONNECTION_FAILED: 'API_CONNECTION_FAILED',
  REQUEST_TIMEOUT: 'REQUEST_TIMEOUT',
  INVALID_RESPONSE: 'INVALID_RESPONSE',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',

  // Validation errors
  INVALID_MESSAGE_FORMAT: 'INVALID_MESSAGE_FORMAT',
  MESSAGE_TOO_LONG: 'MESSAGE_TOO_LONG',
  MESSAGE_EMPTY: 'MESSAGE_EMPTY',
  INVALID_SOURCE_URL: 'INVALID_SOURCE_URL',

  // Session/storage errors
  SESSION_STORAGE_FAILED: 'SESSION_STORAGE_FAILED',
  CONVERSATION_NOT_FOUND: 'CONVERSATION_NOT_FOUND',

  // General errors
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR'
};

/**
 * Handles API errors and returns a standardized error
 * @param {Error|Response|any} error - The error to handle
 * @returns {ChatError} A standardized ChatError object
 */
export const handleApiError = (error) => {
  if (error instanceof ChatError) {
    return error;
  }

  // Handle fetch API errors
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return new ChatError(
      'Unable to connect to the chat service. Please check your network connection.',
      ERROR_CODES.API_CONNECTION_FAILED
    );
  }

  // Handle timeout errors
  if (error.message && error.message.includes('timeout')) {
    return new ChatError(
      'Request timed out. Please try again.',
      ERROR_CODES.REQUEST_TIMEOUT
    );
  }

  // Handle response errors
  if (error.status) {
    switch (error.status) {
      case 429:
        return new ChatError(
          'Rate limit exceeded. Please wait before sending another message.',
          ERROR_CODES.RATE_LIMIT_EXCEEDED,
          error.status
        );
      case 400:
        return new ChatError(
          'Invalid request sent to the chat service.',
          ERROR_CODES.INVALID_RESPONSE,
          error.status
        );
      case 500:
        return new ChatError(
          'The chat service encountered an error. Please try again later.',
          ERROR_CODES.UNKNOWN_ERROR,
          error.status
        );
      default:
        return new ChatError(
          `The chat service returned an error (${error.status}).`,
          ERROR_CODES.UNKNOWN_ERROR,
          error.status
        );
    }
  }

  // Handle generic errors
  return new ChatError(
    error.message || 'An unexpected error occurred.',
    ERROR_CODES.UNKNOWN_ERROR
  );
};

/**
 * Handles validation errors and returns a standardized error
 * @param {string} field - The field that failed validation
 * @param {string} value - The value that failed validation
 * @param {string} expected - What was expected
 * @returns {ChatError} A standardized ChatError object
 */
export const handleValidationError = (field, value, expected) => {
  let errorCode = ERROR_CODES.UNKNOWN_ERROR;
  let message = `Validation failed for ${field}.`;

  switch (field) {
    case 'message':
      if (!value || value.trim() === '') {
        errorCode = ERROR_CODES.MESSAGE_EMPTY;
        message = 'Message cannot be empty.';
      } else if (value.length > 2000) {
        errorCode = ERROR_CODES.MESSAGE_TOO_LONG;
        message = 'Message is too long. Maximum 2000 characters allowed.';
      } else {
        errorCode = ERROR_CODES.INVALID_MESSAGE_FORMAT;
        message = 'Message format is invalid.';
      }
      break;
    case 'sourceUrl':
      errorCode = ERROR_CODES.INVALID_SOURCE_URL;
      message = 'Source URL format is invalid.';
      break;
    default:
      message = `Validation failed for ${field}. Expected ${expected}.`;
  }

  return new ChatError(message, errorCode);
};

/**
 * Logs an error with additional context
 * @param {Error} error - The error to log
 * @param {string} context - Context about where the error occurred
 * @param {Object} additionalData - Additional data to log with the error
 */
export const logError = (error, context = '', additionalData = {}) => {
  const errorLog = {
    timestamp: new Date().toISOString(),
    context,
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
      code: error.code,
      status: error.status
    },
    additionalData
  };

  console.error('Chat Error:', errorLog);
};

/**
 * Shows a user-friendly error message
 * @param {ChatError} error - The error to display
 * @returns {string} A user-friendly error message
 */
export const getUserFriendlyErrorMessage = (error) => {
  if (!(error instanceof ChatError)) {
    return 'An unexpected error occurred. Please try again.';
  }

  switch (error.code) {
    case ERROR_CODES.API_CONNECTION_FAILED:
      return 'Unable to connect to the chat service. Please check your network connection.';
    case ERROR_CODES.REQUEST_TIMEOUT:
      return 'Request timed out. Please try again.';
    case ERROR_CODES.RATE_LIMIT_EXCEEDED:
      return 'You\'ve sent too many messages recently. Please wait before sending another.';
    case ERROR_CODES.MESSAGE_TOO_LONG:
      return 'Your message is too long. Please keep it under 2000 characters.';
    case ERROR_CODES.MESSAGE_EMPTY:
      return 'Please enter a message before sending.';
    case ERROR_CODES.UNKNOWN_ERROR:
      return error.message || 'An unexpected error occurred. Please try again.';
    default:
      return error.message || 'An error occurred. Please try again.';
  }
};

/**
 * Checks if an error is a network error
 * @param {Error} error - The error to check
 * @returns {boolean} Whether the error is a network error
 */
export const isNetworkError = (error) => {
  return error.code === ERROR_CODES.API_CONNECTION_FAILED ||
         error.code === ERROR_CODES.REQUEST_TIMEOUT ||
         error.name === 'TypeError' ||
         error.message.includes('network') ||
         error.message.includes('fetch');
};

/**
 * Checks if an error is a client-side validation error
 * @param {Error} error - The error to check
 * @returns {boolean} Whether the error is a validation error
 */
export const isValidationError = (error) => {
  return [
    ERROR_CODES.INVALID_MESSAGE_FORMAT,
    ERROR_CODES.MESSAGE_TOO_LONG,
    ERROR_CODES.MESSAGE_EMPTY,
    ERROR_CODES.INVALID_SOURCE_URL
  ].includes(error.code);
};

/**
 * Error boundary component for React (to be used in JSX files)
 * This is a placeholder - actual implementation would require JSX
 */
export const createErrorBoundary = (fallbackComponent) => {
  // This would be implemented as a React component in a separate file
  // Returning a configuration object for now
  return {
    fallback: fallbackComponent || 'An error occurred in the chat widget.',
    onError: (error, errorInfo) => {
      logError(error, 'Error Boundary', { errorInfo });
    }
  };
};