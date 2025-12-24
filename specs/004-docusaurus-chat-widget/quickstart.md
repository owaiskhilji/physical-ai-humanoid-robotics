# Quickstart Guide: Docusaurus Chat Widget

## Overview
This guide provides instructions for implementing and integrating the floating chat widget into your Docusaurus documentation site.

## Prerequisites
- Docusaurus v2.x or v3.x project
- Node.js 16+ installed
- Backend API with chat endpoints available
- Tailwind CSS configured in your Docusaurus project

## Installation Steps

### 1. Install Dependencies
```bash
npm install lucide-react
# If Tailwind CSS is not already installed:
npm install -D tailwindcss postcss autoprefixer
```

### 2. Environment Configuration
Add the API URL to your environment variables:

Create or update `.env` file in your Docusaurus root:
```
REACT_APP_API_URL=http://localhost:8000/api
```

### 3. Component Files
Create the following component files in your Docusaurus project:

```
src/
├── components/
│   ├── ChatWidget/
│   │   ├── ChatWidget.jsx
│   │   ├── ChatWindow.jsx
│   │   ├── ChatMessage.jsx
│   │   ├── ChatInput.jsx
│   │   └── FloatingButton.jsx
│   └── APIService.js
```

### 4. API Service Setup
Create an API service to handle communication with the backend:

```javascript
// src/components/APIService.js
class APIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
  }

  async healthCheck() {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }

  async createSession(sessionData) {
    const response = await fetch(`${this.baseURL}/v1/chat/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sessionData),
    });
    return response.json();
  }

  // Additional API methods...
}

export default new APIService();
```

### 5. Main Widget Component
The main ChatWidget component will manage state and coordinate sub-components.

## Integration with Docusaurus

### Method 1: Layout Wrapper (Recommended)
Create a layout wrapper to inject the chat widget globally:

```javascript
// src/theme/Layout/index.js
import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import ChatWidget from '@site/src/components/ChatWidget/ChatWidget';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <ChatWidget />
    </>
  );
}
```

### Method 2: Root Injection
Alternatively, inject the widget at the root level using Docusaurus' root injection mechanism.

## Configuration Options
The chat widget can be configured with the following options:

- `initiallyVisible`: Whether the chat window is initially open (default: false)
- `widgetTitle`: Title displayed in the chat header (default: "AI Assistant")
- `botIcon`: Icon to use for the bot messages (default: Bot icon from Lucide)
- `theme`: Color theme for the widget (default: follows site theme)

## Testing
1. Start your Docusaurus development server: `npm run start`
2. Verify the floating chat button appears at the bottom-right
3. Click the button to open the chat window
4. Test creating a session and sending messages
5. Verify session history persists across page navigation
6. Test clearing the chat session

## Troubleshooting
- If the widget doesn't appear, check that you've properly wrapped the Layout component
- If API calls fail, verify the `REACT_APP_API_URL` is correctly set
- If styling doesn't apply, ensure Tailwind CSS is properly configured in your Docusaurus project

## Next Steps
- Customize the widget's appearance to match your site's design
- Add additional functionality like message history persistence
- Implement error handling and loading states
- Add analytics to track user engagement with the chat widget