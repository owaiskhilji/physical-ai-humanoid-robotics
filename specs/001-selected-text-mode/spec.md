# Feature Specification: Selected Text Mode with Dual-Mode Logic

**Feature Branch**: `001-selected-text-mode`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "My goal is to implement 'Selected Text Mode' (Requirement #2) using a 'Dual-Mode' logic. Please update the specifications and tasks accordingly:

Default Mode: If no text is selected, the chatbot must function exactly as it does now (retrieving answers via Qdrant database search).

Selected Mode: Whenever I select (highlight) any text in the textbook, the chatbot should detect it and skip the Qdrant search. Instead, it must use only the selected text as its 'Source Context' for the LLM (Strict Grounding).

UI/UX: Provide a clear visual indicator (e.g., a 'Focus Mode' or 'Selected Context' badge) on the Chatbot UI whenever text is selected so the user knows the AI is focusing on that specific part.

Implementation: Identify and include all necessary architectural or API changes required in the Frontend (Docusaurus) and Backend (FastAPI). Ensure the implementation adheres to the project Constitution's principles of 'Technical Accuracy' and 'Free-tier' constraints"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Dual-Mode Chatbot Functionality (Priority: P1)

As a textbook reader, I want the chatbot to automatically switch between two modes based on text selection, so that I can get contextually relevant answers whether I'm browsing the entire textbook or focusing on specific content.

**Why this priority**: This is the core functionality that enables the dual-mode experience, providing the primary value proposition of the feature.

**Independent Test**: Can be fully tested by selecting text in the textbook and observing that the chatbot uses only that text as context, then deselecting text and verifying it returns to normal Qdrant search behavior.

**Acceptance Scenarios**:

1. **Given** no text is selected in the textbook, **When** I ask a question in the chatbot, **Then** the chatbot retrieves answers via Qdrant database search as it does currently
2. **Given** I have selected text in the textbook, **When** I ask a question in the chatbot, **Then** the chatbot uses only the selected text as source context for the LLM response

---

### User Story 2 - Visual Indicator for Selected Context (Priority: P2)

As a user, I want to see a clear visual indicator when the chatbot is in 'Selected Text Mode', so I understand that the AI is focusing specifically on the text I've highlighted.

**Why this priority**: This provides essential UX feedback to ensure users understand the current mode of operation and can trust the responses are contextually appropriate.

**Independent Test**: Can be fully tested by selecting text and verifying the visual indicator appears, then deselecting text and confirming the indicator disappears.

**Acceptance Scenarios**:

1. **Given** I have selected text in the textbook, **When** I look at the chatbot UI, **Then** I see a clear visual indicator (e.g., 'Focus Mode' or 'Selected Context' badge) showing the chatbot is using only the selected text as context
2. **Given** the chatbot has the visual indicator showing 'Selected Context', **When** I deselect the text, **Then** the visual indicator disappears and the chatbot returns to normal mode

---

### User Story 3 - Strict Grounding in Selected Text (Priority: P3)

As a user, I want the chatbot to strictly ground its responses in the selected text when in 'Selected Mode', so I can get detailed explanations and insights specifically about the content I'm focusing on.

**Why this priority**: This ensures the quality and relevance of responses when users want to dive deep into specific content.

**Independent Test**: Can be fully tested by selecting specific text and asking questions that should be answered only based on that text, verifying the responses are grounded in the selected content.

**Acceptance Scenarios**:

1. **Given** I have selected specific text about a physics concept, **When** I ask a question about that concept, **Then** the chatbot response is strictly based on the selected text without referencing other parts of the textbook
2. **Given** I have selected text in one chapter, **When** I ask about content from a different chapter, **Then** the chatbot either declines to answer or indicates the question is outside the selected context

---

### Edge Cases


- What happens when the selected text is very short or contains only special characters?
- How does the system handle very long text selections (e.g., entire chapters)?
- What occurs when the user selects text and then navigates to a different page before asking a question?
- How does the system behave when multiple text selections are made consecutively?
- What happens if the selected text contains code snippets, equations, or other special formatting?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST detect when text is selected in the textbook content area
- **FR-002**: System MUST automatically switch to 'Selected Text Mode' when text is highlighted and revert to 'Default Mode' when text is deselected
- **FR-003**: System MUST bypass Qdrant database search when in 'Selected Text Mode' and use only the selected text as context
- **FR-004**: System MUST provide strict grounding of LLM responses to the selected text when in 'Selected Text Mode'
- **FR-005**: System MUST display a clear visual indicator on the chatbot UI when in 'Selected Text Mode'
- **FR-006**: System MUST maintain existing Qdrant search functionality when no text is selected ('Default Mode')
- **FR-007**: System MUST handle text selections of varying lengths without performance degradation
- **FR-008**: System MUST preserve the selected text context even if the user scrolls or navigates within the same page
- **FR-009**: System MUST clear the selected text context when the user navigates to a different page or deselects text
- **FR-010**: System MUST provide appropriate error handling when selected text is too large to process

### Key Entities

- **Text Selection**: The highlighted text content from the textbook that serves as context for the LLM
- **Chatbot Mode**: The operational state (Default Mode or Selected Text Mode) that determines how the system processes user queries
- **Visual Indicator**: The UI element that shows the current mode of operation to the user
- **Context Source**: The data source used for grounding LLM responses (either Qdrant database or selected text)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can seamlessly switch between Default Mode and Selected Text Mode with immediate visual feedback (indicator appears/disappears within 200ms of text selection/deselection)
- **SC-002**: When in Selected Text Mode, 95% of chatbot responses are strictly grounded in the selected text without referencing other content
- **SC-003**: Users report 80% higher satisfaction with chatbot responses when using Selected Text Mode for specific content queries compared to Default Mode
- **SC-004**: The system maintains response times under 3 seconds even with large text selections (up to 1000 words)
- **SC-005**: 90% of users correctly understand when the chatbot is operating in Selected Text Mode based on the visual indicator
