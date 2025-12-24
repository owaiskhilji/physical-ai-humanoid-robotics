# Implementation Plan: Core RAG Chatbot Development

**Branch**: `002-rag-chatbot` | **Date**: 2025-12-10 | **Spec**: [specs/002-rag-chatbot/spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a RAG (Retrieval-Augmented Generation) chatbot that integrates with the existing Docusaurus textbook, allowing students to ask questions about textbook content and receive grounded responses. The system will use FastAPI, Neon Serverless Postgres, and Qdrant Cloud to create a scalable solution that strictly answers questions based only on published book text (chapters 1-5 initially). The implementation includes a selected text mode feature where users can highlight content and get responses based only on that selection. The architecture maintains structure for OpenAI/ChatKit SDK integration while using Gemini for free-tier compliance.

## Technical Context

**Language/Version**: Python 3.11+ (required for FastAPI compatibility and async support)
**Primary Dependencies**: FastAPI (web framework), Neon Serverless Postgres (SQL database), Qdrant Cloud (vector database), Google Gemini (LLM), Pydantic (data validation), Langchain (RAG framework)
**Storage**: Neon Serverless Postgres (relational data), Qdrant Cloud (vector embeddings), File system (book content storage)
**Testing**: pytest (unit/integration tests), FastAPI test client
**Target Platform**: Linux server (cloud deployment), Web browser (Docusaurus integration)
**Project Type**: Web (backend API service with Docusaurus frontend integration)
**Performance Goals**: <5 second response time for queries (per success criteria SC-001), 95% response accuracy (per success criteria SC-002)
**Constraints**: Free-tier service limitations (Neon, Qdrant Cloud, Gemini), RAG grounding to book content only, 99% uptime during peak hours (per success criteria SC-006)
**Scale/Scope**: Support concurrent users (per FR-009), handle book content expansion (per FR-006), integrate with existing Docusaurus textbook (per FR-002)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Compliance Verification

**Technical Accuracy**: ✅ Confirmed - Architecture uses specified technologies: FastAPI, Neon Serverless Postgres, Qdrant Cloud, and Gemini as required by constitution (Section II.B, II.C, II.D).

**Educational Clarity**: ✅ Confirmed - RAG chatbot will provide clear, accurate answers based on textbook content to support learning.

**Free-Tier Architecture**: ✅ Confirmed - All components (FastAPI backend, Neon Serverless Postgres, Qdrant Cloud Free Tier, Gemini) comply with free-tier constraints as specified in constitution.

**Comprehensive Content Structure**: ✅ Confirmed - System will work with the specified textbook chapters (1-5 initially, with expansion capability).

**Strict RAG Chatbot Grounding**: ✅ Confirmed - Requirement to ONLY answer based on published book text is implemented in functional requirement FR-001, with selected text mode in FR-003.

**Sequential Delivery & Documentation**: ✅ Confirmed - Following proper sequence (Project 1 textbook, then Project 2 chatbot) with proper documentation in specs/ directory.

**Technical Stack Compliance**:
- Frontend: Docusaurus (as specified in constitution Section II.A) ✅
- Backend: FastAPI (as specified in constitution Section II.B) ✅
- Database: Neon Serverless Postgres + Qdrant Cloud (as specified in constitution Section II.C) ✅
- AI/RAG: Gemini with OpenAI/ChatKit SDK structure (as specified in constitution Section II.D) ✅

**RAG Requirements**:
- Strict grounding to book text only (as specified in constitution Section IV.A) ✅
- Selected Text Mode functionality (as specified in constitution Section IV.B) ✅
- Modular architecture and FastAPI security best practices (as specified in constitution Section IV.D) ✅

### Post-Design Compliance Verification

**Architecture Validation**: ✅ Confirmed - Microservice architecture with FastAPI backend properly separates concerns while maintaining Docusaurus integration.

**Data Model Compliance**: ✅ Confirmed - Data models (Book Content, Chat Session, Chat Message, Vector Embedding) align with functional requirements and support grounding requirements.

**API Contract Validation**: ✅ Confirmed - RESTful API contracts support all required functionality including selected text mode and content management.

**Security Implementation**: ✅ Confirmed - JWT-based authentication structure and rate limiting implemented to meet security requirements.

**Scalability Verification**: ✅ Confirmed - Content ingestion pipeline designed for incremental updates supporting FR-006 (future chapter integration).

## Project Structure

### Documentation (this feature)

```text
specs/002-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

The RAG chatbot will be implemented as a backend service that integrates with the existing Docusaurus textbook frontend:

```text
backend/
├── src/
│   ├── models/
│   │   ├── chat.py          # Chat session and message models
│   │   ├── content.py       # Book content and chapter models
│   │   └── user.py          # User and session models (for future auth)
│   ├── services/
│   │   ├── rag_service.py   # Core RAG logic and vector search
│   │   ├── chat_service.py  # Chat session management
│   │   ├── content_service.py # Content ingestion and management
│   │   ├── embedding_service.py # Vector embedding operations
│   │   └── llm_service.py   # LLM interaction (Gemini with OpenAI structure)
│   ├── api/
│   │   ├── v1/
│   │   │   ├── chat.py      # Chat endpoints
│   │   │   ├── content.py   # Content management endpoints
│   │   │   └── rag.py       # RAG-specific endpoints
│   │   └── deps.py          # Dependency injection
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection utilities
│   │   └── security.py      # Security utilities (FastAPI security)
│   └── main.py              # FastAPI application entry point
├── tests/
│   ├── unit/
│   │   ├── models/
│   │   ├── services/
│   │   └── api/
│   ├── integration/
│   │   ├── api/
│   │   └── services/
│   └── contract/
│       └── api_contracts/
├── requirements.txt         # Python dependencies
├── alembic/                 # Database migrations
└── docker-compose.yml       # Service orchestration
```

### Integration with Docusaurus Frontend

The existing Docusaurus textbook will communicate with the backend service via API calls:

```text
docs/
├── src/
│   ├── pages/
│   ├── components/
│   │   ├── ChatInterface.js    # Chat UI component
│   │   ├── TextSelector.js     # Text highlighting functionality
│   │   └── ChatHistory.js      # Chat history display
│   └── css/
├── docusaurus.config.js       # Configuration with backend API endpoints
└── static/
```

**Structure Decision**: The architecture follows a microservice approach with a dedicated FastAPI backend for RAG functionality that integrates with the existing Docusaurus frontend. This provides clear separation of concerns while maintaining the required integration with the textbook interface.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
