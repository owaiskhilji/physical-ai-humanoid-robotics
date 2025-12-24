/**
 * ChatSession data model based on data-model.md specification
 */
export class ChatSession {
  constructor(sessionId, title, createdAt, lastActive, status = 'active') {
    this.sessionId = sessionId;
    this.title = title;
    this.createdAt = createdAt;
    this.lastActive = lastActive;
    this.status = status; // 'active', 'inactive', 'archived'

    this.validate();
  }

  validate() {
    if (!this.sessionId) {
      throw new Error('sessionId must be provided');
    }
    if (!this.title) {
      throw new Error('title must be provided');
    }
    if (!(this.createdAt instanceof Date) || this.createdAt > new Date()) {
      throw new Error('createdAt must be a valid past date');
    }
    if (!['active', 'inactive', 'archived'].includes(this.status)) {
      throw new Error('status must be one of: active, inactive, archived');
    }
  }

  updateLastActive() {
    this.lastActive = new Date();
  }

  isActive() {
    return this.status === 'active';
  }

  archive() {
    this.status = 'archived';
  }

  toJSON() {
    return {
      sessionId: this.sessionId,
      title: this.title,
      createdAt: this.createdAt.toISOString(),
      lastActive: this.lastActive.toISOString(),
      status: this.status,
    };
  }

  static fromJSON(json) {
    return new ChatSession(
      json.sessionId,
      json.title,
      new Date(json.createdAt),
      new Date(json.lastActive),
      json.status
    );
  }
}