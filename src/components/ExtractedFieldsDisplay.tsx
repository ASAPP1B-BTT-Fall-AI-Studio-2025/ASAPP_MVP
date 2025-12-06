'use client';

import { ExtractedFields } from '@/lib/fieldExtractor';

interface ExtractedFieldsDisplayProps {
  fields: ExtractedFields | null;
  isLoading: boolean;
  bulkResults?: any[];
  onDownload?: () => void;
}

export default function ExtractedFieldsDisplay({ 
  fields, 
  isLoading,
  bulkResults = [],
  onDownload
}: ExtractedFieldsDisplayProps) {
  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-white to-yellow-50 rounded-xl shadow-lg border border-yellow-100 p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800 bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
          Extracted Fields
        </h2>
        <div className="animate-pulse space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-6 bg-yellow-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  // Check if we have bulk results to display
  const isBulkProcessing = bulkResults && bulkResults.length > 1;

  if (!fields && !isBulkProcessing) {
    return (
      <div className="bg-gradient-to-br from-white to-yellow-50 rounded-xl shadow-lg border border-yellow-100 p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800 bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
          Extracted Fields
        </h2>
        <div className="text-gray-500 text-center py-8">
          Upload a conversation file to see extracted fields
        </div>
      </div>
    );
  }

  // For bulk processing, show all results in a table
  if (isBulkProcessing) {
    return (
      <div className="bg-gradient-to-br from-white to-yellow-50 rounded-xl shadow-lg border border-yellow-100 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800 bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
            Extracted Fields
          </h2>
          <button 
            className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-2 px-6 rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-all duration-300 shadow-md font-medium text-sm"
            onClick={onDownload}
          >
            Download Results
          </button>
        </div>
        
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-800 font-semibold">
            📦 Bulk Processing: {bulkResults.length} conversations processed
          </p>
        </div>

        {/* Full-width scrollable table */}
        <div className="overflow-x-auto max-h-[400px] overflow-y-auto border border-gray-200 rounded-lg">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gradient-to-r from-indigo-100 to-purple-100">
              <tr className="border-b border-gray-200">
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Convo #</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Email</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Phone</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">ZIP Code</th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700">Order ID</th>
              </tr>
            </thead>
            <tbody>
              {bulkResults.map((result, idx) => (
                <tr key={idx} className="border-b border-gray-100 hover:bg-yellow-50 transition-colors">
                  <td className="px-4 py-3 text-gray-700 font-medium">{idx + 1}</td>
                  <td className="px-4 py-3">
                    <span className={`text-sm px-3 py-1 rounded-full ${
                      result.email && result.email !== 'NA'
                        ? 'bg-green-100 text-green-800 font-medium'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {result.email || 'NA'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-sm px-3 py-1 rounded-full ${
                      result.phone && result.phone !== 'NA'
                        ? 'bg-green-100 text-green-800 font-medium'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {result.phone || 'NA'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-sm px-3 py-1 rounded-full ${
                      result.zipCode && result.zipCode !== 'NA'
                        ? 'bg-green-100 text-green-800 font-medium'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {result.zipCode || 'NA'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-sm px-3 py-1 rounded-full ${
                      result.orderId && result.orderId !== 'NA'
                        ? 'bg-green-100 text-green-800 font-medium'
                        : 'bg-gray-100 text-gray-500'
                    }`}>
                      {result.orderId || 'NA'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // For single conversation, show individual fields
  const fieldEntries = [
    { label: 'Email', value: fields?.email, key: 'email' },
    { label: 'Phone', value: fields?.phone, key: 'phone' },
    { label: 'ZIP Code', value: fields?.zipCode, key: 'zipCode' },
    { label: 'Order ID', value: fields?.orderId, key: 'orderId' },
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
                  !field.value || field.value === 'NA'
                    ? 'bg-gray-200 text-gray-600' 
                    : 'bg-gradient-to-r from-green-100 to-blue-100 text-green-800 border border-green-200'
                }`}
              >
                {field.value || 'N/A'}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <button 
          className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-3 px-6 rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all duration-300 transform hover:scale-105 shadow-lg font-medium"
          onClick={onDownload}
        >
          Download Results
        </button>
      </div>
    </div>
  );
}