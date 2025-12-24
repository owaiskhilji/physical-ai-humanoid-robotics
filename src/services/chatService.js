/**
 * Service for handling chat communication with the backend API
 */

const CHAT_API_BASE = 'http://localhost:8000/api';

/**
 * Send a message to the chat API
 * @param {string} message - The user's message
 * @param {string} [conversationId] - Optional conversation ID for context
 * @param {string} [sessionId] - Optional session ID
 * @returns {Promise<Object>} Response from the API
 */
export const sendMessage = async (message, conversationId = null, sessionId = null) => {
  try {
    const requestBody = {
      message: message,
    };

    if (conversationId) {
      requestBody.conversation_id = conversationId;
    }

    if (sessionId) {
      requestBody.session_id = sessionId;
    }

    const response = await fetch(`${CHAT_API_BASE}/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Start a new conversation
 * @returns {Promise<Object>} Response with new conversation ID
 */
export const startNewConversation = async () => {
  try {
    const response = await fetch(`${CHAT_API_BASE}/chat/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to start new conversation: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error starting new conversation:', error);
    throw error;
  }
};

/**
 * Validate API response format
 * @param {Object} response - The API response to validate
 * @returns {boolean} Whether the response is valid
 */
export const validateApiResponse = (response) => {
  // Check if response has required fields based on API contract
  return (
    response &&
    typeof response.response === 'string' &&
    typeof response.conversation_id === 'string' &&
    Array.isArray(response.sources) &&
    typeof response.timestamp === 'string'
  );
};

/**
 * Validate API request format
 * @param {Object} request - The API request to validate
 * @returns {boolean} Whether the request is valid
 */
export const validateApiRequest = (request) => {
  // Check if request has required fields based on API contract
  return (
    request &&
    typeof request.message === 'string' &&
    request.message.trim() !== '' &&
    request.message.length >= 1 &&
    request.message.length <= 2000
  );
};

/**
 * Make an API call with timeout handling
 * @param {string} endpoint - The API endpoint to call
 * @param {Object} options - Fetch options
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<Object>} Response from the API
 */
export const apiCallWithTimeout = async (endpoint, options, timeout = 10000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(endpoint, {
      ...options,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timeout');
    }

    throw error;
  }
};

/**
 * Make an API call with retry mechanism
 * @param {Function} apiCall - The API call function to retry
 * @param {number} maxRetries - Maximum number of retry attempts
 * @param {number} delay - Delay between retries in milliseconds
 * @returns {Promise<Object>} Response from the API
 */
export const apiCallWithRetry = async (apiCall, maxRetries = 3, delay = 1000) => {
  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;

      // If this was the last attempt, throw the error
      if (attempt === maxRetries) {
        break;
      }

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt))); // Exponential backoff
    }
  }

  throw lastError;
};

/**
 * Send a message with retry and timeout handling
 * @param {string} message - The user's message
 * @param {string} [conversationId] - Optional conversation ID for context
 * @param {string} [sessionId] - Optional session ID
 * @param {number} timeout - Request timeout in milliseconds
 * @param {number} maxRetries - Maximum number of retry attempts
 * @returns {Promise<Object>} Response from the API
 */
export const sendMessageWithRetry = async (
  message,
  conversationId = null,
  sessionId = null,
  timeout = 10000,
  maxRetries = 3
) => {
  const apiCall = () => apiCallWithTimeout(
    `${CHAT_API_BASE}/chat/send`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        session_id: sessionId
      })
    },
    timeout
  );

  return await apiCallWithRetry(apiCall, maxRetries, 1000);
};