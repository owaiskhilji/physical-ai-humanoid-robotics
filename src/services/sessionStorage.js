/**
 * Service for handling session storage of chat data
 * Based on data-model.md specification for session storage schema
 */

const CHAT_STORAGE_KEY = 'chat';

/**
 * Saves chat data to session storage
 * @param {Object} chatData - The chat data to save
 * @returns {boolean} Whether the save was successful
 */
export const saveChatToSession = (chatData) => {
  try {
    // Validate chat data structure according to data-model.md
    if (!chatData || typeof chatData !== 'object') {
      console.error('Invalid chat data provided for session storage');
      return false;
    }

    const sessionStorageData = {
      [CHAT_STORAGE_KEY]: chatData
    };

    window.sessionStorage.setItem(
      CHAT_STORAGE_KEY,
      JSON.stringify(sessionStorageData)
    );

    return true;
  } catch (error) {
    console.error('Error saving chat to session storage:', error);
    return false;
  }
};

/**
 * Loads chat data from session storage
 * @returns {Object|null} The chat data or null if not found
 */
export const loadChatFromSession = () => {
  try {
    const sessionData = window.sessionStorage.getItem(CHAT_STORAGE_KEY);

    if (!sessionData) {
      return null;
    }

    const parsedData = JSON.parse(sessionData);

    // Return the chat object from the stored data
    return parsedData[CHAT_STORAGE_KEY] || null;
  } catch (error) {
    console.error('Error loading chat from session storage:', error);
    return null;
  }
};

/**
 * Clears chat data from session storage
 */
export const clearChatFromSession = () => {
  try {
    window.sessionStorage.removeItem(CHAT_STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing chat from session storage:', error);
  }
};

/**
 * Saves the current conversation to session storage
 * @param {Object} conversation - The conversation object to save
 * @returns {boolean} Whether the save was successful
 */
export const saveConversationToSession = (conversation) => {
  try {
    const currentData = loadChatFromSession() || {};

    const updatedData = {
      ...currentData,
      currentConversation: conversation,
      updatedAt: new Date().toISOString()
    };

    return saveChatToSession(updatedData);
  } catch (error) {
    console.error('Error saving conversation to session storage:', error);
    return false;
  }
};

/**
 * Loads the current conversation from session storage
 * @returns {Object|null} The conversation object or null if not found
 */
export const loadConversationFromSession = () => {
  try {
    const chatData = loadChatFromSession();
    return chatData?.currentConversation || null;
  } catch (error) {
    console.error('Error loading conversation from session storage:', error);
    return null;
  }
};

/**
 * Saves widget state to session storage
 * @param {Object} widgetState - The widget state to save ({isOpen, position})
 * @returns {boolean} Whether the save was successful
 */
export const saveWidgetStateToSession = (widgetState) => {
  try {
    const currentData = loadChatFromSession() || {};

    const updatedData = {
      ...currentData,
      widgetState: {
        ...currentData.widgetState,
        ...widgetState
      },
      updatedAt: new Date().toISOString()
    };

    return saveChatToSession(updatedData);
  } catch (error) {
    console.error('Error saving widget state to session storage:', error);
    return false;
  }
};

/**
 * Loads widget state from session storage
 * @returns {Object} The widget state or default state if not found
 */
export const loadWidgetStateFromSession = () => {
  try {
    const chatData = loadChatFromSession();
    return chatData?.widgetState || {
      isOpen: false,
      position: { x: null, y: null }
    };
  } catch (error) {
    console.error('Error loading widget state from session storage:', error);
    return {
      isOpen: false,
      position: { x: null, y: null }
    };
  }
};

/**
 * Gets the complete chat state from session storage
 * @returns {Object} The complete chat state
 */
export const getCompleteChatStateFromSession = () => {
  try {
    const chatData = loadChatFromSession();

    if (!chatData) {
      return {
        currentConversation: null,
        widgetState: {
          isOpen: false,
          position: { x: null, y: null }
        },
        updatedAt: null
      };
    }

    return {
      currentConversation: chatData.currentConversation || null,
      widgetState: chatData.widgetState || {
        isOpen: false,
        position: { x: null, y: null }
      },
      updatedAt: chatData.updatedAt || null
    };
  } catch (error) {
    console.error('Error getting complete chat state from session storage:', error);
    return {
      currentConversation: null,
      widgetState: {
        isOpen: false,
        position: { x: null, y: null }
      },
      updatedAt: null
    };
  }
};