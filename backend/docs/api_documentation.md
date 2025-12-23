# API Documentation: Physical AI Textbook RAG Chatbot

## Overview

The Physical AI Textbook RAG Chatbot provides a RESTful API for interacting with textbook content through a Retrieval-Augmented Generation (RAG) system. The API allows students to ask questions about textbook content and receive grounded responses based only on the provided textbook material.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints are public and do not require authentication. Content management endpoints may require admin authentication.

## Rate Limits

The API implements rate limiting to prevent abuse:
- Chat messages: 30 per minute per IP
- Session creation: 10 per minute per IP
- Content retrieval: 100 per minute per IP
- Health checks: 100 per minute per IP

## Endpoints

### Chat Session Management

#### Create Chat Session
```
POST /chat/start
```

Initialize a new chat session.

**Request Body:**
```json
{
  "session_title": "string",
  "user_id": "string (optional)"
}
```

**Response:**
```json
{
  "id": "string",
  "session_title": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "expires_at": "datetime"
}
```

#### Send Message
```
POST /chat/message
```

Send a message and receive a response from the chatbot.

**Request Body:**
```json
{
  "session_id": "string",
  "message": "string",
  "selected_text": "string (optional)"
}
```

**Response:**
```json
{
  "session_id": "string",
  "response": "string",
  "context_sources": "array",
  "timestamp": "datetime"
}
```

**Selected Text Mode:**
When `selected_text` is provided, the chatbot will respond only based on the provided text, enabling focused explanations of highlighted content.

#### Get Chat Session
```
GET /chat/session/{session_id}
```

Retrieve chat history for a session.

**Response:**
```json
{
  "session_id": "string",
  "session_title": "string",
  "messages": [
    {
      "id": "string",
      "role": "string",
      "content": "string",
      "selected_text": "string",
      "timestamp": "datetime"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Close Chat Session
```
DELETE /chat/session/{session_id}
```

Close and archive a chat session.

**Response:**
```json
{
  "message": "string"
}
```

### Content Management

#### List Chapters
```
GET /content/chapters
```

List available textbook chapters.

**Response:**
```json
{
  "chapters": [
    {
      "chapter_number": "integer",
      "chapter_title": "string",
      "version": "string",
      "published_at": "datetime",
      "content_length": "integer"
    }
  ]
}
```

#### Get Chapter
```
GET /content/chapter/{chapter_number}
```

Retrieve specific chapter content.

**Response:**
```json
{
  "id": "string",
  "chapter_number": "integer",
  "chapter_title": "string",
  "content_text": "string",
  "content_chunks": "array",
  "version": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Create Chapter
```
POST /content/chapter
```

Add new textbook content (admin only).

**Request Body:**
```json
{
  "chapter_number": "integer",
  "chapter_title": "string",
  "content_text": "string (min 100 chars)",
  "version": "string"
}
```

**Response:**
```json
{
  "chapter_id": "string",
  "chapter_number": "integer",
  "chapter_title": "string",
  "version": "string",
  "status": "string"
}
```

#### Update Chapter
```
PUT /content/chapter/{chapter_number}
```

Update existing chapter content with incremental update mechanism.

**Request Body:**
```json
{
  "chapter_title": "string (optional)",
  "content_text": "string (optional, min 100 chars)",
  "version": "string (optional)"
}
```

**Response:**
```json
{
  "chapter_id": "string",
  "chapter_number": "integer",
  "chapter_title": "string",
  "version": "string",
  "status": "string",
  "message": "string"
}
```

#### Delete Chapter
```
DELETE /content/chapter/{chapter_number}
```

Delete chapter content.

**Response:**
```json
{
  "message": "string"
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation error)
- `404`: Not Found
- `409`: Conflict (e.g., chapter already exists)
- `422`: Validation Error
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

## Functional Requirements

### FR-001: Strict RAG Grounding
The system only answers questions based on published book text. Responses will indicate if requested information is not available in the textbook.

### FR-002: Docusaurus Integration
The API is designed for seamless integration with Docusaurus textbook frontend.

### FR-003: Selected Text Mode
When selected text is provided, responses are generated only from the selected content.

### FR-004: Session Persistence
Chat sessions persist for 24 hours and maintain conversation context.

### FR-005: Content Attribution
Responses include attribution to source content when possible.

### FR-006: Content Management
New content can be added without requiring system rebuilds through incremental updates.

### FR-007: Content Quality Validation
All content undergoes validation to ensure quality standards.

### FR-008: Mode Toggle
The system supports both general textbook mode and selected text mode.

### FR-009: Concurrent Users
The system supports multiple concurrent users with isolated sessions.

### FR-010: Error Handling
The system provides graceful degradation and clear error messages.

## Success Criteria

### SC-001: Response Time
Response time is under 5 seconds for 95% of requests.

### SC-002: Response Accuracy
95% of responses are accurate and grounded in textbook content.

### SC-003: Selected Text Mode
Selected text mode functions correctly and provides focused responses.

### SC-004: Content Integration
New content can be integrated within 1 hour of addition.

### SC-006: Uptime
System maintains 99% uptime during peak hours.

## Health Check

```
GET /health
```

Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-chatbot-api"
}
```