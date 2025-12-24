import React, { useState, useRef } from 'react';
import { Send, Trash2 } from 'lucide-react';

/**
 * ChatInput component with send functionality and keyboard navigation support
 */
const ChatInput = ({ onSend, onClear, disabled = false, placeholder = "Type your message..." }) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef(null);
  const sendButtonRef = useRef(null);
  const clearButtonRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSend(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled) {
        handleSubmit(e);
      }
    }

    // Allow Shift+Enter for new line
    if (e.key === 'Enter' && e.shiftKey) {
      // Allow default behavior for new line
      return;
    }

    // Tab navigation enhancement: Allow cycling through controls
    if (e.key === 'Tab') {
      // Handle tab navigation manually if needed
    }
  };

  // Focus the input when component mounts or becomes enabled
  React.useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  return (
    <div className="p-4 border-t border-gray-200 bg-white">
      <form onSubmit={handleSubmit} className="flex items-end space-x-2">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className={`
              w-full px-3 py-2 border rounded-lg resize-none
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
              disabled:bg-gray-100 disabled:cursor-not-allowed
              text-sm
            `}
            rows="1"
            style={{ minHeight: '40px', maxHeight: '100px' }}
            aria-label="Type your message"
            role="textbox"
            aria-multiline="true"
          />
        </div>
        <div className="flex flex-col space-y-2">
          <button
            ref={sendButtonRef}
            type="submit"
            disabled={disabled || !inputValue.trim()}
            className={`
              p-2 rounded-full
              ${inputValue.trim() && !disabled
                ? 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-2 focus:ring-blue-300'
                : 'bg-gray-200 text-gray-400'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
              focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-opacity-50
            `}
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
          <button
            ref={clearButtonRef}
            type="button"
            onClick={onClear}
            disabled={disabled}
            className={`
              p-2 rounded-full
              bg-gray-200 text-gray-600 hover:bg-gray-300 focus:ring-2 focus:ring-gray-300
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
              focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-opacity-50
            `}
            aria-label="Clear chat"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInput;