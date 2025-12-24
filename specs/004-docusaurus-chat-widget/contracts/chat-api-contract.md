# API Contract: Chat Widget Backend Integration

## Base URL Configuration
The API base URL is configured via environment variable `REACT_APP_API_URL` with default value `http://localhost:8000/api`.

## Health Check Endpoint

### GET /health
Check if the chat API is available.

#### Request
```
GET /health
No request body required
```

#### Response
**Success (200 OK)**
```json
{
  "status": "healthy",
  "service": "rag-chatbot-api"
}
```

**Error (503 Service Unavailable)**
```json
{
  "status": "unhealthy",
  "service": "rag-chatbot-api",
  "error": "description of the issue"
}
```

## Chat Session Management

### POST /v1/chat/start
Create a new chat session.

#### Request
```
POST /v1/chat/start
Content-Type: application/json
```

```json
{
  "session_title": "string",
  "user_id": "string (optional)"
}
```

#### Response
**Success (200 OK)**
```json
{
  "id": "string (session ID)",
  "session_title": "string",
  "is_active": "boolean",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "expires_at": "timestamp (optional)"
}
```

**Error (400 Bad Request)**
```json
{
  "detail": "error description"
}
```

## Messaging Endpoints

### POST /v1/chat/message
Send a message to the chat session and receive a response.

#### Request
```
POST /v1/chat/message
Content-Type: application/json
```

```json
{
  "session_id": "string",
  "message": "string",
  "selected_text": "string (optional)"
}
```

#### Response
**Success (200 OK)**
```json
{
  "session_id": "string",
  "response": "string",
  "context_sources": "array of source objects",
  "timestamp": "timestamp"
}
```

**Error (400 Bad Request)**
```json
{
  "detail": "error description"
}
```

### GET /v1/chat/session/{session_id}
Retrieve chat session history and details.

#### Request
```
GET /v1/chat/session/{session_id}
```

#### Response
**Success (200 OK)**
```json
{
  "session_id": "string",
  "session_title": "string",
  "messages": [
    {
      "id": "string",
      "role": "string (user or assistant)",
      "content": "string",
      "selected_text": "string (optional)",
      "timestamp": "timestamp"
    }
  ],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Error (404 Not Found)**
```json
{
  "detail": "Session not found"
}
```

## Session Deletion

### DELETE /v1/chat/session/{session_id}
Delete/clear a chat session.

#### Request
```
DELETE /v1/chat/session/{session_id}
```

#### Response
**Success (200 OK)**
```json
{
  "message": "Session closed successfully"
}
```

**Error (404 Not Found)**
```json
{
  "detail": "Session not found"
}
```

## Error Response Format
All error responses follow the standard format:
```json
{
  "detail": "error message"
}
```

## Authentication
All endpoints are currently unauthenticated. Future versions may require authentication headers.