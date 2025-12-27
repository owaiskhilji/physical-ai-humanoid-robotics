import React from 'react';
import { MessageCircle } from 'lucide-react';

/**
 * FloatingButton component with light theme styling
 */
const FloatingButton = ({ isVisible, onClick, hasUnreadMessages = false }) => {
  if (!isVisible) return null;

  return (
    <button
      onClick={onClick}
      className={`
        fixed bottom-6 right-6 z-[9999]
        w-14 h-14 rounded-full shadow-xl
        bg-white hover:bg-gray-50
        text-blue-500 flex items-center justify-center
        transition-all duration-300 ease-in-out
        transform hover:scale-105
        focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-opacity-50
        group
        border border-gray-200
        chat-widget
      `}
      aria-label="Open chat"
    >
      <MessageCircle size={24} className="text-blue-500" />
      {hasUnreadMessages && (
        <span className="absolute top-0 right-0 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center border-2 border-white">
          !
        </span>
      )}
      <span className="absolute -top-8 left-1/2 transform -translate-x-1/2 px-2 py-1 text-xs text-gray-700 bg-white rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-sm border border-gray-200">
        Chat with AI
      </span>
    </button>
  );
};

export default FloatingButton;