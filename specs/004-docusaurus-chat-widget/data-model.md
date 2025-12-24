# Data Model: Docusaurus Chat Widget

## Entity: ChatSession

### Attributes
- `sessionId` (string): Unique identifier for the chat session
- `title` (string): Display title for the session
- `createdAt` (timestamp): Session creation time
- `lastActive` (timestamp): Time of last interaction
- `status` (enum): Session status (active, inactive, archived)

### Relationships
- Contains many ChatMessage entities
- Associated with one User (optional for anonymous chats)

### Validation Rules
- sessionId must be unique
- createdAt must be in the past
- status must be one of allowed values

## Entity: ChatMessage

### Attributes
- `messageId` (string): Unique identifier for the message
- `sessionId` (string): Reference to parent chat session
- `senderType` (enum): Type of sender (user, assistant)
- `content` (string): Message content text
- `timestamp` (timestamp): Time when message was sent
- `status` (enum): Delivery status (sent, delivered, error)

### Relationships
- Belongs to one ChatSession
- May have associated metadata for rich content

### Validation Rules
- content must not be empty
- senderType must be user or assistant
- timestamp must be in chronological order within session

## Entity: WidgetState

### Attributes
- `isVisible` (boolean): Whether the widget is currently visible
- `isMinimized` (boolean): Whether the chat window is minimized
- `isLoading` (boolean): Whether the widget is in a loading state
- `hasError` (boolean): Whether an error state is active
- `errorMessage` (string): Error message when in error state
- `sessionData` (ChatSession): Current session data

### Relationships
- Contains reference to current ChatSession
- Contains UI state properties

### Validation Rules
- Only one of visible/minimized states should be true
- Error message must be provided when hasError is true

## Entity: APIConfig

### Attributes
- `baseUrl` (string): Base URL for API endpoints
- `healthEndpoint` (string): Health check endpoint path
- `chatStartEndpoint` (string): Chat session start endpoint path
- `messageEndpoint` (string): Message sending endpoint path
- `sessionEndpoint` (string): Session retrieval endpoint path
- `deleteEndpoint` (string): Session deletion endpoint path

### Relationships
- Used by APIService to make API calls

### Validation Rules
- baseUrl must be a valid URL
- All endpoint paths must start with forward slash

## State Transitions

### ChatSession States
```
inactive -> active (on first message)
active -> inactive (on timeout)
active -> archived (on user clear action)
```

### ChatMessage States
```
sent -> delivered (on API confirmation)
sent -> error (on API failure)
```

### WidgetState States
```
hidden -> visible (on FAB click)
visible -> minimized (on minimize action)
minimized -> visible (on expand action)
```