# Data Model: Selected Text Mode

## Entities

### TextSelection
- **id**: string (unique identifier for the selection session)
- **content**: string (the actual selected text content)
- **startOffset**: number (start position in the text)
- **endOffset**: number (end position in the text)
- **timestamp**: datetime (when the selection was made)
- **metadata**: object (additional selection context)

### ChatbotMode
- **mode**: enum ['DEFAULT', 'SELECTED_TEXT'] (current operating mode)
- **selectedText**: string? (optional text when in SELECTED_TEXT mode)
- **isActive**: boolean (whether selection mode is currently active)
- **lastUpdated**: datetime (timestamp of last mode change)

### ChatRequest
- **message**: string (user's input message)
- **mode**: enum ['DEFAULT', 'SELECTED_TEXT'] (operating mode for this request)
- **selectedText**: string? (text content when in SELECTED_TEXT mode)
- **context**: object (additional context information)
- **userId**: string? (optional user identifier)

### ChatResponse
- **message**: string (AI's response message)
- **mode**: enum ['DEFAULT', 'SELECTED_TEXT'] (mode used for this response)
- **sourceContext**: string (the context used to generate the response)
- **confidence**: number (confidence score of the response)
- **timestamp**: datetime (when response was generated)

## State Transitions

### Mode State Machine
```
[DEFAULT] <---> [SELECTED_TEXT]
   ^                  ^
   |                  |
   +------------------+
     User selects/deselects text
```

- **DEFAULT** → **SELECTED_TEXT**: When user selects text in textbook content
- **SELECTED_TEXT** → **DEFAULT**: When user deselects text or navigates away
- **SELECTED_TEXT** → **SELECTED_TEXT**: When user selects different text (updates context)

## Validation Rules

### TextSelection Validation
- Content length: 1-1000 words (prevent overly large selections)
- Content must be non-empty when in SELECTED_TEXT mode
- Content must be properly sanitized to prevent injection

### Mode Validation
- Only one active mode at a time per user session
- Mode must match the presence/absence of selected text
- Mode transitions must be properly logged for debugging