import { APIService } from '../../services/APIService';
import { StorageManager } from '../../utils/storage';
import { ChatSession } from '../../models/ChatSession';
import { ChatMessage } from '../../models/ChatMessage';

/**
 * Session management logic for creating, retrieving, and deleting chat sessions
 */
export class SessionManager {
  constructor(apiService = null) {
    this.apiService = apiService || new APIService();
  }

  async createSession(title = 'New Chat Session') {
    try {
      const sessionData = {
        session_title: title,
        user_id: null // Anonymous user for now
      };

      const response = await this.apiService.createSession(sessionData);

      const session = new ChatSession(
        response.id,
        response.session_title,
        new Date(response.created_at),
        new Date(response.updated_at),
        response.is_active ? 'active' : 'inactive'
      );

      // Save session to localStorage
      StorageManager.saveSession(session.toJSON());

      return session;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }

  async getSession(sessionId) {
    try {
      const response = await this.apiService.getSession(sessionId);

      const session = new ChatSession(
        response.session_id,
        response.session_title,
        new Date(response.created_at),
        new Date(response.updated_at),
        response.messages.length > 0 ? 'active' : 'inactive'
      );

      // Convert messages from API response to ChatMessage objects
      const messages = response.messages.map(msg =>
        new ChatMessage(
          msg.id,
          msg.session_id,
          msg.role,
          msg.content,
          new Date(msg.timestamp),
          'delivered' // Assume delivered since we're retrieving
        )
      );
      console.log('Retrieved session with messages:', session, messages);
      return { session, messages };
    } catch (error) {
      console.error('Error getting session:', error);
      throw error;
    }
  }

  async deleteSession(sessionId) {
    try {
      const response = await this.apiService.deleteSession(sessionId);

      // Remove session from localStorage
      StorageManager.clearSession();

      return response;
    } catch (error) {
      console.error('Error deleting session:', error);
      throw error;
    }
  }

  async sendMessage(sessionId, message, selectedText = null, mode = 'DEFAULT') {
    try {
      const response = await this.apiService.sendMessage(sessionId, message, selectedText, mode);

      // Validate the response structure to ensure it has the expected fields
      if (!response || typeof response.response !== 'string') {
        console.error('Invalid response structure received:', response);
        throw new Error('Invalid response from server: missing response field');
      }

      // Create ChatMessage object from response
      const aiMessage = new ChatMessage(
        `ai_${Date.now()}`, // Generate a temporary ID
        response.session_id || sessionId,
        'assistant',
        response.response,
        new Date(response.timestamp || new Date()),
        'delivered'
      );

      return { response: aiMessage, contextSources: response.context_sources || [] };
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async healthCheck() {
    try {
      const response = await this.apiService.healthCheck();
      return response;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Get session ID from localStorage
  getCurrentSessionId() {
    return StorageManager.getSessionId();
  }

  // Get session from localStorage
  getCurrentSession() {
    const sessionData = StorageManager.getSession();
    if (sessionData) {
      return ChatSession.fromJSON(sessionData);
    }
    return null;
  }

  // Clear current session from localStorage
  clearCurrentSession() {
    StorageManager.clearSession();
  }
}