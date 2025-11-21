'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import ConversationHistory from '@/components/ConversationHistory';
import ConversationInput from '@/components/ConversationInput';
import FileUpload from '@/components/FileUpload';
import ExtractedFieldsDisplay from '@/components/ExtractedFieldsDisplay';
import { ExtractedFields } from '@/lib/fieldExtractor';

interface Conversation {
  id: string;
  title: string;
  date: string;
  preview: string;
}

const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string>();
  const [extractedFields, setExtractedFields] = useState<ExtractedFields | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Load conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await fetch(`${FASTAPI_URL}/conversations`);
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      alert('Failed to connect to backend. Make sure FastAPI server is running on http://localhost:8000');
    }
  };

  const processConversation = async (text: string, fileName?: string) => {
    setIsProcessing(true);
    setIsLoading(true);
    
    try {
      // Extract fields using FastAPI
      const extractResponse = await fetch(`${FASTAPI_URL}/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, fileName }),
      });

      if (!extractResponse.ok) {
        throw new Error('Failed to extract fields');
      }

      const extractedData = await extractResponse.json();
      setExtractedFields(extractedData);

      // Save conversation using FastAPI
      const saveResponse = await fetch(`${FASTAPI_URL}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: fileName || `Conversation ${conversations.length + 1}`,
          content: text,
          fileName,
        }),
      });

      if (saveResponse.ok) {
        const savedConversation = await saveResponse.json();
        setConversations(prev => [savedConversation, ...prev]);
        setSelectedConversationId(savedConversation.id);
      }
    } catch (error) {
      console.error('Failed to process conversation:', error);
      alert('Failed to process conversation. Make sure FastAPI server is running on http://localhost:8000');
    } finally {
      setIsProcessing(false);
      setIsLoading(false);
    }
  };

  const handleTextSubmit = (text: string) => {
    processConversation(text);
  };

  const handleFileUpload = (content: string, fileName: string) => {
    processConversation(content, fileName);
  };

  const handleConversationSelect = async (conversationId: string) => {
    setSelectedConversationId(conversationId);
    
    try {
      const response = await fetch(`${FASTAPI_URL}/conversations/${conversationId}`);
      if (response.ok) {
        const conversation = await response.json();
        setExtractedFields(conversation.extractedFields);
      }
    } catch (error) {
      console.error('Failed to load conversation details:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
          {/* Left Sidebar - Conversation History */}
          <div className="lg:col-span-1">
            <ConversationHistory
              conversations={conversations}
              selectedId={selectedConversationId}
              onSelect={handleConversationSelect}
            />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Input Methods */}
            <div className="space-y-6">
              <ConversationInput
                onSubmit={handleTextSubmit}
                isProcessing={isProcessing}
              />
              
              <div className="text-center text-gray-500 text-sm">
                — OR —
              </div>
              
              <FileUpload
                onFileUpload={handleFileUpload}
                isProcessing={isProcessing}
              />
            </div>
          </div>

          {/* Right Sidebar - Extracted Fields */}
          <div className="lg:col-span-1">
            <ExtractedFieldsDisplay
              fields={extractedFields}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Optional Bottom Section for Future Features */}
        <div className="mt-12 p-8 bg-gradient-to-r from-white to-gray-50 rounded-xl shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Future Features
          </h3>
          <p className="text-gray-600">
            This section can be used to visualize features explored during EDA for batch conversation processing, 
            analytics dashboards, or additional extraction capabilities.
          </p>
        </div>
      </main>
    </div>
  );
}