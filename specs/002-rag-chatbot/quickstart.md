# Quickstart Guide: RAG Chatbot Service

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Access to Google Gemini API
- Qdrant Cloud account
- Neon Serverless Postgres account

## Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Update .env with your credentials:
# - GEMINI_API_KEY
# - QDRANT_URL and QDRANT_API_KEY
# - NEON_DATABASE_URL
# - SECRET_KEY
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Run database migrations
cd backend
alembic upgrade head
```

### 4. Start Services
```bash
# Option A: Using Docker Compose
docker-compose up -d

# Option B: Running locally
cd backend
python -m src.main
```

## API Usage

### Initialize Chat Session
```bash
curl -X POST http://localhost:8000/api/v1/chat/start \
  -H "Content-Type: application/json" \
  -d '{"session_title": "Physical AI Questions"}'
```

### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "Explain ROS 2 fundamentals",
    "selected_text": "Optional highlighted text context"
  }'
```

### Get Chat History
```bash
curl -X GET http://localhost:8000/api/v1/chat/session/your-session-id
```

## Frontend Integration

The chatbot integrates with Docusaurus through JavaScript API calls:

```javascript
// Initialize chat interface
const chatSession = await fetch('/api/v1/chat/start', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({session_title: 'Book Questions'})
});

// Send message with selected text
const response = await fetch('/api/v1/chat/message', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: sessionId,
    message: userQuestion,
    selected_text: window.getSelection().toString()
  })
});
```

## Content Management

### Add New Chapter
```bash
curl -X POST http://localhost:8000/api/v1/content/chapter \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{
    "chapter_number": 6,
    "chapter_title": "Hardware Requirements & Architecture",
    "content_text": "Full chapter content here..."
  }'
```

## Development

### Running Tests
```bash
cd backend
pytest tests/unit/
pytest tests/integration/
```

### Local Development
```bash
# Install in development mode
pip install -e .

# Run with auto-reload
python -m src.main --reload
```