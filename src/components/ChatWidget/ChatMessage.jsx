import React from 'react';
import { Bot, User } from 'lucide-react';

/**
 * ChatMessage component for message display with visual distinction between user and AI messages
 */
const ChatMessage = ({ message, senderType, timestamp, status = 'delivered' }) => {
  const isUser = senderType === 'user';

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`
        max-w-[85%] rounded-lg p-3
        ${isUser
          ? 'bg-blue-500 text-white rounded-br-none'
          : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }
      `}>
        <div className="flex items-start space-x-2">
          {isUser ? (
            <User size={16} className="mt-0.5 text-white" />
          ) : (
            <Bot size={16} className="mt-0.5 text-blue-600" />
          )}
          <div className="flex-1">
            <div className="text-sm">{message}</div>
            <div className={`
              text-xs mt-1
              ${isUser ? 'text-blue-100' : 'text-gray-500'}
            `}>
              {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              {status === 'error' && !isUser && (
                <span className="ml-1 text-red-300">(Failed to deliver)</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;