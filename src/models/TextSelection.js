/**
 * TextSelection model for representing selected text in the UI
 */
export class TextSelection {
  constructor(id = null, content = '', startOffset = 0, endOffset = 0, timestamp = new Date(), metadata = {}) {
    this.id = id || this.generateId();
    this.content = content;
    this.startOffset = startOffset;
    this.endOffset = endOffset;
    this.timestamp = timestamp instanceof Date ? timestamp : new Date(timestamp);
    this.metadata = metadata;
  }

  generateId() {
    return 'textsel_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Validate the text selection
   * @returns {boolean} True if valid, false otherwise
   */
  isValid() {
    return this.content && this.content.trim().length > 0;
  }

  /**
   * Get the length of the selected text
   * @returns {number} Length of selected text
   */
  getLength() {
    return this.content ? this.content.length : 0;
  }

  /**
   * Get word count of the selected text
   * @returns {number} Word count
   */
  getWordCount() {
    return this.content ? this.content.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
  }

  /**
   * Convert to JSON format
   * @returns {Object} JSON representation
   */
  toJSON() {
    return {
      id: this.id,
      content: this.content,
      startOffset: this.startOffset,
      endOffset: this.endOffset,
      timestamp: this.timestamp.toISOString(),
      metadata: this.metadata
    };
  }

  /**
   * Create TextSelection from JSON
   * @param {Object} json - JSON representation
   * @returns {TextSelection} New instance
   */
  static fromJSON(json) {
    return new TextSelection(
      json.id,
      json.content,
      json.startOffset,
      json.endOffset,
      new Date(json.timestamp),
      json.metadata
    );
  }
}

// Export as default and named
export default TextSelection;