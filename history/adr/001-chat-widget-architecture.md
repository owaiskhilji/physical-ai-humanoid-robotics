# ADR-001: Chat Widget Architecture

## Status

Accepted

## Date

2025-12-21

## Context

The project requires implementing a floating chat widget for Docusaurus documentation sites that provides AI-powered assistance with session management capabilities. The widget needs to integrate seamlessly with existing Docusaurus layouts while providing a professional conversational interface to a RAG backend system.

Key constraints and requirements include:
- Integration with Docusaurus v2.x and v3.x
- Use of Tailwind CSS for styling (as specified in requirements)
- Use of Lucide-react for icons (as specified in requirements)
- Client-side implementation without additional service costs
- Global availability across all documentation pages
- Session persistence across page navigation
- Responsive design for mobile and desktop

## Decision

We have made several interconnected architectural decisions that form the core of the chat widget implementation:

### Frontend Technology Stack
- **Framework**: JavaScript with JSX for component implementation
- **Styling**: Tailwind CSS for maintainable and lightweight styling with robotic/AI theme
- **Icons**: Lucide-react library for consistent iconography (Send, Trash, Bot icons)
- **State Management**: React hooks (useState, useEffect) with localStorage for session persistence

### Integration Approach
- **Docusaurus Integration**: Layout wrapper component approach by creating a custom theme component that wraps the main Docusaurus layout
- **Global Injection**: Component injection into Docusaurus Layout via theme system

### API Communication
- **Service Layer**: Dedicated API service module handling all backend communication
- **Configuration**: Environment variable-based configuration using `REACT_APP_API_URL`
- **Endpoints**: Standard HTTP requests to backend API endpoints for health check, session management, and messaging

### User Experience
- **Widget Pattern**: Floating action button (FAB) at bottom-right with collapsible/minimizable chat window
- **Visual Design**: Clear visual distinction between user and AI messages with distinct bubble styles
- **Interaction Features**: Auto-scrolling to latest message, loading indicators, and error handling

## Alternatives Considered

### Frontend Stack Alternatives
- **Alternative Stack**: React with TypeScript + Styled Components + Material UI
- **Tradeoff**: More type safety but additional complexity and dependencies
- **Reason Rejected**: Overkill for this use case, increases bundle size

### Integration Alternatives
- **Root-level injection**: More complex setup, harder to maintain
- **Plugin approach**: Overkill for a simple widget
- **Layout wrapper**: Clean, maintainable, follows Docusaurus patterns (Chosen)

### State Management Alternatives
- **Redux/Zustand**: More complex but centralized state management
- **Context API**: Could work but unnecessary complexity for this scope
- **Local state with localStorage**: Simple and effective for this use case (Chosen)

### Styling Alternatives
- **CSS modules**: Would require additional configuration
- **Styled components**: Additional dependencies and runtime overhead
- **Tailwind CSS**: Matches requirement and is lightweight (Chosen)

### API Integration Alternatives
- **Direct fetch calls in components**: Harder to maintain and test
- **Third-party HTTP libraries**: Additional dependencies
- **Dedicated service module**: Better organization and reusability (Chosen)

## Consequences

### Positive Consequences
- Lightweight implementation with minimal bundle impact
- Follows Docusaurus best practices for component integration
- Clean separation of concerns with dedicated API service
- Responsive design that works across device sizes
- Familiar patterns for developers (React hooks, Tailwind CSS)
- Session persistence without backend complexity
- Clear visual distinction between user and AI interactions

### Negative Consequences
- Client-side session storage limits cross-device synchronization
- Dependency on environment variable for API configuration
- Potential for increased complexity as features are added
- Local storage limitations for very large chat histories
- May require additional error handling for network conditions

## References

- `specs/004-docusaurus-chat-widget/plan.md` - Implementation plan and architecture overview
- `specs/004-docusaurus-chat-widget/research.md` - Detailed decision analysis and alternatives
- `specs/004-docusaurus-chat-widget/data-model.md` - Data models for session and message management
- `specs/004-docusaurus-chat-widget/contracts/chat-api-contract.md` - API endpoint specifications
- `specs/004-docusaurus-chat-widget/quickstart.md` - Integration patterns and component structure