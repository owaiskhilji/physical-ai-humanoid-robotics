# Research Summary: Selected Text Mode Implementation

## Decision: Text Selection Detection Approach
**Rationale**: Using JavaScript's Selection API to detect text selection in the Docusaurus textbook content area. This provides reliable access to selected text content and selection state across browsers.

**Alternatives considered**:
- MutationObserver approach: More complex and less reliable
- Custom text selection handlers: Would require more code and maintenance
- Third-party libraries: Would add unnecessary dependencies

## Decision: Mode Switching Architecture
**Rationale**: Implementing state management in both frontend and backend to handle mode switching. Frontend detects selection and sends mode information with chat requests; backend processes requests differently based on mode.

**Alternatives considered**:
- Pure frontend solution: Would not allow backend to optimize processing
- WebSocket-based approach: Overly complex for this use case
- Cookie/localStorage approach: Less secure and reliable

## Decision: Visual Indicator Design
**Rationale**: Implementing a clear UI badge/indicator in the chatbot interface that shows the current mode and selected text snippet when in Selected Text Mode.

**Alternatives considered**:
- Toolbar approach: Would require more UI real estate
- Highlighted text approach: Would be redundant with user's selection
- Notification approach: Would be too intrusive

## Decision: API Contract Design
**Rationale**: Extending existing chat API endpoint to accept an optional "selectedText" parameter and "mode" field to indicate the current operating mode.

**Alternatives considered**:
- Separate endpoint: Would require more API endpoints to maintain
- Query parameter approach: Would be less structured
- Header-based approach: Would be less obvious to developers