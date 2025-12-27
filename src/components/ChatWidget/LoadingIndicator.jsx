import React from 'react';

/**
 * LoadingIndicator component for AI processing states with light theme
 */
const LoadingIndicator = ({ message = "Thinking..." }) => {
  return (
    <div className="flex items-center space-x-2 text-gray-600 text-sm">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
      </div>
      <span>{message}</span>
    </div>
  );
};

export default LoadingIndicator;