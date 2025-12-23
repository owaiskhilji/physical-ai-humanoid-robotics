# Physical AI Textbook RAG Chatbot - Backend

A Retrieval-Augmented Generation (RAG) chatbot backend service that integrates with the Physical AI & Humanoid Robotics textbook, allowing students to ask questions about textbook content and receive grounded responses.

## Features

- **RAG-based Q&A**: Ask questions about textbook content and get responses grounded in the actual textbook
- **Selected Text Mode**: Highlight text and ask questions only about the selected content
- **Content Management**: Add, update, and manage textbook chapters without system rebuilds
- **Session Persistence**: Maintain conversation context across multiple questions
- **Rate Limiting**: Prevent API abuse with configurable rate limits
- **Content Validation**: Ensure quality standards for all textbook content

## Architecture

The backend is built with:
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
- **Qdrant**: Vector similarity search engine for RAG functionality
- **Google Gemini**: Large Language Model for generating responses
- **Neon**: Serverless PostgreSQL for storing structured data

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for containerized deployment)
- Google Gemini API key
- Qdrant Cloud account (or local Qdrant instance)
- Neon Serverless Postgres account

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd physical-ai-textbook/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URLs
   ```

## Configuration

Create a `.env` file in the backend directory with the following variables:

```bash
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
NEON_DATABASE_URL=your_neon_database_url
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Database Setup

Run database migrations to set up the required tables:

```bash
alembic upgrade head
```

## Running the Application

### Development Mode
```bash
python -m src.main
```

### Using Docker
```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Chat Endpoints

- `POST /api/v1/chat/start` - Create a new chat session
- `POST /api/v1/chat/message` - Send a message and get a response
- `GET /api/v1/chat/session/{session_id}` - Get chat history
- `DELETE /api/v1/chat/session/{session_id}` - Close a chat session

### Content Endpoints

- `GET /api/v1/content/chapters` - List all available chapters
- `GET /api/v1/content/chapter/{chapter_number}` - Get specific chapter content
- `POST /api/v1/content/chapter` - Create new chapter (admin only)
- `PUT /api/v1/content/chapter/{chapter_number}` - Update chapter content
- `DELETE /api/v1/content/chapter/{chapter_number}` - Delete chapter content

### Health Check

- `GET /health` - Check API health status

## Selected Text Mode

The chatbot supports a special "Selected Text Mode" where users can highlight text in the textbook and ask questions specifically about that content. To use this feature, include the `selected_text` parameter in your message request:

```json
{
  "session_id": "session-id",
  "message": "Explain this concept?",
  "selected_text": "The highlighted text content here..."
}
```

## Content Management

The system supports dynamic content management without requiring system rebuilds:

1. **Adding Content**: Use the POST `/api/v1/content/chapter` endpoint
2. **Updating Content**: Use the PUT `/api/v1/content/chapter/{chapter_number}` endpoint (uses incremental updates)
3. **Content Validation**: All content undergoes validation for quality and structure

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Chat messages: 30 per minute per IP
- Session creation: 10 per minute per IP
- Content retrieval: 100 per minute per IP

## Testing

Run unit tests:
```bash
pytest tests/unit/
```

Run integration tests:
```bash
pytest tests/integration/
```

Run all tests:
```bash
pytest
```

## Project Structure

```
backend/
├── src/
│   ├── models/           # Database models
│   ├── services/         # Business logic services
│   ├── api/             # API routes
│   │   └── v1/          # API version 1
│   ├── core/            # Core utilities
│   └── main.py          # Application entry point
├── tests/               # Test files
├── docs/                # Documentation
├── requirements.txt     # Python dependencies
├── alembic/             # Database migrations
└── docker-compose.yml   # Docker configuration
```

## Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key
- `QDRANT_URL`: Qdrant vector database URL
- `QDRANT_API_KEY`: Qdrant API key
- `NEON_DATABASE_URL`: Neon PostgreSQL database URL
- `SECRET_KEY`: Secret key for security
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS

## Deployment

For production deployment:

1. Set up environment variables in your deployment environment
2. Run database migrations
3. Start the application server
4. Set up a reverse proxy (e.g., nginx) for SSL termination
5. Configure load balancing if needed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.