/**
 * localStorage integration for session persistence
 */

const CHAT_STORAGE_KEY = 'docusaurus-chat-widget';

export class StorageManager {
  static saveSession(sessionData) {
    try {
      const storedData = this.getStoredData();
      storedData.session = sessionData;
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(storedData));
    } catch (error) {
      console.error('Error saving session to localStorage:', error);
      throw error;
    }
  }

  static getSession() {
    try {
      const storedData = this.getStoredData();
      return storedData.session || null;
    } catch (error) {
      console.error('Error getting session from localStorage:', error);
      return null;
    }
  }

  static saveWidgetState(widgetState) {
    try {
      const storedData = this.getStoredData();
      storedData.widgetState = widgetState;
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(storedData));
    } catch (error) {
      console.error('Error saving widget state to localStorage:', error);
      throw error;
    }
  }

  static getWidgetState() {
    try {
      const storedData = this.getStoredData();
      return storedData.widgetState || null;
    } catch (error) {
      console.error('Error getting widget state from localStorage:', error);
      return null;
    }
  }

  static clearSession() {
    try {
      const storedData = this.getStoredData();
      delete storedData.session;
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(storedData));
    } catch (error) {
      console.error('Error clearing session from localStorage:', error);
      throw error;
    }
  }

  static clearWidgetState() {
    try {
      const storedData = this.getStoredData();
      delete storedData.widgetState;
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(storedData));
    } catch (error) {
      console.error('Error clearing widget state from localStorage:', error);
      throw error;
    }
  }

  static clearAll() {
    try {
      localStorage.removeItem(CHAT_STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing all chat data from localStorage:', error);
      throw error;
    }
  }

  static getStoredData() {
    try {
      const stored = localStorage.getItem(CHAT_STORAGE_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error parsing stored data:', error);
      return {};
    }
  }

  static getSessionId() {
    try {
      const session = this.getSession();
      return session ? session.sessionId : null;
    } catch (error) {
      console.error('Error getting session ID from localStorage:', error);
      return null;
    }
  }
}