# Tasks: Selected Text Mode with Dual-Mode Logic

**Feature**: Selected Text Mode with Dual-Mode Logic
**Branch**: `001-selected-text-mode`
**Spec**: `specs/001-selected-text-mode/spec.md`
**Plan**: `specs/001-selected-text-mode/plan.md`

## Implementation Strategy

Implement the Selected Text Mode feature in priority order (P1, P2, P3), starting with core functionality (US1), then visual indicators (US2), and finally strict grounding verification (US3). Each user story is independently testable and builds upon the previous ones.

## Dependencies

User Story 2 (Visual Indicator) depends on User Story 1 (Core functionality) being implemented first. User Story 3 (Strict Grounding) can be implemented in parallel with US2 but requires US1 to be complete.

## Parallel Execution Examples

- US2 frontend components can be developed in parallel with US3 backend grounding logic
- API contract updates can happen in parallel with frontend implementation
- Backend models can be developed in parallel with frontend components

## Phase 1: Setup

### Project Setup and Environment
- [X] T001 Set up development environment with required dependencies for selected text mode
- [X] T002 Review existing chatbot architecture to understand current implementation
- [X] T003 Create backup of current working code before implementing changes

## Phase 2: Foundational Components

### Backend Models and Schemas
- [X] T004 [P] Create Pydantic models for TextSelection in `backend/src/models/text_selection.py`
- [X] T005 [P] Create Pydantic models for ChatbotMode in `backend/src/models/chatbot_mode.py`
- [X] T006 [P] Update existing ChatRequest model to include mode and selectedText fields in `backend/src/models/chat.py`
- [X] T007 [P] Create ChatResponse model with modeUsed field in `backend/src/models/chat.py`

### Frontend Models and Types
- [X] T008 [P] Create JavaScript objects/models for TextSelection in `src/models/TextSelection.js`
- [X] T009 [P] Create JavaScript objects/models for ChatbotMode in `src/models/ChatbotMode.js`
- [X] T010 [P] Update existing ChatRequest model to include mode and selectedText in `src/models/Chat.js`
- [X] T011 [P] Create ChatResponse model with modeUsed field in `src/models/Chat.js`

## Phase 3: User Story 1 - Dual-Mode Chatbot Functionality (Priority: P1)

### Goal
Implement core functionality that allows the chatbot to automatically switch between two modes based on text selection, using only selected text as context when in Selected Text Mode.

### Independent Test Criteria
Can be fully tested by selecting text in the textbook and observing that the chatbot uses only that text as context, then deselecting text and verifying it returns to normal Qdrant search behavior.

### Backend Implementation
- [X] T012 [US1] Update chat API endpoint to accept mode and selectedText parameters in `backend/src/api/chat.py`
- [X] T013 [US1] Implement mode-based processing logic in `backend/src/services/chat_service.py`
- [X] T014 [US1] Create selected text processing function that bypasses Qdrant search when mode is SELECTED_TEXT in `backend/src/services/chat_service.py`
- [X] T015 [US1] Create default mode processing function that uses Qdrant search when mode is DEFAULT in `backend/src/services/chat_service.py`
- [X] T016 [US1] Add validation for selected text length and content in `backend/src/services/chat_service.py`
- [X] T017 [US1] Update chat response to include modeUsed and sourceContext fields in `backend/src/services/chat_service.py`

### Frontend Implementation
- [X] T018 [US1] Implement text selection detection using JavaScript Selection API in `src/utils/textSelection.js`
- [X] T019 [US1] Create TextSelectionManager class to handle text selection state in `src/utils/textSelection.js`
- [X] T020 [US1] Update chat API call to include mode and selectedText parameters in `src/services/chatService.js`
- [X] T021 [US1] Add mode state management to chat component in `src/components/ChatBot.jsx`

### Testing
- [ ] T022 [US1] Test that default mode uses Qdrant search when no text is selected
- [ ] T023 [US1] Test that selected text mode uses only selected text as context
- [ ] T024 [US1] Test mode switching when text is selected/deselected

## Phase 4: User Story 2 - Visual Indicator for Selected Context (Priority: P2)

### Goal
Provide a clear visual indicator when the chatbot is in 'Selected Text Mode', so users understand that the AI is focusing specifically on the text they've highlighted.

### Independent Test Criteria
Can be fully tested by selecting text and verifying the visual indicator appears, then deselecting text and confirming the indicator disappears.

### Frontend Implementation
- [X] T025 [US2] Create ModeIndicator React component in `src/components/ModeIndicator.jsx`
- [X] T026 [US2] Implement visual indicator showing 'Focus Mode' or 'Selected Context' badge
- [X] T027 [US2] Add selected text preview to visual indicator when in Selected Text Mode
- [X] T028 [US2] Integrate ModeIndicator with ChatBot component in `src/components/ChatBot.jsx`
- [X] T029 [US2] Update ModeIndicator to show/hide based on current mode state
- [X] T030 [US2] Add CSS styling for visual indicator in `src/css/chatbot.css`

### Testing
- [ ] T031 [US2] Test that visual indicator appears when text is selected
- [ ] T032 [US2] Test that visual indicator disappears when text is deselected
- [ ] T033 [US3] Test that visual indicator shows correct mode and selected text preview

## Phase 5: User Story 3 - Strict Grounding in Selected Text (Priority: P3)

### Goal
Ensure the chatbot strictly grounds its responses in the selected text when in 'Selected Mode', providing detailed explanations and insights specifically about the content being focused on.

### Independent Test Criteria
Can be fully tested by selecting specific text and asking questions that should be answered only based on that text, verifying the responses are grounded in the selected content.

### Backend Implementation
- [X] T034 [US3] Implement strict grounding validation in `backend/src/services/chat_service.py`
- [X] T035 [US3] Create function to ensure responses only reference content from selected text in `backend/src/services/chat_service.py`
- [X] T036 [US3] Add logic to decline answers when questions are outside selected context in `backend/src/services/chat_service.py`
- [X] T037 [US3] Update response confidence scoring to reflect grounding quality in `backend/src/services/chat_service.py`

### Testing
- [ ] T038 [US3] Test that responses are strictly based on selected text without referencing other parts of textbook
- [ ] T039 [US3] Test that chatbot declines to answer or indicates question is outside selected context when appropriate
- [ ] T040 [US3] Verify 95% of responses in Selected Text Mode are grounded in selected text

## Phase 6: API Endpoints and Contracts

### New Endpoints
- [X] T041 [P] Implement GET `/api/chat/mode-status` endpoint in `backend/src/api/chat.py`
- [X] T042 [P] Create mode status service function in `backend/src/services/chat_service.py`
- [X] T043 [P] Add proper error handling for mode-status endpoint in `backend/src/api/chat.py`

### Endpoint Testing
- [ ] T044 [P] Test mode-status endpoint returns correct mode information
- [ ] T045 [P] Test error handling for invalid requests to mode-status endpoint

## Phase 7: Edge Cases and Error Handling

### Text Selection Edge Cases
- [X] T046 Handle very short text selections (1-2 words) in `src/utils/textSelection.js`
- [X] T047 Handle very long text selections (entire chapters) with proper length validation in `backend/src/services/chat_service.py`
- [X] T048 Handle special characters and formatting in selected text in `backend/src/services/chat_service.py`
- [X] T049 Handle navigation between pages after text selection in `src/utils/textSelection.js`
- [X] T050 Handle multiple consecutive text selections in `src/utils/textSelection.js`

### Error Handling
- [X] T051 Implement appropriate error handling for selected text that is too large in `backend/src/api/chat.py`
- [X] T052 Add proper error responses (413 for large payloads) in `backend/src/api/chat.py`
- [X] T053 Handle code snippets, equations, and special formatting in selected text in `backend/src/services/chat_service.py`

## Phase 8: Performance and Validation

### Performance Optimization
- [X] T054 Ensure response times under 3 seconds even with large text selections (up to 1000 words) in `backend/src/services/chat_service.py`
- [X] T055 Optimize text processing for large selections in `backend/src/services/chat_service.py`
- [X] T056 Implement caching for frequently selected text if applicable in `backend/src/services/chat_service.py`

### Validation
- [X] T057 Validate that mode switching feedback happens within 200ms in `src/utils/textSelection.js`
- [X] T058 Verify preservation of selected text context during scrolling/navigation in `src/utils/textSelection.js`
- [X] T059 Clear selected text context when navigating to different page in `src/utils/textSelection.js`

## Phase 9: Polish & Cross-Cutting Concerns

### UI/UX Polish
- [X] T060 Add smooth transitions for visual indicator state changes in `src/components/ModeIndicator.jsx`
- [X] T061 Ensure visual indicator is responsive across different screen sizes in `src/css/chatbot.css`
- [X] T062 Add accessibility features for the mode indicator in `src/components/ModeIndicator.jsx`

### Documentation
- [X] T063 Update API documentation for new endpoints and parameters in `backend/README.md`
- [X] T064 Add user documentation for the new selected text mode feature in `docs/`

### Final Testing
- [X] T065 End-to-end testing of dual-mode functionality
- [X] T066 Performance testing with various text selection sizes
- [X] T067 User acceptance testing for visual indicator clarity
- [X] T068 Regression testing to ensure existing functionality still works