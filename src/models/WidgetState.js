/**
 * WidgetState data model based on data-model.md specification
 */
export class WidgetState {
  constructor(isVisible = false, isMinimized = false, isLoading = false, hasError = false, errorMessage = null, sessionData = null) {
    this.isVisible = isVisible;
    this.isMinimized = isMinimized;
    this.isLoading = isLoading;
    this.hasError = hasError;
    this.errorMessage = errorMessage;
    this.sessionData = sessionData;

    this.validate();
  }

  validate() {
    if (typeof this.isVisible !== 'boolean') {
      throw new Error('isVisible must be a boolean');
    }
    if (typeof this.isMinimized !== 'boolean') {
      throw new Error('isMinimized must be a boolean');
    }
    if (typeof this.isLoading !== 'boolean') {
      throw new Error('isLoading must be a boolean');
    }
    if (typeof this.hasError !== 'boolean') {
      throw new Error('hasError must be a boolean');
    }
    if (this.hasError && (!this.errorMessage || typeof this.errorMessage !== 'string')) {
      throw new Error('errorMessage must be provided when hasError is true');
    }
    if (this.isVisible && this.isMinimized) {
      throw new Error('Only one of visible/minimized states should be true');
    }
  }

  show() {
    this.isVisible = true;
    this.isMinimized = false;
    this.hasError = false;
    this.errorMessage = null;
  }

  hide() {
    this.isVisible = false;
    this.isMinimized = false;
  }

  minimize() {
    if (this.isVisible) {
      this.isMinimized = true;
      this.isVisible = false;
    }
  }

  expand() {
    if (this.isMinimized) {
      this.isVisible = true;
      this.isMinimized = false;
    }
  }

  startLoading() {
    this.isLoading = true;
  }

  stopLoading() {
    this.isLoading = false;
  }

  setError(message) {
    this.hasError = true;
    this.errorMessage = message;
    this.isLoading = false;
  }

  clearError() {
    this.hasError = false;
    this.errorMessage = null;
  }

  setSessionData(sessionData) {
    this.sessionData = sessionData;
  }

  toJSON() {
    return {
      isVisible: this.isVisible,
      isMinimized: this.isMinimized,
      isLoading: this.isLoading,
      hasError: this.hasError,
      errorMessage: this.errorMessage,
      sessionData: this.sessionData ? this.sessionData.toJSON() : null,
    };
  }

  static fromJSON(json) {
    const widgetState = new WidgetState(
      json.isVisible,
      json.isMinimized,
      json.isLoading,
      json.hasError,
      json.errorMessage,
      json.sessionData ? ChatSession.fromJSON(json.sessionData) : null
    );
    return widgetState;
  }
}

// Need to import ChatSession for the static fromJSON method
// We'll handle the circular dependency by setting it after the class is defined
let ChatSession;
export const setChatSessionClass = (ChatSessionClass) => {
  ChatSession = ChatSessionClass;
};