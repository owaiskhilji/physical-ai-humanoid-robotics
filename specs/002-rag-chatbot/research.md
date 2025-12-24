# Research: Core RAG Chatbot Development

## Overview
This research document addresses all technical unknowns and implementation decisions for the RAG chatbot feature. It consolidates findings from various research tasks to inform the technical design.

## Decision: RAG Architecture Pattern
**Rationale**: Implementing a Retrieval-Augmented Generation system that retrieves relevant textbook content before generating responses ensures grounding to book text only, meeting FR-001 requirement.

**Alternatives considered**:
- Direct LLM without RAG: Would not meet grounding requirements
- Keyword-based search: Would lack semantic understanding of context
- Rule-based system: Would not provide natural language responses

## Decision: Vector Database Selection (Qdrant Cloud)
**Rationale**: Qdrant Cloud provides managed vector storage with semantic search capabilities, supporting the free-tier requirement while enabling efficient similarity search for RAG.

**Alternatives considered**:
- Pinecone: More expensive, doesn't meet free-tier requirement
- Weaviate: Self-hosted option available but requires more maintenance
- FAISS: Requires self-hosting, no managed cloud option

## Decision: LLM Provider (Google Gemini)
**Rationale**: Gemini meets the free-tier compliance requirement while providing strong language understanding capabilities for educational content. The architecture maintains OpenAI/ChatKit SDK structure for future flexibility.

**Alternatives considered**:
- OpenAI: Would exceed free-tier limits
- Anthropic Claude: Would exceed free-tier limits
- Open-source models: Would require self-hosting and more compute resources

## Decision: Selected Text Mode Implementation
**Rationale**: Selected text mode will work by sending the highlighted text as additional context to the LLM, with instructions to only use that context for the response. This ensures responses are grounded in the selected text only.

**Implementation approach**: The frontend will detect text selection and send this context to the backend API, which will prioritize this content in the RAG retrieval process.

## Decision: Content Ingestion Pipeline
**Rationale**: A modular ingestion pipeline allows new chapters to be added without rebuilding the system (FR-006). The pipeline will process new content and update vector embeddings incrementally.

**Implementation approach**:
- Monitor content directory for changes
- Process new/updated chapters into chunks
- Generate embeddings for new chunks
- Update Qdrant index with new embeddings
- Update Postgres metadata

## Decision: Session Management
**Rationale**: Conversation sessions need to be maintained for context, meeting FR-004 requirement. Sessions will be stored temporarily in Postgres with appropriate cleanup policies.

**Implementation approach**:
- Create session records in Postgres
- Associate messages with session IDs
- Implement TTL for inactive sessions
- Include user context for future personalization features

## Decision: API Contract Design
**Rationale**: RESTful API design with FastAPI provides clear contract for frontend integration while supporting the Docusaurus integration requirement (FR-002).

**Key endpoints**:
- POST /api/v1/chat/start - Initialize chat session
- POST /api/v1/chat/message - Send message and receive response
- POST /api/v1/chat/message/selected - Send message with selected text context
- GET /api/v1/chat/session/{id} - Retrieve chat history

## Decision: Security and Authentication Structure
**Rationale**: Implementing security best practices from the start supports future authentication features while maintaining current requirements.

**Implementation approach**:
- JWT-based authentication (ready for future user accounts)
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure API key handling for LLM services