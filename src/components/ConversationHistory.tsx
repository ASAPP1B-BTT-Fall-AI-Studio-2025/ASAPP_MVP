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

// Helper to get icon based on conversation title/type
function getConversationIcon(title: string): string {
  const lowerTitle = title.toLowerCase();
  if (lowerTitle.includes('pasted')) return '📋';
  if (lowerTitle.includes('abcd') || lowerTitle.includes('dataset')) return '📊';
  if (lowerTitle.includes('conversations')) return '📚';
  if (lowerTitle.includes('defect') || lowerTitle.includes('issue')) return '⚠️';
  if (lowerTitle.includes('shipping')) return '📦';
  if (lowerTitle.includes('order')) return '🛒';
  if (lowerTitle.includes('account')) return '👤';
  if (lowerTitle.includes('subscription')) return '🔄';
  if (lowerTitle.includes('promo') || lowerTitle.includes('query') || lowerTitle.includes('storewide')) return '❓';
  if (lowerTitle.includes('troubleshoot') || lowerTitle.includes('site')) return '🔧';
  if (lowerTitle.includes('.json')) return '📄';
  if (lowerTitle.includes('.txt')) return '📝';
  if (lowerTitle.includes('.csv')) return '📋';
  return '💬';
}

export default function ConversationHistory({ 
  conversations, 
  selectedId, 
  onSelect 
}: ConversationHistoryProps) {
  return (
    <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-lg border border-blue-100 p-6 h-full">
      <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
        <span>📂</span> Conversation History
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
              className={`p-4 rounded-xl border cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-102 ${
                selectedId === conversation.id
                  ? 'border-blue-500 bg-gradient-to-r from-blue-100 to-purple-100 shadow-md'
                  : 'border-gray-200 hover:border-blue-300 bg-white'
              }`}
            >
              <div className="font-medium text-sm text-gray-800 mb-1 flex items-start gap-2">
                <span className="flex-shrink-0">{getConversationIcon(conversation.title)}</span>
                <span className="break-words leading-tight" title={conversation.title}>
                  {conversation.title}
                </span>
              </div>
              <div className="text-xs text-gray-500 pl-6">
                {conversation.date}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}