/**
 * ChatbotMode model for representing the current operating mode of the chatbot
 */
export class ChatbotMode {
  constructor(mode = 'DEFAULT', selectedText = null, isActive = false, lastUpdated = new Date()) {
    this.mode = mode; // 'DEFAULT' or 'SELECTED_TEXT'
    this.selectedText = selectedText;
    this.isActive = isActive;
    this.lastUpdated = lastUpdated instanceof Date ? lastUpdated : new Date(lastUpdated);
  }

  /**
   * Set the mode to DEFAULT
   */
  setDefaultMode() {
    this.mode = 'DEFAULT';
    this.selectedText = null;
    this.isActive = true;
    this.lastUpdated = new Date();
  }

  /**
   * Set the mode to SELECTED_TEXT
   * @param {string} selectedText - The selected text content
   */
  setSelectedTextMode(selectedText) {
    this.mode = 'SELECTED_TEXT';
    this.selectedText = selectedText;
    this.isActive = true;
    this.lastUpdated = new Date();
  }

  /**
   * Check if the current mode is DEFAULT
   * @returns {boolean} True if in DEFAULT mode
   */
  isDefaultMode() {
    return this.mode === 'DEFAULT';
  }

  /**
   * Check if the current mode is SELECTED_TEXT
   * @returns {boolean} True if in SELECTED_TEXT mode
   */
  isSelectedTextMode() {
    return this.mode === 'SELECTED_TEXT';
  }

  /**
   * Get the current mode
   * @returns {string} Current mode ('DEFAULT' or 'SELECTED_TEXT')
   */
  getCurrentMode() {
    return this.mode;
  }

  /**
   * Check if the mode has selected text
   * @returns {boolean} True if there is selected text
   */
  hasSelectedText() {
    return this.mode === 'SELECTED_TEXT' && this.selectedText && this.selectedText.trim().length > 0;
  }

  /**
   * Get the selected text (if any)
   * @returns {string|null} Selected text or null
   */
  getSelectedText() {
    return this.hasSelectedText() ? this.selectedText : null;
  }

  /**
   * Convert to JSON format
   * @returns {Object} JSON representation
   */
  toJSON() {
    return {
      mode: this.mode,
      selectedText: this.selectedText,
      isActive: this.isActive,
      lastUpdated: this.lastUpdated.toISOString()
    };
  }

  /**
   * Create ChatbotMode from JSON
   * @param {Object} json - JSON representation
   * @returns {ChatbotMode} New instance
   */
  static fromJSON(json) {
    return new ChatbotMode(
      json.mode,
      json.selectedText,
      json.isActive,
      new Date(json.lastUpdated)
    );
  }

  /**
   * Validate the current mode
   * @returns {boolean} True if valid, false otherwise
   */
  isValid() {
    return ['DEFAULT', 'SELECTED_TEXT'].includes(this.mode);
  }

  /**
   * Get a display label for the current mode
   * @returns {string} Display label
   */
  getDisplayLabel() {
    if (this.mode === 'SELECTED_TEXT') {
      return 'Focus Mode';
    }
    return 'Default Mode';
  }

  /**
   * Get a display description for the current mode
   * @returns {string} Display description
   */
  getDisplayDescription() {
    if (this.mode === 'SELECTED_TEXT') {
      return 'Responding based on selected text only';
    }
    return 'Searching entire textbook for answers';
  }
}

// Export as default and named
export default ChatbotMode;