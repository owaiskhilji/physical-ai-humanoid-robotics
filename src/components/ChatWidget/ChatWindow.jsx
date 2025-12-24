import React from 'react';
import { X, Minus, Bot } from 'lucide-react';

/**
 * ChatWindow component with Tailwind CSS styling
 */
const ChatWindow = ({
  isVisible,
  isMinimized,
  onClose,
  onMinimize,
  title = "AI Assistant",
  children,
  showHeader = true
}) => {
  if (!isVisible || isMinimized) return null;

  return (
    <div className={`
      fixed bottom-20 right-6 z-[9998]
      w-80 h-[500px] max-h-[80vh] flex flex-col
      bg-white rounded-lg shadow-xl border border-gray-200
      transition-all duration-300 ease-in-out
      transform
    `}>
      {showHeader && (
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
          <div className="flex items-center space-x-2">
            <Bot size={20} className="text-blue-600" />
            <h3 className="font-semibold text-gray-800">{title}</h3>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={onMinimize}
              className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-200 transition-colors"
              aria-label="Minimize chat"
            >
              <Minus size={16} />
            </button>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-200 transition-colors"
              aria-label="Close chat"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}
      <div className="flex-1 overflow-hidden flex flex-col">
        {children}
      </div>
    </div>
  );
};

export default ChatWindow;