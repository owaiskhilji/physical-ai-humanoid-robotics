import React from 'react';
import { Bot, User } from 'lucide-react';

/**
 * ChatMessage component for message display with light theme and visual distinction between user and AI messages
 */
const ChatMessage = ({ message, senderType, timestamp, status = 'delivered' }) => {
  const isUser = senderType === 'user';

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`
        max-w-[85%] rounded-xl p-4 shadow-sm
        ${isUser
          ? 'bg-blue-500 text-white rounded-br-none border border-blue-200'
          : 'bg-white/80 backdrop-blur-sm text-gray-800 rounded-bl-none border border-gray-100'
        }
      `}>
        <div className="flex items-start space-x-2">
          {isUser ? (
            <User size={16} className="mt-0.5 text-white" />
          ) : (
            <Bot size={16} className="mt-0.5 text-blue-500" />
          )}
          <div className="flex-1">
            <div className="text-sm">{message}</div>
            <div className={`
              text-xs mt-1
              ${isUser ? 'text-blue-100' : 'text-gray-500'}
            `}>
              {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              {status === 'error' && !isUser && (
                <span className="ml-1 text-red-400">(Failed to deliver)</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;