/**
 * Enhanced field extraction utilities
 * Combines regex patterns with optional LLM extraction
 */

export interface ExtractedFields {
  email: string;
  phone: string;
  zipCode: string;
  orderId: string;
}

export interface ExtractedFieldsWithMetadata extends ExtractedFields {
  metadata?: {
    fileName?: string;
    processedAt: string;
    textLength: number;
    extractionMethod: 'regex' | 'llm' | 'hybrid';
  };
}

/**
 * Extract email address from conversation text
 */
export function extractEmail(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Enhanced email pattern to match more variations
  const emailPattern = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
  const matches = text.match(emailPattern);

  // Return the first valid email found
  if (matches && matches.length > 0) {
    // Filter out potential false positives
    const validEmails = matches.filter(email => 
      email.includes('.') && 
      email.length > 5 && 
      !email.includes('..') &&
      email.split('@').length === 2
    );
    
    return validEmails.length > 0 ? validEmails[0] : "NA";
  }

  return "NA";
}

/**
 * Extract phone number from conversation text
 * Enhanced patterns for multiple phone number formats
 */
export function extractPhone(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Multiple patterns for different phone formats
  const phonePatterns = [
    // (XXX) XXX-XXXX format (strict)
    /\(\d{3}\)\s*\d{3}-\d{4}/,
    // XXX-XXX-XXXX format
    /\b\d{3}-\d{3}-\d{4}\b/,
    // XXX.XXX.XXXX format
    /\b\d{3}\.\d{3}\.\d{4}\b/,
    // +1 XXX XXX XXXX format
    /\+1\s*\d{3}\s*\d{3}\s*\d{4}/,
    // General 10+ digit numbers (more lenient)
    /\+?\d[\d\s-]{8,}\d/
  ];

  for (const pattern of phonePatterns) {
    const match = text.match(pattern);
    if (match) {
      // Validate the phone number has correct digit count
      const digits = match[0].replace(/\D/g, '');
      if (digits.length >= 10 && digits.length <= 11) {
        return match[0];
      }
    }
  }

  return "NA";
}

/**
 * Extract ZIP code from conversation text
 */
export function extractZipCode(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Pattern for 5-digit ZIP codes (avoiding order IDs and other numbers)
  const zipPattern = /\b\d{5}(?:-\d{4})?\b/g;
  const matches = text.match(zipPattern);

  if (matches) {
    // Filter out numbers that are likely order IDs or other identifiers
    const validZips = matches.filter(zip => {
      const digits = zip.replace(/\D/g, '');
      // Basic US ZIP code validation (00001-99999 range)
      const num = parseInt(digits.substring(0, 5));
      return num >= 1 && num <= 99999;
    });

    return validZips.length > 0 ? validZips[0] : "NA";
  }

  return "NA";
}

/**
 * Extract order ID from conversation text
 * Enhanced comprehensive pattern for various order ID formats
 */
export function extractOrderId(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Multiple patterns for different order ID formats (based on your FastAPI code)
  const orderPatterns = [
    // Pattern 1: "order" followed by alphanumeric (case insensitive)
    /order[:\s#]*([A-Za-z0-9]+)/i,
    
    // Pattern 2: "order id" or "order number" followed by alphanumeric
    /order\s+(?:id|number)[:\s#]*([A-Za-z0-9]+)/i,
    
    // Pattern 3: Hash symbol followed by alphanumeric
    /#([A-Za-z0-9]+)/,
    
    // Pattern 4: Standalone alphanumeric strings that look like order IDs
    /\b([A-Z]{2,}\d{4,}|\d{6,}[A-Z]+|[A-Z]\d{5,})\b/,
    
    // Pattern 5: Order with various separators
    /\b(?:order|ord|ref)[:\s#-]*([A-Za-z0-9]+)/i,
    
    // Pattern 6: Invoice or transaction patterns
    /\b(?:inv|txn|ref)[:\s#-]*([A-Za-z0-9]+)/i
  ];

  for (const pattern of orderPatterns) {
    const match = text.match(pattern);
    if (match) {
      const orderId = match[1] || match[0];
      // Validate order ID (should be at least 3 characters and not just numbers that could be ZIP/phone)
      if (orderId && orderId.length >= 3) {
        // Avoid ZIP codes and phone numbers
        if (!/^\d{5}$/.test(orderId) && !/^\d{10}$/.test(orderId)) {
          return orderId;
        }
      }
    }
  }

  return "NA";
}

/**
 * Extract all fields from conversation text using regex
 */
export function extractAllFields(text: string): ExtractedFields {
  return {
    email: extractEmail(text),
    phone: extractPhone(text),
    zipCode: extractZipCode(text),
    orderId: extractOrderId(text),
  };
}

/**
 * Extract all fields with metadata
 */
export function extractAllFieldsWithMetadata(
  text: string, 
  fileName?: string
): ExtractedFieldsWithMetadata {
  const fields = extractAllFields(text);
  
  return {
    ...fields,
    metadata: {
      fileName,
      processedAt: new Date().toISOString(),
      textLength: text.length,
      extractionMethod: 'regex',
    },
  };
}

/**
 * Legacy regex extraction function (matching your FastAPI format)
 */
export function regexExtractFields(text: string): {
  emails: string[];
  phone_numbers: string[];
  order_ids: string[];
} {
  const emailMatches = text.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g) || [];
  const phoneMatches = text.match(/\+?\d[\d\s-]{8,}\d/g) || [];
  const orderMatches = text.match(/order[\s#:]*\d+/gi) || [];
  
  return {
    emails: Array.from(new Set(emailMatches)),
    phone_numbers: Array.from(new Set(phoneMatches)),
    order_ids: Array.from(new Set(orderMatches)),
  };
}