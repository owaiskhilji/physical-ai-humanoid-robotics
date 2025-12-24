# Chat Widget Integration Documentation

## Overview
The chat widget is a React component that integrates with the Docusaurus documentation site to provide users with an AI assistant for asking questions about the documentation. The widget is built using React, TypeScript, and follows accessibility standards.

## Architecture

### Components
- **ChatWidget**: Main UI component that handles user interactions and displays messages
- **ChatContext**: React Context provider that manages the chat state across the application
- **MessageDisplay**: Component for displaying individual messages with proper formatting

### Services
- **chatService**: Handles communication with the backend API
- **sessionStorage**: Manages chat history persistence in browser storage
- **performanceMonitor**: Tracks response times and performance metrics
- **errorHandler**: Provides consistent error handling across the application
- **dateUtils**: Utilities for date/time formatting

### Data Models
- **ChatMessage**: Represents a single message in the conversation
- **Conversation**: Represents a collection of related messages
- **ContextSource**: Represents a reference to documentation content

## Integration

### Docusaurus Layout
The chat widget is integrated into all Docusaurus pages through a custom Layout wrapper (`docs/src/theme/Layout.tsx`) that wraps the original layout and adds the ChatWidget component.

### Styling
- The widget styles are defined in `docs/src/css/chatWidget.css`
- Styles are imported via `docs/src/css/custom.css` which is automatically loaded by Docusaurus
- Responsive design and accessibility features are included

## Features

### Core Functionality
- Real-time chat with AI assistant
- Conversation history persistence
- Context source citations
- Multi-turn conversation support

### User Experience
- Floating widget that can be opened/closed
- Visual indicators for connection status
- Typing indicators during AI response generation
- Responsive design for all screen sizes

### Accessibility
- ARIA labels and roles for screen readers
- Keyboard navigation support (Enter to send, Escape to close)
- High contrast mode support
- Focus management

### Error Handling
- Graceful handling of network errors
- Retry mechanism for failed requests
- User-friendly error messages

## API Integration

### Endpoints
- `POST /api/chat/send`: Send a message to the chatbot
- `POST /api/chat/new`: Start a new conversation

### Request Format
```json
{
  "message": "User's message content",
  "conversation_id": "Optional conversation ID for context",
  "session_id": "User session identifier"
}
```

### Response Format
```json
{
  "response": "AI's response content",
  "conversation_id": "ID of the conversation",
  "sources": [Source objects],
  "timestamp": "ISO 8601 datetime"
}
```

## Configuration

### Environment Variables
- `REACT_APP_API_URL`: Base URL for the backend API (defaults to http://localhost:8000)

### Customization
The widget can be customized by passing props to the ChatWidget component:
- `title`: The title displayed in the widget header
- `subtitle`: The subtitle displayed in the widget header

## Development

### Running the Application
1. Start the backend: `cd backend && python -m src.main`
2. Start the frontend: `cd docs && npm start`
3. Access the documentation at http://localhost:3000

### Testing
The implementation includes various quality measures:
- Input validation (1-2000 characters for messages)
- Response time monitoring (target &lt;5 seconds)
- Conversation history limits (max 50 messages)
- URL validation for context sources
- ISO 8601 timestamp formatting

## Security Considerations
- All API communication is validated
- Input is sanitized before being sent to the backend
- Session IDs are managed securely
- No sensitive data is stored in localStorage/sessionStorage beyond chat history