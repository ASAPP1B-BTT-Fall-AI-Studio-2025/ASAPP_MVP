/**
 * Field extraction utilities based on regex patterns
 * Extracts structured data from unstructured conversation text
 */

export interface ExtractedFields {
  email: string;
  phone: string;
  zipCode: string;
  orderId: string;
}

/**
 * Extract email address from conversation text
 */
export function extractEmail(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Pattern to match email addresses
  const emailPattern = /[\w.-]+@[\w.-]+/;
  const match = text.match(emailPattern);

  return match ? match[0] : "NA";
}

/**
 * Extract phone number from conversation text
 * Phone numbers MUST have parentheses around area code: (XXX) XXX-XXXX
 */
export function extractPhone(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Strict pattern for phone numbers with parentheses around area code
  const phonePattern = /\(\d{3}\)\s*\d{3}-\d{4}/;
  const match = text.match(phonePattern);

  return match ? match[0] : "NA";
}

/**
 * Extract ZIP code from conversation text
 */
export function extractZipCode(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Pattern for 5-digit ZIP codes
  const zipPattern = /\b\d{5}\b/;
  const match = text.match(zipPattern);

  return match ? match[0] : "NA";
}

/**
 * Extract order ID from conversation text
 * Comprehensive pattern for various order ID formats
 */
export function extractOrderId(text: string): string {
  if (!text || text.trim() === "") {
    return "NA";
  }

  // Multiple patterns for different order ID formats
  const orderPatterns = [
    // Pattern 1: "order" followed by alphanumeric (case insensitive)
    /order[:\s#]*([A-Za-z0-9]+)/i,
    
    // Pattern 2: "order id" or "order number" followed by alphanumeric
    /order\s+(?:id|number)[:\s#]*([A-Za-z0-9]+)/i,
    
    // Pattern 3: Hash symbol followed by alphanumeric
    /#([A-Za-z0-9]+)/,
    
    // Pattern 4: Standalone alphanumeric strings that look like order IDs
    /\b([A-Z]{2}\d{6,}|\d{8,}|[A-Z]\d{7,})\b/
  ];

  for (const pattern of orderPatterns) {
    const match = text.match(pattern);
    if (match) {
      return match[1] || match[0];
    }
  }

  return "NA";
}

/**
 * Extract all fields from conversation text
 */
export function extractAllFields(text: string): ExtractedFields {
  return {
    email: extractEmail(text),
    phone: extractPhone(text),
    zipCode: extractZipCode(text),
    orderId: extractOrderId(text),
  };
}