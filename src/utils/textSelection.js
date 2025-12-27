/**
 * TextSelectionManager - Handles text selection detection and management
 */
export class TextSelectionManager {
  constructor() {
    this.currentSelection = null;
    this.mode = 'DEFAULT';
    this.onModeChange = null;
    this.onTextSelection = null;
    this.onTextDeselection = null;

    // Only set up event listeners in browser environment
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      this.setupSelectionListener();
    }
  }

  /**
   * Set up event listeners for text selection
   */
  setupSelectionListener() {
    // Only set up event listeners in browser environment
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      return;
    }

    // Listen for mouseup event to detect text selection
    document.addEventListener('mouseup', () => {
      this.handleTextSelection();
    });

    // Listen for keyup events (like Escape) that might clear selection
    document.addEventListener('keyup', (event) => {
      if (event.key === 'Escape') {
        this.handleTextDeselection();
      }
    });

    // Listen for clicks outside selected text
    document.addEventListener('click', (event) => {
      // Check if the click target is within the chat interface to avoid
      // clearing selection when user wants to type in the chat
      const chatElements = ['TEXTAREA', 'INPUT', 'BUTTON'];
      const isClickInChat = chatElements.includes(event.target.tagName) ||
                           event.target.closest('.chat-widget') !== null ||
                           event.target.closest('.chat-input') !== null ||
                           event.target.closest('.chat-send-button') !== null ||
                           event.target.closest('.mode-indicator') !== null;

      // Only clear selection if:
      // 1. The click is NOT in the chat area (to preserve selection while typing)
      // 2. The click is on elements that should explicitly clear the selection (like body, html, etc.)
      // 3. We currently have a stored selection
      if (!isClickInChat && this.currentSelection &&
          (event.target.tagName === 'BODY' || event.target.tagName === 'HTML')) {
        this.handleTextDeselection();
      }
    });
  }

  /**
   * Handle text selection event
   */
  handleTextSelection() {
    // Only handle text selection in browser environment
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      return;
    }

    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    if (selectedText) {
      // Get selection range for offset information
      const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;
      const startOffset = range ? this.getTextOffset(range.startContainer, range.startOffset) : 0;
      const endOffset = range ? this.getTextOffset(range.endContainer, range.endOffset) : 0;

      this.currentSelection = {
        content: selectedText,
        startOffset: startOffset,
        endOffset: endOffset,
        timestamp: new Date(),
        metadata: {
          container: range ? range.commonAncestorContainer : null,
          containerType: range ? range.commonAncestorContainer.nodeType : null
        }
      };

      this.mode = 'SELECTED_TEXT';

      // Notify listeners of mode change
      if (this.onModeChange) {
        this.onModeChange('SELECTED_TEXT', this.currentSelection);
      }

      // Notify listeners of text selection
      if (this.onTextSelection) {
        this.onTextSelection(this.currentSelection);
      }
    }
    // NOTE: We don't automatically clear the stored selection when browser selection is empty
    // because the user might have clicked in the chat input to type, which clears browser selection
    // but should not clear the stored selection for chat context.
  }

  /**
   * Handle text deselection event
   */
  handleTextDeselection() {
    if (this.currentSelection) {
      this.currentSelection = null;
      this.mode = 'DEFAULT';

      // Notify listeners of mode change
      if (this.onModeChange) {
        this.onModeChange('DEFAULT', null);
      }

      // Notify listeners of text deselection
      if (this.onTextDeselection) {
        this.onTextDeselection();
      }
    }
  }

  /**
   * Get text offset relative to parent container
   * @param {Node} node - The text node
   * @param {number} offset - The offset within the node
   * @returns {number} The calculated offset
   */
  getTextOffset(node, offset) {
    if (node.nodeType === Node.TEXT_NODE) {
      return offset;
    }
    return 0; // Simplified - in a real implementation, you'd calculate the full offset
  }

  /**
   * Get the current selected text
   * @returns {string|null} Selected text or null if no selection
   */
  getSelectedText() {
    return this.currentSelection ? this.currentSelection.content : null;
  }

  /**
   * Get the current mode
   * @returns {string} Current mode ('DEFAULT' or 'SELECTED_TEXT')
   */
  getCurrentMode() {
    return this.mode;
  }

  /**
   * Check if currently in selected text mode
   * @returns {boolean} True if in selected text mode
   */
  isSelectionMode() {
    return this.mode === 'SELECTED_TEXT';
  }

  /**
   * Clear the current selection
   */
  clearSelection() {
    this.handleTextDeselection();
    // Only clear selection in browser environment
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      window.getSelection().removeAllRanges();
    }
  }

  /**
   * Get the current selection object
   * @returns {Object|null} Selection object or null
   */
  getCurrentSelection() {
    return this.currentSelection;
  }

  /**
   * Validate the selected text length
   * @param {string} text - Text to validate
   * @param {number} maxLength - Maximum allowed length (default: 5000 characters)
   * @returns {boolean} True if valid length, false otherwise
   */
  validateTextLength(text, maxLength = 5000) {
    if (!text) return true; // Allow null/empty text
    return text.length <= maxLength;
  }

  /**
   * Sanitize selected text to prevent injection
   * @param {string} text - Text to sanitize
   * @returns {string} Sanitized text
   */
  sanitizeText(text) {
    if (!text) return text;

    // Remove potentially dangerous content
    return text
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
      .replace(/javascript:/gi, '') // Remove javascript: protocol
      .replace(/on\w+\s*=/gi, ''); // Remove event handlers
  }

  /**
   * Get word count of selected text
   * @param {string} text - Text to count words for
   * @returns {number} Word count
   */
  getWordCount(text) {
    if (!text) return 0;
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  /**
   * Check if text selection is too long
   * @param {string} text - Text to check
   * @returns {boolean} True if too long, false otherwise
   */
  isTextTooLong(text) {
    return !this.validateTextLength(text);
  }

  /**
   * Set callback for mode changes
   * @param {Function} callback - Function to call when mode changes
   */
  setOnModeChange(callback) {
    this.onModeChange = callback;
  }

  /**
   * Set callback for text selection
   * @param {Function} callback - Function to call when text is selected
   */
  setOnTextSelection(callback) {
    this.onTextSelection = callback;
  }

  /**
   * Set callback for text deselection
   * @param {Function} callback - Function to call when text is deselected
   */
  setOnTextDeselection(callback) {
    this.onTextDeselection = callback;
  }

  /**
   * Get a preview of the selected text (first 60 characters)
   * @param {string} text - Text to preview
   * @returns {string} Preview text
   */
  getTextPreview(text) {
    if (!text) return '';
    return text.length > 60 ? text.substring(0, 60) + '...' : text;
  }
}

// Create a singleton instance
const textSelectionManager = new TextSelectionManager();
export default textSelectionManager;