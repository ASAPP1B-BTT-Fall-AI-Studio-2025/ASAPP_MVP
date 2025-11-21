/**
 * FastAPI Backend Integration Utility
 * 
 * This module provides utilities to integrate with your FastAPI backend
 * from the Jupyter notebook for enhanced extraction capabilities.
 */

interface FastAPIExtractionResult {
  emails: string[];
  phone_numbers: string[];
  order_ids: string[];
  error?: string;
}

interface FastAPIConfig {
  baseUrl: string;
  apiKey?: string;
}

class FastAPIClient {
  private config: FastAPIConfig;

  constructor(config: FastAPIConfig) {
    this.config = config;
  }

  /**
   * Extract fields using the FastAPI backend
   */
  async extractFields(text: string): Promise<FastAPIExtractionResult> {
    try {
      const response = await fetch(`${this.config.baseUrl}/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`FastAPI request failed: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('FastAPI extraction error:', error);
      return {
        emails: [],
        phone_numbers: [],
        order_ids: [],
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Process multiple conversations in batch
   */
  async processBatch(conversations: string[]): Promise<FastAPIExtractionResult[]> {
    try {
      const response = await fetch(`${this.config.baseUrl}/process_batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
        body: JSON.stringify({ conversations }),
      });

      if (!response.ok) {
        throw new Error(`FastAPI batch request failed: ${response.status}`);
      }

      const results = await response.json();
      return results;
    } catch (error) {
      console.error('FastAPI batch processing error:', error);
      return conversations.map(() => ({
        emails: [],
        phone_numbers: [],
        order_ids: [],
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }

  /**
   * Check if FastAPI backend is available
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.baseUrl}/`, {
        method: 'GET',
        headers: {
          ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
        },
      });

      return response.ok;
    } catch {
      return false;
    }
  }
}

/**
 * Environment-based FastAPI client factory
 */
export function createFastAPIClient(): FastAPIClient | null {
  const fastApiUrl = process.env.FASTAPI_URL || process.env.NEXT_PUBLIC_FASTAPI_URL;
  const fastApiKey = process.env.FASTAPI_API_KEY;

  if (!fastApiUrl) {
    console.warn('FastAPI URL not configured. Falling back to regex-only extraction.');
    return null;
  }

  return new FastAPIClient({
    baseUrl: fastApiUrl,
    apiKey: fastApiKey,
  });
}

/**
 * Hybrid extraction combining regex and FastAPI
 */
export async function hybridExtraction(text: string): Promise<{
  regex: { emails: string[]; phone_numbers: string[]; order_ids: string[] };
  fastapi?: FastAPIExtractionResult;
  combined: { email: string; phone: string; zipCode: string; orderId: string };
}> {
  // Always perform regex extraction
  const { regexExtractFields } = await import('./enhancedFieldExtractor');
  const regexResult = regexExtractFields(text);

  let fastApiResult: FastAPIExtractionResult | undefined;
  
  // Try FastAPI extraction if available
  const fastApiClient = createFastAPIClient();
  if (fastApiClient && await fastApiClient.healthCheck()) {
    fastApiResult = await fastApiClient.extractFields(text);
  }

  // Combine results (prioritize FastAPI if available and successful)
  const combinedEmails = [...new Set([
    ...regexResult.emails,
    ...(fastApiResult?.emails || [])
  ])];
  
  const combinedPhones = [...new Set([
    ...regexResult.phone_numbers,
    ...(fastApiResult?.phone_numbers || [])
  ])];
  
  const combinedOrderIds = [...new Set([
    ...regexResult.order_ids,
    ...(fastApiResult?.order_ids || [])
  ])];

  // Extract ZIP codes using regex (not in FastAPI)
  const { extractZipCode } = await import('./enhancedFieldExtractor');
  const zipCode = extractZipCode(text);

  return {
    regex: regexResult,
    fastapi: fastApiResult,
    combined: {
      email: combinedEmails[0] || 'NA',
      phone: combinedPhones[0] || 'NA',
      zipCode,
      orderId: combinedOrderIds[0] || 'NA',
    },
  };
}

export { FastAPIClient };
export type { FastAPIExtractionResult, FastAPIConfig };