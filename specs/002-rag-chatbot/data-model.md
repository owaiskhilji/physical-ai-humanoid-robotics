# Data Model: Core RAG Chatbot Development

## Entity: Book Content
**Description**: Represents the textual content from the physical AI textbook chapters
- **id**: UUID (Primary Key)
- **chapter_number**: Integer (1-6 for textbook chapters)
- **chapter_title**: String (e.g., "Introduction & Why Physical AI Matters")
- **content_text**: Text (Full chapter content)
- **content_chunks**: JSON (Array of text chunks for RAG)
- **version**: String (Content version for tracking changes)
- **created_at**: DateTime (Timestamp of creation)
- **updated_at**: DateTime (Timestamp of last update)

**Validation rules**:
- chapter_number must be between 1 and 6
- chapter_title must not be empty
- content_text must be at least 100 characters

## Entity: Chat Session
**Description**: Represents a user's ongoing interaction with the chatbot
- **id**: UUID (Primary Key)
- **user_id**: UUID (Foreign Key, nullable for anonymous users)
- **session_title**: String (Auto-generated based on first question)
- **is_active**: Boolean (Whether session is currently active)
- **created_at**: DateTime (Timestamp of session creation)
- **updated_at**: DateTime (Timestamp of last interaction)
- **expires_at**: DateTime (TTL for session cleanup)

**Validation rules**:
- user_id is optional (anonymous sessions allowed)
- session_title must not exceed 100 characters
- expires_at must be at least 1 hour after created_at

## Entity: Chat Message
**Description**: Represents individual messages in a conversation
- **id**: UUID (Primary Key)
- **session_id**: UUID (Foreign Key to Chat Session)
- **role**: Enum (user|assistant)
- **content**: Text (The actual message content)
- **selected_text**: Text (Optional highlighted text context)
- **context_chunks**: JSON (Array of content chunks used for response)
- **created_at**: DateTime (Timestamp of message creation)

**Validation rules**:
- role must be either 'user' or 'assistant'
- content must not be empty
- session_id must reference an active session

## Entity: Vector Embedding
**Description**: Represents vector embeddings for RAG retrieval (stored in Qdrant, referenced from Postgres)
- **id**: UUID (Primary Key)
- **content_id**: UUID (Foreign Key to Book Content)
- **chunk_index**: Integer (Position of chunk in original content)
- **chunk_text**: Text (The specific text chunk)
- **vector_id**: String (Reference to Qdrant vector ID)
- **created_at**: DateTime (Timestamp of embedding creation)

**Validation rules**:
- content_id must reference a valid Book Content record
- chunk_index must be non-negative
- vector_id must be unique

## Entity: User (Future Auth Support)
**Description**: Represents users (for future authentication feature)
- **id**: UUID (Primary Key)
- **email**: String (Unique email address)
- **name**: String (User's display name)
- **is_active**: Boolean (Whether account is active)
- **created_at**: DateTime (Account creation timestamp)
- **updated_at**: DateTime (Last update timestamp)

**Validation rules**:
- email must be unique and valid format
- name must not exceed 100 characters

## Relationships
- **Book Content** 1 → * **Vector Embedding** (One content item has many embeddings)
- **Chat Session** 1 → * **Chat Message** (One session has many messages)
- **User** 1 → * **Chat Session** (One user has many sessions, optional)
- **Book Content** * → * **Chat Message** (Many-to-many through context_chunks)

## State Transitions

### Chat Session States
```
CREATED → ACTIVE → INACTIVE → ARCHIVED
```
- CREATED: Session initialized
- ACTIVE: Within TTL period, receiving messages
- INACTIVE: TTL expired, no new messages
- ARCHIVED: Session cleaned up after retention period

### Book Content States
```
DRAFT → PUBLISHED → ARCHIVED
```
- DRAFT: Content exists but not yet available for RAG
- PUBLISHED: Content available for chatbot responses
- ARCHIVED: Content no longer available (for future content management)