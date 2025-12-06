"""
Extractify FastAPI Backend
Enhanced version of your original FastAPI code with database integration
"""

import re
import asyncio
import os
import gzip
import json
import time
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env.local
from dotenv import load_dotenv
load_dotenv('../.env.local')  # Load from parent directory
load_dotenv('.env')  # Also try local .env

# Try to import Gemini, fallback to OpenAI if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Generative AI not installed. Install with: pip install google-generativeai")

# Pydantic Models
class ConversationCreate(BaseModel):
    title: str
    content: str
    fileName: Optional[str] = None
    # Optional pre-extracted fields (from bulk extraction)
    extractedFields: Optional[Dict[str, str]] = None

class BulkSaveRequest(BaseModel):
    fileName: str
    conversations: List[Dict]  # List of extraction results

class ConversationResponse(BaseModel):
    id: str
    title: str
    content: str
    fileName: Optional[str]
    extractedFields: Dict[str, str]
    createdAt: str
    date: str
    preview: str

class ExtractRequest(BaseModel):
    text: str
    fileName: Optional[str] = None

class ExtractResponse(BaseModel):
    email: str
    phone: str
    zipCode: str
    orderId: str
    metadata: dict  # Changed from Dict[str, any] to dict

# Initialize FastAPI app
app = FastAPI(
    title="Extractify Backend",
    description="AI-powered field extraction from conversations with hybrid regex+LLM approach",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_PATH = "data/extractify_fastapi.db"

def init_database():
    """Initialize SQLite database with required tables"""
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            fileName TEXT,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Extracted fields table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversationId TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            zipCode TEXT,
            orderId TEXT,
            metadata TEXT,
            extractionMethod TEXT DEFAULT 'hybrid',
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversationId) REFERENCES conversations(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Enhanced Regex Extraction Functions
def extract_customer_name(text):
    """
    Extract customer name from conversation text.
    Looks for common patterns like "my name is", "this is", "I'm", etc.
    
    Args:
        text: String containing conversation text
        
    Returns:
        Customer name if found, "NA" otherwise
    """
    if text is None or text == "":
        return "NA"
    
    text_str = str(text)
    
    # Patterns to find customer names
    name_patterns = [
        r"(?:my name is|i'm|i am|this is|name's|name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",  # "My name is John Smith"
        r"(?:call me|it's|its)\s+([A-Z][a-z]+)",  # "Call me John"
        r"^(?:hi|hello|hey)[,!]?\s+(?:this is\s+)?([A-Z][a-z]+)",  # "Hi, this is John"
        r"(?:customer|user|caller):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",  # "Customer: John Smith"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text_str, re.IGNORECASE | re.MULTILINE)
        if match:
            name = match.group(1).strip()
            # Capitalize properly
            name = ' '.join(word.capitalize() for word in name.split())
            # Validate it looks like a name (not too long, no numbers)
            if len(name) <= 30 and not re.search(r'\d', name):
                return name
    
    return "NA"

def extract_email(text):
    """
    Extract email address from conversation text.

    Args:
        text: String containing conversation text

    Returns:
        Email address if found, "NA" otherwise
    """
    if text is None or text == "":
        return "NA"

    # Pattern to match email addresses
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    match = re.search(email_pattern, str(text))

    if match:
        return match.group(0)
    else:
        return "NA"


def extract_phone(text):
    """
    Extract phone number from conversation text.
    Supports multiple formats: (XXX) XXX-XXXX, XXX-XXX-XXXX, etc.
    Uses context awareness to avoid confusion with order IDs.

    Args:
        text: String containing conversation text

    Returns:
        Phone number if found, "NA" otherwise
    """
    if text is None or text == "":
        return "NA"

    text_str = str(text)

    # Phone number patterns - multiple formats supported
    phone_patterns = [
        # Format with parentheses: (003) 941-7614
        (r'\((\d{3})\)\s*(\d{3})[-.\s]?(\d{4})', 3),
        # Format with dashes: 116-048-7515
        (r'\b(\d{3})-(\d{3})-(\d{4})\b', 3),
        # Format with dots: 555.123.4567
        (r'\b(\d{3})\.(\d{3})\.(\d{4})\b', 3),
        # Format with spaces: 555 123 4567
        (r'\b(\d{3})\s(\d{3})\s(\d{4})\b', 3),
    ]

    for pattern, num_groups in phone_patterns:
        matches = list(re.finditer(pattern, text_str))
        for match in matches:
            # Check context - make sure it's not preceded by "order" keywords
            start_pos = match.start()
            context_before = text_str[max(0, start_pos-50):start_pos].lower()
            context_after = text_str[match.end():min(len(text_str), match.end()+30)].lower()

            # Skip if it's in order ID context
            if re.search(r'order\s*(id|number|#|:)', context_before):
                continue
            if re.search(r'order', context_before) and not re.search(r'phone|call|contact|number', context_before):
                # If "order" is mentioned but not "phone", skip
                continue

            # Check if context mentions phone explicitly
            is_phone_context = re.search(r'phone|call|contact|reach|mobile|cell', context_before) or \
                               re.search(r'phone|call|contact|reach|mobile|cell', context_after)

            # Reconstruct phone number
            if num_groups == 3:
                phone_clean = match.group(1) + match.group(2) + match.group(3)
            else:
                phone_clean = ''.join(match.groups())

            # Verify it's 10 digits
            if phone_clean.isdigit() and len(phone_clean) == 10:
                # For non-parenthesis formats, require phone context to avoid order ID confusion
                has_parens = '(' in match.group(0)
                if has_parens or is_phone_context:
                    return f"{phone_clean[:3]}-{phone_clean[3:6]}-{phone_clean[6:]}"

    return "NA"


def extract_zip_code(text):
    """
    Extract zip code from conversation text.
    Supports both 5-digit and 5+4 format (e.g., 12345 or 12345-6789).
    Improved to catch zip codes mentioned explicitly or in address contexts.

    Args:
        text: String containing conversation text

    Returns:
        Zip code if found, "NA" otherwise
    """
    if text is None or text == "":
        return "NA"

    text_str = str(text)

    # First, look for explicit mentions of zip code
    # Pattern 1: "zip code" or "zip" followed by a 5-digit number
    explicit_zip_patterns = [
        r'(?:zip\s*(?:code|is|:)?\s*)(\d{5}(?:-\d{4})?)',  # "zip code 12345" or "zip: 12345" or "zip is 12345"
        r'(?:zip\s+)(\d{5}(?:-\d{4})?)',  # "zip 12345"
    ]

    for pattern in explicit_zip_patterns:
        match = re.search(pattern, text_str, re.IGNORECASE)
        if match:
            zip_code = match.group(1)
            return zip_code

    # Pattern 2: 5+4 format (12345-6789) - always return if found
    zip_plus4_pattern = r'\b(\d{5}-\d{4})\b'
    match = re.search(zip_plus4_pattern, text_str)
    if match:
        return match.group(1)

    # Pattern 3: Look for 5-digit numbers in address contexts
    # Address pattern: Street, City, State ZIP
    address_zip_pattern = r'(?:street|ave|avenue|road|rd|drive|dr|blvd|boulevard|way|ln|lane|st|circle)\s+[^,]*,\s*[^,]*,\s*[A-Z]{2}\s+(\d{5})'
    match = re.search(address_zip_pattern, text_str, re.IGNORECASE)
    if match:
        return match.group(1)

    # Pattern 4: Look for standalone 5-digit numbers that are likely zip codes
    # Check all 5-digit numbers and determine if they're zip codes
    all_5digit = list(re.finditer(r'\b(\d{5})\b', text_str))

    for match in all_5digit:
        zip_candidate = match.group(1)
        start_pos = match.start()
        end_pos = match.end()

        # Get context around the number
        context_before = text_str[max(0, start_pos-50):start_pos].lower()
        context_after = text_str[end_pos:min(len(text_str), end_pos+50)].lower()
        surrounding = text_str[max(0, start_pos-10):end_pos+10]

        # Skip if it's part of a phone number (has parentheses nearby)
        if re.search(r'\(\d{3}\)', surrounding):
            continue

        # Skip if it's in order ID context
        if re.search(r'order\s+(id|number|#)', context_before):
            continue

        # Skip if it's part of a longer number (like part of order ID)
        # Check if there are 6+ digit numbers nearby
        nearby_long_numbers = re.findall(r'\d{6,}', surrounding)
        if nearby_long_numbers:
            # If this 5-digit number is part of a longer sequence, skip it
            continue

        # If it's mentioned near "zip", "address", "location", or city/state, it's likely a zip code
        if any(keyword in context_before or context_after for keyword in ['zip', 'address', 'location', 'city', 'state']):
            return zip_candidate

        # If it appears after a state abbreviation pattern (2 letters + space/number)
        if re.search(r'[A-Z]{2}\s+' + re.escape(zip_candidate), text_str, re.IGNORECASE):
            return zip_candidate

        # If it's a standalone 5-digit number and not in problematic context, consider it
        # But be more conservative - only if it's clearly not part of something else
        if not re.search(r'\d{6,}', surrounding):  # No 6+ digit numbers nearby
            # If there's no clear indication it's NOT a zip code, return it
            # (This catches cases like "78202" mentioned alone)
            return zip_candidate

    return "NA"


def extract_order_id(text):
    """
    Extract order ID from conversation text.
    Order ID is only numbers (no letters).
    Comprehensive pattern matching for various ways order IDs are mentioned.

    Args:
        text: String containing conversation text

    Returns:
        Order ID if found, "NA" otherwise
    """
    if text is None or text == "":
        return "NA"

    text_str = str(text)

    # COMPREHENSIVE order ID patterns - try multiple variations
    # Priority order: most specific first

    # Pattern 1: "order ID. It is 1012809669" or "order id: 12345" or "order id is 12345"
    patterns = [
        r'(?:order\s+id\.?\s*(?:it\s+is|is|:)\s*)(\d{6,})',  # "order ID. It is 1012809669" or "order id: 12345" (6+ digits)
        r'(?:order\s+id\.?\s*:?\s*)(\d{6,})',  # "order id: 12345" or "order id 12345" (6+ digits)
        r'(?:order\s+number\.?\s*(?:it\s+is|is|:)?\s*)(\d{6,})',  # "order number: 12345" or "order number 12345"
        r'(?:order\s+#\s*)(\d{6,})',  # "order # 12345"
        r'(?:order\s+)(\d{6,})',  # "order 123456" format (6+ digits)
    ]

    for pattern in patterns:
        matches = list(re.finditer(pattern, text_str, re.IGNORECASE))
        for match in matches:
            order_id = match.group(1)
            # Verify it's only numbers (no letters) and is long enough
            if order_id.isdigit() and len(order_id) >= 6:
                # Skip if it's clearly part of an account ID (has letters nearby)
                start_pos = match.start()
                end_pos = match.end()
                surrounding = text_str[max(0, start_pos-5):end_pos+5]
                # Check if there are letters immediately before or after (account ID pattern)
                if re.search(r'[A-Za-z]\d{6,}|\d{6,}[A-Za-z]', surrounding):
                    continue
                return order_id

    # Pattern 2: Look for numbers that appear right after "order id" on the same or next line
    # This handles cases like:
    # "Do you have an order ID?"
    # "2243746561"
    order_id_context = re.finditer(r'order\s+(?:id|number|#)', text_str, re.IGNORECASE)
    for match in order_id_context:
        # Look for a number within 100 characters after "order id"
        after_text = text_str[match.end():match.end()+100]
        # Find the first standalone number (6+ digits) that appears
        number_match = re.search(r'\b(\d{6,})\b', after_text)
        if number_match:
            order_id = number_match.group(1)
            # Verify it's only numbers and not part of account ID
            if order_id.isdigit():
                # Check if it's part of an account ID (has letters nearby)
                check_text = text_str[match.end():match.end()+number_match.end()+10]
                if not re.search(r'[A-Za-z]\d{6,}|\d{6,}[A-Za-z]', check_text):
                    return order_id

    # Pattern 3: Look for standalone long numeric sequences (9+ digits) that aren't phone numbers
    # Phone numbers have specific formats with parentheses/dashes, so plain long numbers are likely order IDs
    long_number_pattern = r'\b(\d{9,})\b'
    matches = list(re.finditer(long_number_pattern, text_str))

    for match in matches:
        number = match.group(1)
        start_pos = match.start()
        end_pos = match.end()

        # Check context around the number
        context_before = text_str[max(0, start_pos-50):start_pos].lower()
        context_after = text_str[end_pos:min(len(text_str), end_pos+50)].lower()
        surrounding_text = text_str[max(0, start_pos-10):end_pos+10]

        # Skip if it's in a phone number format (has parentheses around area code)
        if re.search(r'\(\d{3}\)', surrounding_text):
            continue

        # Skip if it's in a phone number format with dashes/spaces (XXX-XXX-XXXX)
        if re.search(r'\d{3}[-.\s]\d{3}[-.\s]\d{4}', surrounding_text):
            continue

        # Skip if it looks like a phone number context
        if any(keyword in context_before or context_after for keyword in ['phone', 'call', 'contact', 'telephone']):
            # But allow if it's explicitly in order context
            if 'order' in context_before:
                if number.isdigit():
                    return number
            continue

        # If it's explicitly in order context, return it
        if 'order' in context_before or 'order' in context_after:
            if number.isdigit():
                return number

        # If it's a plain number (no separators) and 9+ digits, it's likely an order ID
        # (phone numbers are typically 10 digits with formatting, order IDs can be longer)
        if number.isdigit() and len(number) >= 9:
            # Double check: if it's exactly 10 digits and not in order context, be cautious
            if len(number) == 10:
                # Only return if there's some indication it's an order ID
                if 'order' in context_before or 'order' in context_after:
                    return number
                # Skip 10-digit numbers that might be phones
                continue
            else:
                # 9 digits or 11+ digits are more likely to be order IDs
                return number

    return "NA"

def regex_extract_fields(text: str) -> Dict[str, str]:
    """Legacy format for compatibility"""
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "zipCode": extract_zip_code(text),
        "orderId": extract_order_id(text),
        "customerName": extract_customer_name(text),
    }

# LLM Extraction Class
class AsyncLLMExtractor:
    """Gemini-based LLM extractor for field extraction"""
    
    def __init__(self):
        # Use environment variable for Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
        
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package is not installed")
            
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        
        # Use Gemini 2.0 Flash for fast extraction
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.prompt_template = """You are an intelligent assistant that extracts structured data from customer service conversations.

Extract the following information from the conversation below:
- email: Email address (return single best match or "NA")
- phone: Phone number (return single best match or "NA") 
- zipCode: ZIP code (return single best match or "NA")
- orderId: Order ID or reference number (return single best match or "NA")

Return ONLY a valid JSON object with these exact keys: email, phone, zipCode, orderId
Return "NA" for any field where no valid information is found.

Conversation:
{conversation}

Respond with ONLY the JSON object, no other text:"""

    async def extract_async(self, text: str) -> Dict[str, str]:
        try:
            prompt = self.prompt_template.format(conversation=text[:4000])  # Limit text length
            
            # Use async generation
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse the response
            content = response.text.strip()
            
            # Clean up the response (remove markdown code blocks if present)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            result = json.loads(content)
            
            # Ensure all required fields exist
            return {
                "email": result.get("email", "NA"),
                "phone": result.get("phone", "NA"), 
                "zipCode": result.get("zipCode", "NA"),
                "orderId": result.get("orderId", "NA"),
            }
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return {"email": "NA", "phone": "NA", "zipCode": "NA", "orderId": "NA"}

# Initialize LLM extractor
try:
    llm_extractor = AsyncLLMExtractor()
    LLM_AVAILABLE = True
except Exception as e:
    print(f"LLM not available: {e}")
    llm_extractor = None
    LLM_AVAILABLE = False

# Database helper functions
def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def save_conversation(conversation_data: dict, extracted_fields: dict) -> str:
    """Save conversation and extracted fields to database"""
    conversation_id = f"conv_{int(time.time())}_{str(uuid4())[:8]}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Save conversation
    cursor.execute("""
        INSERT INTO conversations (id, title, content, fileName, createdAt)
        VALUES (?, ?, ?, ?, ?)
    """, (
        conversation_id,
        conversation_data["title"],
        conversation_data["content"],
        conversation_data.get("fileName"),
        datetime.now().isoformat()
    ))
    
    # Save extracted fields
    cursor.execute("""
        INSERT INTO extracted_fields 
        (conversationId, email, phone, zipCode, orderId, metadata, extractionMethod)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        conversation_id,
        extracted_fields["email"],
        extracted_fields["phone"], 
        extracted_fields["zipCode"],
        extracted_fields["orderId"],
        json.dumps(extracted_fields.get("metadata", {})),
        "hybrid" if LLM_AVAILABLE else "regex"
    ))
    
    conn.commit()
    conn.close()
    
    return conversation_id

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to Extractify Backend API 🚀",
        "version": "2.0.0",
        "features": ["regex_extraction", "llm_extraction" if LLM_AVAILABLE else "regex_only"],
        "database": "sqlite"
    }

@app.post("/extract", response_model=ExtractResponse)
async def extract_fields(request: ExtractRequest):
    """Extract fields using hybrid regex + LLM approach"""
    
    # Always perform regex extraction
    regex_result = regex_extract_fields(request.text)
    
    # Perform LLM extraction if available
    llm_result = {}
    if LLM_AVAILABLE and llm_extractor:
        try:
            llm_result = await llm_extractor.extract_async(request.text)
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            llm_result = {"email": "NA", "phone": "NA", "zipCode": "NA", "orderId": "NA"}
    
    # Combine results - use the best from each source
    # Priority: 1) If both found something, prefer regex (more deterministic)
    #           2) If only one found something, use that
    #           3) If neither found anything, return "NA"
    final_result = {}
    for field in ["email", "phone", "zipCode", "orderId"]:
        regex_val = regex_result.get(field, "NA")
        llm_val = llm_result.get(field, "NA") if LLM_AVAILABLE else "NA"
        
        # Smart combination: use whichever found something
        if regex_val != "NA":
            final_result[field] = regex_val  # Prefer regex (deterministic)
        elif llm_val != "NA":
            final_result[field] = llm_val  # Fallback to LLM
        else:
            final_result[field] = "NA"
    
    # Add metadata
    metadata = {
        "fileName": request.fileName,
        "processedAt": datetime.now().isoformat(),
        "textLength": len(request.text),
        "extractionMethod": "hybrid" if LLM_AVAILABLE else "regex",
        "regexResults": regex_result,
        "llmResults": llm_result if LLM_AVAILABLE else None
    }
    
    return ExtractResponse(
        email=final_result["email"],
        phone=final_result["phone"],
        zipCode=final_result["zipCode"],
        orderId=final_result["orderId"],
        metadata=metadata
    )

@app.get("/conversations")
async def get_conversations():
    """Get all conversations with their extracted fields"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, ef.email, ef.phone, ef.zipCode, ef.orderId, ef.metadata, ef.extractionMethod
        FROM conversations c
        LEFT JOIN extracted_fields ef ON c.id = ef.conversationId
        ORDER BY c.createdAt DESC
    """)
    
    conversations = cursor.fetchall()
    conn.close()
    
    result = []
    for conv in conversations:
        result.append({
            "id": conv[0],
            "title": conv[1], 
            "content": conv[2],
            "fileName": conv[3],
            "createdAt": conv[4],
            "date": datetime.fromisoformat(conv[4]).strftime("%Y-%m-%d"),
            "preview": conv[2][:100] + "..." if len(conv[2]) > 100 else conv[2],
            "extractedFields": {
                "email": conv[6] or "NA",
                "phone": conv[7] or "NA", 
                "zipCode": conv[8] or "NA",
                "orderId": conv[9] or "NA",
            },
            "metadata": json.loads(conv[10]) if conv[10] else {},
            "extractionMethod": conv[11] or "unknown"
        })
    
    return result

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, ef.email, ef.phone, ef.zipCode, ef.orderId, ef.metadata, ef.extractionMethod
        FROM conversations c
        LEFT JOIN extracted_fields ef ON c.id = ef.conversationId
        WHERE c.id = ?
    """, (conversation_id,))
    
    conversation = cursor.fetchone()
    conn.close()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": conversation[0],
        "title": conversation[1],
        "content": conversation[2], 
        "fileName": conversation[3],
        "createdAt": conversation[4],
        "extractedFields": {
            "email": conversation[6] or "NA",
            "phone": conversation[7] or "NA",
            "zipCode": conversation[8] or "NA", 
            "orderId": conversation[9] or "NA",
        },
        "metadata": json.loads(conversation[10]) if conversation[10] else {},
        "extractionMethod": conversation[11] or "unknown"
    }

@app.post("/conversations")
async def create_conversation(request: ConversationCreate):
    """Create new conversation with field extraction"""
    
    # Use pre-extracted fields if provided (from bulk extraction)
    if request.extractedFields:
        extracted_fields_dict = {
            "email": request.extractedFields.get("email", "NA"),
            "phone": request.extractedFields.get("phone", "NA"),
            "zipCode": request.extractedFields.get("zipCode", "NA"), 
            "orderId": request.extractedFields.get("orderId", "NA"),
            "metadata": {}  # Empty metadata for pre-extracted fields
        }
    else:
        # Extract fields if not provided
        extract_request = ExtractRequest(text=request.content, fileName=request.fileName)
        extraction_result = await extract_fields(extract_request)
        extracted_fields_dict = {
            "email": extraction_result.email,
            "phone": extraction_result.phone,
            "zipCode": extraction_result.zipCode, 
            "orderId": extraction_result.orderId,
            "metadata": extraction_result.metadata
        }
    
    # Save to database
    conversation_data = {
        "title": request.title,
        "content": request.content,
        "fileName": request.fileName
    }
    
    conversation_id = save_conversation(conversation_data, extracted_fields_dict)
    
    return {
        "id": conversation_id,
        "title": request.title,
        "content": request.content,
        "fileName": request.fileName,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "preview": request.content[:100] + "..." if len(request.content) > 100 else request.content,
        "extractedFields": {
            "email": extracted_fields_dict["email"],
            "phone": extracted_fields_dict["phone"],
            "zipCode": extracted_fields_dict["zipCode"],
            "orderId": extracted_fields_dict["orderId"],
        },
        "createdAt": datetime.now().isoformat()
    }

@app.post("/conversations/bulk-save")
async def save_bulk_conversations(request: BulkSaveRequest):
    """Save multiple conversations from bulk extraction with their pre-extracted fields"""
    saved_conversations = []
    
    for idx, conv_result in enumerate(request.conversations):
        # Create conversation with pre-extracted fields (only string values)
        conv_request = ConversationCreate(
            title=f"{request.fileName} - Conversation {idx + 1}",
            content=f"Conversation {idx + 1} from {request.fileName}",
            fileName=request.fileName,
            extractedFields={
                "email": str(conv_result.get("email", "NA")),
                "phone": str(conv_result.get("phone", "NA")),
                "zipCode": str(conv_result.get("zipCode", "NA")),
                "orderId": str(conv_result.get("orderId", "NA")),
            }
        )
        
        result = await create_conversation(conv_request)
        saved_conversations.append(result)
    
    return {
        "success": True,
        "saved": len(saved_conversations),
        "conversations": saved_conversations
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation and its extracted fields"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete extracted fields first (foreign key constraint)
    cursor.execute("DELETE FROM extracted_fields WHERE conversationId = ?", (conversation_id,))
    
    # Delete conversation
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conn.commit()
    conn.close()
    
    return {"success": True}

@app.post("/extract-bulk")
async def extract_bulk(request: ExtractRequest):
    """Extract fields from multiple conversations in a file"""
    try:
        # Try to parse as JSON first (for JSONL or JSON array format)
        text = request.text.strip()
        results = []
        
        # Try parsing as complete JSON (ABCD format or JSON object with 'train' key)
        try:
            json_data = json.loads(text)
            
            # Handle ABCD dataset format (has 'train' key with list of conversations)
            if isinstance(json_data, dict) and 'train' in json_data:
                conversations_list = json_data['train']
                for idx, item in enumerate(conversations_list):
                    if isinstance(item, dict):
                        # Extract text from the conversation structure
                        conversation_text = ""
                        
                        # PRIORITY 1: Use 'original' field (has REAL data - emails, phones, etc.)
                        # NOTE: 'delexed' field has ANONYMIZED placeholders like <email>, <order_id>
                        if 'original' in item and isinstance(item['original'], list):
                            texts = []
                            for turn in item['original']:
                                if isinstance(turn, list) and len(turn) > 1:
                                    texts.append(str(turn[1]))
                            conversation_text = " ".join(texts)
                        
                        # Fallback: try 'delexed' field (anonymized but better than nothing)
                        elif 'delexed' in item and isinstance(item['delexed'], list):
                            texts = []
                            for turn in item['delexed']:
                                if isinstance(turn, dict) and 'text' in turn:
                                    texts.append(turn['text'])
                            conversation_text = " ".join(texts)
                        
                        # Fallback: try 'scenario' field (has structured data)
                        elif 'scenario' in item:
                            conversation_text = str(item['scenario'])
                        
                        if conversation_text.strip():
                            convo_id = item.get('convo_id', idx)
                            
                            # First extract from conversation text
                            extraction_result = await extract_single_conversation(
                                conversation_text,
                                f"{request.fileName or 'abcd'}_convo_{convo_id}"
                            )
                            
                            # ALSO extract from scenario field (has customer info like phone, zip, order_id)
                            if 'scenario' in item and isinstance(item['scenario'], dict):
                                scenario = item['scenario']
                                
                                # Extract from personal info
                                if 'personal' in scenario:
                                    personal = scenario['personal']
                                    if extraction_result['phone'] == 'NA' and personal.get('phone'):
                                        extraction_result['phone'] = personal['phone']
                                    if extraction_result['email'] == 'NA' and personal.get('email'):
                                        extraction_result['email'] = personal['email']
                                
                                # Extract from order info
                                if 'order' in scenario:
                                    order = scenario['order']
                                    if extraction_result['zipCode'] == 'NA' and order.get('zip_code'):
                                        extraction_result['zipCode'] = order['zip_code']
                                    if extraction_result['orderId'] == 'NA' and order.get('order_id'):
                                        extraction_result['orderId'] = order['order_id']
                            
                            # Add conversation ID and category info to metadata
                            extraction_result['metadata']['conversation_id'] = convo_id
                            extraction_result['metadata']['has_scenario_data'] = 'scenario' in item
                            
                            # Add flow/subflow for conversation categorization
                            if 'scenario' in item and isinstance(item['scenario'], dict):
                                scenario = item['scenario']
                                extraction_result['metadata']['flow'] = scenario.get('flow', 'unknown')
                                extraction_result['metadata']['subflow'] = scenario.get('subflow', '')
                                # Create a human-readable category
                                flow = scenario.get('flow', '').replace('_', ' ').title()
                                subflow = scenario.get('subflow', '').replace('_', ' ').title()
                                extraction_result['metadata']['category'] = f"{flow}" if not subflow else f"{flow} - {subflow}"
                            
                            results.append(extraction_result)
                
                if results:
                    # Create summary of conversation types
                    categories = {}
                    for r in results:
                        cat = r.get('metadata', {}).get('flow', 'unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    # Create a descriptive summary
                    summary = ", ".join([f"{v} {k.replace('_', ' ')}" for k, v in categories.items()])
                    
                    return {
                        "conversations": results, 
                        "total": len(results), 
                        "format": "abcd", 
                        "dataset": "ABCD v1.1",
                        "summary": summary,
                        "categories": categories
                    }
            
            # Handle JSON array format
            if isinstance(json_data, list):
                for idx, item in enumerate(json_data):
                    conversation_text = ""
                    if isinstance(item, dict):
                        for key in ['text', 'content', 'message', 'conversation', 'dialog', 'messages']:
                            if key in item:
                                if isinstance(item[key], list):
                                    conversation_text = " ".join(str(x) for x in item[key])
                                else:
                                    conversation_text = str(item[key])
                                break
                        if not conversation_text:
                            conversation_text = " ".join(str(v) for v in item.values() if isinstance(v, str))
                    else:
                        conversation_text = str(item)
                    
                    if conversation_text.strip():
                        extraction_result = await extract_single_conversation(
                            conversation_text,
                            f"{request.fileName or 'bulk'}_conversation_{idx+1}"
                        )
                        results.append(extraction_result)
                
                if results:
                    return {"conversations": results, "total": len(results), "format": "json"}
        except json.JSONDecodeError:
            pass
        
        # Check if it's JSONL format (JSON Lines - one JSON object per line)
        if '\n' in text:
            lines = text.split('\n')
            json_lines = [line.strip() for line in lines if line.strip()]
            
            # Try to parse as JSONL
            jsonl_parsed = True
            jsonl_data = []
            for line in json_lines:
                try:
                    data = json.loads(line)
                    jsonl_data.append(data)
                except json.JSONDecodeError:
                    jsonl_parsed = False
                    break
            
            if jsonl_parsed and jsonl_data:
                # Process each JSON object as a separate conversation
                for idx, item in enumerate(jsonl_data):
                    # Extract text from the JSON object
                    conversation_text = ""
                    if isinstance(item, dict):
                        # Try common field names for conversation text
                        for key in ['text', 'content', 'message', 'conversation', 'dialog', 'messages']:
                            if key in item:
                                if isinstance(item[key], list):
                                    conversation_text = " ".join(str(x) for x in item[key])
                                else:
                                    conversation_text = str(item[key])
                                break
                        
                        # If no standard field found, concatenate all string values
                        if not conversation_text:
                            conversation_text = " ".join(str(v) for v in item.values() if isinstance(v, str))
                    else:
                        conversation_text = str(item)
                    
                    if conversation_text.strip():
                        # Extract fields from this conversation
                        extraction_result = await extract_single_conversation(
                            conversation_text,
                            f"{request.fileName or 'bulk'}_conversation_{idx+1}"
                        )
                        results.append(extraction_result)
                
                if results:
                    return {"conversations": results, "total": len(results), "format": "jsonl"}
        
        # If not JSON, treat entire text as single conversation
        result = await extract_single_conversation(text, request.fileName)
        return {"conversations": [result], "total": 1, "format": "text"}
        
    except Exception as e:
        print(f"Bulk extraction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def extract_single_conversation(text: str, file_name: Optional[str] = None):
    """Extract fields from a single conversation"""
    # Regex extraction
    regex_result = regex_extract_fields(text)
    
    # LLM extraction
    llm_result = {}
    if LLM_AVAILABLE and llm_extractor:
        try:
            llm_result = await llm_extractor.extract_async(text)
        except Exception as e:
            print(f"LLM extraction error: {e}")
            llm_result = {"email": "NA", "phone": "NA", "zipCode": "NA", "orderId": "NA"}
    
    # Combine results - use the best from each source
    # Priority: regex first (deterministic), then LLM as fallback
    final_result = {}
    for field in ["email", "phone", "zipCode", "orderId"]:
        regex_val = regex_result.get(field, "NA")
        llm_val = llm_result.get(field, "NA") if LLM_AVAILABLE else "NA"
        
        if regex_val != "NA":
            final_result[field] = regex_val  # Prefer regex
        elif llm_val != "NA":
            final_result[field] = llm_val  # Fallback to LLM
        else:
            final_result[field] = "NA"
    
    # Customer name from regex only (LLM not trained for this yet)
    customer_name = regex_result.get("customerName", "NA")
    
    # Add metadata
    metadata = {
        "fileName": file_name,
        "processedAt": datetime.now().isoformat(),
        "textLength": len(text),
        "extractionMethod": "hybrid" if LLM_AVAILABLE else "regex",
        "regexResults": regex_result,
        "llmResults": llm_result if LLM_AVAILABLE else None
    }
    
    return {
        "email": final_result["email"],
        "phone": final_result["phone"],
        "zipCode": final_result["zipCode"],
        "orderId": final_result["orderId"],
        "customerName": customer_name,
        "metadata": metadata
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_available": LLM_AVAILABLE,
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)