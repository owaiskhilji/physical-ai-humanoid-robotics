import { APIConfig } from '../models/APIConfig';

/**
 * API service module for backend communication based on API contracts
 */
export class APIService {
  constructor(config = null) {
    this.config = config || new APIConfig();
  }

  async healthCheck() {
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error('Request timeout: The server is taking too long to respond. Please try again.'));
        }, 15000); // 15 second timeout for health check (increased from 10s)
      });

      // Create the fetch promise
      const fetchPromise = fetch(this.config.getHealthUrl());

      // Race the fetch and timeout promises
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Health check failed');
      }

      return data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  async createSession(sessionData) {
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error('Request timeout: The server is taking too long to respond. Please try again.'));
        }, 30000); // 30 second timeout for session creation (increased from 10s)
      });

      // Create the fetch promise
      const fetchPromise = fetch(this.config.getChatStartUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });

      // Race the fetch and timeout promises
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create session');
      }

      return data;
    } catch (error) {
      console.error('Create session error:', error);
      throw error;
    }
  }

  async sendMessage(sessionId, message, selectedText = null, mode = 'DEFAULT') {
    try {
      const requestBody = {
        session_id: sessionId,
        message: message,
        mode: mode,  // Add mode parameter
      };

      if (selectedText) {
        requestBody.selected_text = selectedText;
      }

      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error('Request timeout: The server is taking too long to respond. Please try again.'));
        }, 30000); // 30 second timeout
      });

      // Create the fetch promise
      const fetchPromise = fetch(this.config.getMessageUrl(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      // Race the fetch and timeout promises
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to send message');
      }

      return data;
    } catch (error) {
      console.error('Send message error:', error);
      // Re-throw the error to be handled by the calling component
      throw error;
    }
  }

  async getSession(sessionId) {
    try {
      // Create a timeout promise with longer timeout for database operations
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error('Request timeout: The server is taking too long to respond. Please try again.'));
        }, 30000); // 30 second timeout for getting session (increased from 10s)
      });

      // Create the fetch promise
      const fetchPromise = fetch(this.config.getSessionUrl(sessionId));

      // Race the fetch and timeout promises
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Session not found');
        }
        throw new Error(data.detail || 'Failed to get session');
      }

      return data;
    } catch (error) {
      console.error('Get session error:', error);
      throw error;
    }
  }

  async deleteSession(sessionId) {
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error('Request timeout: The server is taking too long to respond. Please try again.'));
        }, 30000); // 30 second timeout for deleting session (increased from 10s)
      });

      // Create the fetch promise
      const fetchPromise = fetch(this.config.getDeleteUrl(sessionId), {
        method: 'DELETE',
      });

      // Race the fetch and timeout promises
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Session not found');
        }
        throw new Error(data.detail || 'Failed to delete session');
      }

      return data;
    } catch (error) {
      console.error('Delete session error:', error);
      throw error;
    }
  }

  // Method to update the API configuration
  updateConfig(config) {
    this.config = config;
  }
}

// Export as class and default instance
export default new APIService();