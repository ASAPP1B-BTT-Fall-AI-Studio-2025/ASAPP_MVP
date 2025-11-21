'use client';

interface ConversationHistoryProps {
  conversations: Array<{
    id: string;
    title: string;
    date: string;
    preview: string;
  }>;
  selectedId?: string;
  onSelect: (id: string) => void;
}

export default function ConversationHistory({ 
  conversations, 
  selectedId, 
  onSelect 
}: ConversationHistoryProps) {
  return (
    <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-lg border border-blue-100 p-6 h-full">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">
        Conversation History
      </h2>
      
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-8">
            No conversations yet
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => onSelect(conversation.id)}
              className={`p-4 rounded-xl border cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-105 ${
                selectedId === conversation.id
                  ? 'border-blue-500 bg-gradient-to-r from-blue-100 to-purple-100 shadow-md'
                  : 'border-gray-200 hover:border-blue-300 bg-white'
              }`}
            >
              <div className="font-medium text-sm text-gray-800 mb-1">
                {conversation.title}
              </div>
              <div className="text-xs text-gray-500 mb-2">
                {conversation.date}
              </div>
              <div className="text-xs text-gray-600 truncate">
                {conversation.preview}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}