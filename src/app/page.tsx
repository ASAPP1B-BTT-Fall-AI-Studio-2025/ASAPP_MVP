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
  const [bulkResults, setBulkResults] = useState<ExtractedFields[]>([]);

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
      // Try bulk extraction first (handles both single and multiple conversations)
      const bulkResponse = await fetch(`${FASTAPI_URL}/extract-bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, fileName }),
      });

      if (!bulkResponse.ok) {
        throw new Error('Failed to extract fields');
      }

      const bulkData = await bulkResponse.json();
      const results = bulkData.conversations || [];
      
      // Store bulk results for download
      setBulkResults(results);
      
      // Use the first result to display
      if (results.length > 0) {
        setExtractedFields(results[0]);
      }

      // Save ONE entry for the upload with summary of extracted fields
      if (results.length > 0) {
        try {
          // Create a concise, clean title
          let convTitle = '';
          const baseName = fileName ? fileName.replace(/\.[^/.]+$/, '') : ''; // Remove extension
          const format = bulkData.format || 'text';
          const total = results.length;
          const firstResult = results[0];
          const category = firstResult?.metadata?.category;
          
          // Get the most common conversation type for multi-convo uploads
          const categories = bulkData.categories || {};
          const topCategory = Object.entries(categories)
            .sort((a, b) => (b[1] as number) - (a[1] as number))[0];
          const topCategoryName = topCategory 
            ? (topCategory[0] as string).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
            : '';
          
          // Single conversation
          if (total === 1) {
            // Get just the main flow type for ABCD data
            const flow = firstResult?.metadata?.flow;
            const mainCategory = flow 
              ? flow.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())
              : '';
            
            if (mainCategory) {
              convTitle = mainCategory;
            } else if (baseName) {
              convTitle = baseName;
            } else {
              convTitle = `Chat ${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
            }
          }
          // Multiple conversations from ABCD dataset
          else if (format === 'abcd') {
            // Clean format: "filename (50) - Mostly Product Defect"
            if (topCategoryName) {
              convTitle = `${baseName || 'ABCD'} (${total}) • ${topCategoryName}`;
            } else {
              convTitle = `${baseName || 'ABCD Dataset'} (${total} convos)`;
            }
          }
          // Multiple conversations from file
          else if (baseName) {
            convTitle = `${baseName} (${total} convos)`;
          }
          // Fallback for pasted multi-conversation text
          else {
            convTitle = `${total} Conversations`;
          }
          
          const saveResponse = await fetch(`${FASTAPI_URL}/conversations`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              title: convTitle,
              content: JSON.stringify({ totalConversations: results.length, results }),
              fileName,
              // Use first result's extracted fields as summary
              extractedFields: {
                email: results[0]?.email || 'NA',
                phone: results[0]?.phone || 'NA',
                zipCode: results[0]?.zipCode || 'NA',
                orderId: results[0]?.orderId || 'NA',
              }
            }),
          });

          if (saveResponse.ok) {
            const savedConversation = await saveResponse.json();
            setConversations(prev => [savedConversation, ...prev]);
            setSelectedConversationId(savedConversation.id);
          }
        } catch (error) {
          console.error('Failed to save conversation:', error);
        }
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
        
        // Check if this conversation has stored bulk results
        try {
          const content = JSON.parse(conversation.content);
          if (content.results && Array.isArray(content.results)) {
            setBulkResults(content.results);
          } else {
            // Single conversation - clear bulk results and show single fields
            setBulkResults([]);
          }
        } catch {
          // Not JSON content - clear bulk results
          setBulkResults([]);
        }
      }
    } catch (error) {
      console.error('Failed to load conversation details:', error);
    }
  };

  const handleDownloadResults = () => {
    if (bulkResults.length === 0) {
      alert('No results to download');
      return;
    }

    // Create download object
    const downloadData = {
      fileName: 'extractify_results',
      exportDate: new Date().toISOString(),
      totalRecords: bulkResults.length,
      results: bulkResults
    };

    // Convert to JSON string
    const jsonString = JSON.stringify(downloadData, null, 2);
    
    // Create blob and download
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `extractify_results_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-indigo-50 to-purple-100">
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
          <div className="lg:col-span-3 space-y-6">
            {/* Input Methods */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ConversationInput
                onSubmit={handleTextSubmit}
                isProcessing={isProcessing}
              />
              
              <FileUpload
                onFileUpload={handleFileUpload}
                isProcessing={isProcessing}
              />
            </div>
          </div>
        </div>

        {/* Bottom Section - Extracted Fields Results */}
        <div className="mt-8">
          <ExtractedFieldsDisplay
            fields={extractedFields}
            isLoading={isLoading}
            bulkResults={bulkResults}
            onDownload={handleDownloadResults}
          />
        </div>
      </main>
    </div>
  );
}