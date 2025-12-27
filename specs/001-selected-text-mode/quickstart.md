# Quickstart Guide: Selected Text Mode Implementation

## Overview
This guide provides step-by-step instructions for implementing the Selected Text Mode feature that allows users to highlight text in the textbook and have the chatbot respond using only that selected text as context.

## Frontend Implementation (Docusaurus)

### 1. Text Selection Detection
```javascript
// Add to your chat component or a global text selection handler
class TextSelectionManager {
  constructor() {
    this.currentSelection = null;
    this.mode = 'DEFAULT';
    this.setupSelectionListener();
  }

  setupSelectionListener() {
    document.addEventListener('mouseup', () => {
      const selection = window.getSelection();
      if (selection.toString().trim()) {
        this.handleTextSelection(selection);
      } else {
        this.handleTextDeselection();
      }
    });
  }

  handleTextSelection(selection) {
    const selectedText = selection.toString().trim();
    if (selectedText) {
      this.currentSelection = selectedText;
      this.mode = 'SELECTED_TEXT';
      this.updateUIIndicator(true);
      this.notifyChatComponent();
    }
  }

  handleTextDeselection() {
    this.currentSelection = null;
    this.mode = 'DEFAULT';
    this.updateUIIndicator(false);
    this.notifyChatComponent();
  }
}
```

### 2. Visual Indicator Component
```jsx
// Create a visual indicator for the chat UI
function ModeIndicator({ mode, selectedText }) {
  if (mode === 'SELECTED_TEXT') {
    return (
      <div className="mode-indicator selected-text-mode">
        <span className="indicator-badge">🔍 Focus Mode</span>
        <div className="selected-text-preview">
          {selectedText.substring(0, 60)}...
        </div>
      </div>
    );
  }
  return (
    <div className="mode-indicator default-mode">
      <span className="indicator-badge">📚 Default Mode</span>
    </div>
  );
}
```

### 3. Modified Chat API Calls
```javascript
async function sendChatMessage(message, mode, selectedText = null) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      mode,  // 'DEFAULT' or 'SELECTED_TEXT'
      selectedText: mode === 'SELECTED_TEXT' ? selectedText : null,
      context: {
        sessionId: getSessionId(),
        pageUrl: window.location.href
      }
    })
  });

  return response.json();
}
```

## Backend Implementation (FastAPI)

### 1. Updated Pydantic Models
```python
from pydantic import BaseModel
from typing import Optional, Literal

class ChatRequest(BaseModel):
    message: str
    mode: Literal["DEFAULT", "SELECTED_TEXT"]
    selectedText: Optional[str] = None
    context: dict = {}

class ChatResponse(BaseModel):
    id: str
    message: str
    modeUsed: Literal["DEFAULT", "SELECTED_TEXT"]
    sourceContext: str
    confidence: float
    timestamp: str
    metadata: dict
```

### 2. Modified Chat Endpoint
```python
from fastapi import APIRouter, HTTPException
from typing import Literal
import logging

router = APIRouter()

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        if request.mode == "SELECTED_TEXT":
            if not request.selectedText or len(request.selectedText.strip()) == 0:
                raise HTTPException(status_code=400, detail="Selected text is required in SELECTED_TEXT mode")

            # Use only the selected text as context
            response = await process_with_selected_context(
                request.message,
                request.selectedText
            )
            mode_used = "SELECTED_TEXT"
        else:
            # Use normal Qdrant search
            response = await process_with_qdrant_search(request.message)
            mode_used = "DEFAULT"

        return ChatResponse(
            id=generate_response_id(),
            message=response.message,
            modeUsed=mode_used,
            sourceContext=response.context,
            confidence=response.confidence,
            timestamp=get_current_timestamp(),
            metadata=response.metadata
        )
    except Exception as e:
        logging.error(f"Chat processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. Mode Status Endpoint
```python
class ModeStatus(BaseModel):
    mode: Literal["DEFAULT", "SELECTED_TEXT"]
    selectedText: Optional[str]
    isActive: bool
    lastUpdated: str

@router.get("/api/chat/mode-status")
async def get_mode_status(session_id: str) -> ModeStatus:
    # Retrieve mode status from session store
    status = await get_session_mode_status(session_id)
    return ModeStatus(**status)
```

## Integration Steps

### 1. Frontend Integration
1. Add text selection detection to textbook content area
2. Update chat component to pass mode and selected text to API
3. Add visual indicator to chat UI
4. Update UI to reflect current mode state

### 2. Backend Integration
1. Update existing chat endpoint to handle mode parameter
2. Implement selected text processing logic
3. Maintain backward compatibility with default mode
4. Add mode status endpoint for UI synchronization

### 3. Testing
1. Test text selection detection and deselection
2. Verify mode switching behavior
3. Validate strict grounding in selected text mode
4. Test visual indicator updates
5. Verify performance with large text selections