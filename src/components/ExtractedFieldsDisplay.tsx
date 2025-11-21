'use client';

import { ExtractedFields } from '@/lib/fieldExtractor';

interface ExtractedFieldsDisplayProps {
  fields: ExtractedFields | null;
  isLoading: boolean;
}

export default function ExtractedFieldsDisplay({ 
  fields, 
  isLoading 
}: ExtractedFieldsDisplayProps) {
  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-white to-yellow-50 rounded-xl shadow-lg border border-yellow-100 p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">
          Extracted Fields
        </h2>
        <div className="animate-pulse space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-4 bg-yellow-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!fields) {
    return (
      <div className="bg-gradient-to-br from-white to-yellow-50 rounded-xl shadow-lg border border-yellow-100 p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">
          Extracted Fields
        </h2>
        <div className="text-gray-500 text-center py-8">
          Upload a conversation file to see extracted fields
        </div>
      </div>
    );
  }

  const fieldEntries = [
    { label: 'Email', value: fields.email, key: 'email' },
    { label: 'Phone', value: fields.phone, key: 'phone' },
    { label: 'ZIP Code', value: fields.zipCode, key: 'zipCode' },
    { label: 'Order ID', value: fields.orderId, key: 'orderId' },
  ];

  return (
    <div className="bg-gradient-to-br from-white to-yellow-50 rounded-xl shadow-lg border border-yellow-100 p-6">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">
        Extracted Fields
      </h2>
      
      <div className="space-y-4">
        {fieldEntries.map((field) => (
          <div key={field.key} className="border-b border-gray-100 pb-3 last:border-b-0">
            <div className="flex justify-between items-start">
              <span className="font-medium text-gray-700 text-sm">
                {field.label}:
              </span>
              <span 
                className={`text-sm px-3 py-1 rounded-full font-medium ${
                  field.value === 'NA' 
                    ? 'bg-gray-200 text-gray-600' 
                    : 'bg-gradient-to-r from-green-100 to-blue-100 text-green-800 border border-green-200'
                }`}
              >
                {field.value}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <button 
          className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-3 px-6 rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all duration-300 transform hover:scale-105 shadow-lg font-medium"
          onClick={() => {
            const data = JSON.stringify(fields, null, 2);
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'extracted_fields.json';
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          Download Results
        </button>
      </div>
    </div>
  );
}