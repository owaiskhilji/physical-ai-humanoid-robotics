import React from 'react';
import ChatbotMode from '../models/ChatbotMode';

/**
 * ModeIndicator - Visual indicator for the current chat mode with light theme and glassmorphism
 */
const ModeIndicator = ({ mode, selectedTextPreview = '', onSwitchToDefault = null }) => {
  // Create a ChatbotMode instance to get display information
  const chatbotMode = new ChatbotMode(mode, selectedTextPreview, true);

  if (mode === 'SELECTED_TEXT') {
    return (
      <div className="mode-indicator selected-text-mode flex flex-col gap-2 p-2 bg-white/70 backdrop-blur-sm border border-slate-200 rounded-lg mb-3 shadow-sm">
        <div className="flex justify-between items-center">
          <span className="indicator-badge bg-white/80 text-slate-700 px-2 py-1 rounded-full text-xs font-medium flex items-center">
            <span className="w-2 h-2 bg-slate-500 rounded-full mr-1"></span>
            🔍 Focus Mode
          </span>
          <button
            onClick={onSwitchToDefault}
            className="text-xs bg-white/80 hover:bg-white/90 text-slate-700 px-2 py-1 rounded-lg transition-colors border border-slate-200"
          >
            Default
          </button>
        </div>
        {selectedTextPreview && (
          <div className="selected-text-preview text-xs text-slate-600 bg-white/80 backdrop-blur-sm p-3 rounded-lg border border-slate-200 shadow-sm">
            <span className="font-medium text-slate-700">Context:</span> "{selectedTextPreview}"
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mode-indicator default-mode flex items-center justify-between p-1 bg-white/70 backdrop-blur-sm rounded-none shadow-sm" style={{ height: '24px' }}>
      <span className="indicator-badge bg-white/80 text-slate-700 px-2 py-0.5 rounded-full text-xs font-medium flex items-center">
        <span className="w-1.5 h-1.5 bg-slate-500 rounded-full mr-1"></span>
        📚 Default Mode
      </span>
      <div className="text-xs text-slate-500">
        Entire textbook
      </div>
    </div>
  );
};

export default ModeIndicator;