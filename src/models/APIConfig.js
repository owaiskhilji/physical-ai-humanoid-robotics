/**
 * APIConfig data model based on data-model.md specification
 */
export class APIConfig {
  constructor(
    baseUrl = this.getEnvVar('REACT_APP_API_URL') || 'https://representative-claire-owaiskhilji-f0476f0b.koyeb.app/api',
    healthEndpoint = '/health',
    chatStartEndpoint = '/v1/chat/start',
    messageEndpoint = '/v1/chat/message',
    sessionEndpoint = '/v1/chat/session',
    deleteEndpoint = '/v1/chat/session'
  ) {
    this.baseUrl = baseUrl;
    this.healthEndpoint = healthEndpoint;
    this.chatStartEndpoint = chatStartEndpoint;
    this.messageEndpoint = messageEndpoint;
    this.sessionEndpoint = sessionEndpoint;
    this.deleteEndpoint = deleteEndpoint;

    this.validate();
  }

  validate() {
    try {
      new URL(this.baseUrl);
    } catch (e) {
      throw new Error('baseUrl must be a valid URL');
    }

    if (!this.healthEndpoint.startsWith('/')) {
      throw new Error('healthEndpoint must start with forward slash');
    }
    if (!this.chatStartEndpoint.startsWith('/')) {
      throw new Error('chatStartEndpoint must start with forward slash');
    }
    if (!this.messageEndpoint.startsWith('/')) {
      throw new Error('messageEndpoint must start with forward slash');
    }
    if (!this.sessionEndpoint.startsWith('/')) {
      throw new Error('sessionEndpoint must start with forward slash');
    }
    if (!this.deleteEndpoint.startsWith('/')) {
      throw new Error('deleteEndpoint must start with forward slash');
    }
  }

  getHealthUrl() {
    return this.baseUrl + this.healthEndpoint;
  }

  getChatStartUrl() {
    return this.baseUrl + this.chatStartEndpoint;
  }

  getMessageUrl() {
    return this.baseUrl + this.messageEndpoint;
  }

  getSessionUrl(sessionId) {
    return `${this.baseUrl}${this.sessionEndpoint}/${sessionId}`;
  }

  getDeleteUrl(sessionId) {
    return `${this.baseUrl}${this.deleteEndpoint}/${sessionId}`;
  }

  toJSON() {
    return {
      baseUrl: this.baseUrl,
      healthEndpoint: this.healthEndpoint,
      chatStartEndpoint: this.chatStartEndpoint,
      messageEndpoint: this.messageEndpoint,
      sessionEndpoint: this.sessionEndpoint,
      deleteEndpoint: this.deleteEndpoint,
    };
  }

  static fromJSON(json) {
    return new APIConfig(
      json.baseUrl,
      json.healthEndpoint,
      json.chatStartEndpoint,
      json.messageEndpoint,
      json.sessionEndpoint,
      json.deleteEndpoint
    );
  }

  // Helper method to safely get environment variables in both Node.js and browser environments
  getEnvVar(varName) {
    // Check if we're in a Node.js environment (process exists)
    if (typeof process !== 'undefined' && process.env) {
      return process.env[varName];
    }

    // For browser environments, check if there's a global environment variable
    // This can be set via Docusaurus webpack DefinePlugin if needed
    if (typeof window !== 'undefined' && window.ENV) {
      return window.ENV[varName];
    }

    // Fallback for browser environments where no process exists
    return undefined;
  }
}