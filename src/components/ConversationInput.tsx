'use client';

import { useState } from 'react';

interface ConversationInputProps {
  onSubmit: (text: string) => void;
  isProcessing: boolean;
}

export default function ConversationInput({ onSubmit, isProcessing }: ConversationInputProps) {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !isProcessing) {
      onSubmit(text.trim());
      setText('');
    }
  };

  return (
    <div className="bg-gradient-to-br from-white to-purple-50 rounded-xl shadow-lg border border-purple-100 p-6">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">
        Input Conversation
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="conversation-text" className="sr-only">
            Conversation Text
          </label>
          <textarea
            id="conversation-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or type your conversation text here..."
            className="w-full h-32 p-4 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
            disabled={isProcessing}
          />
        </div>
        
        <button
          type="submit"
          disabled={!text.trim() || isProcessing}
          className={`w-full py-3 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 ${
            !text.trim() || isProcessing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 shadow-lg'
          }`}
        >
          {isProcessing ? 'Processing...' : 'Extract Fields'}
        </button>
      </form>
    </div>
  );
}