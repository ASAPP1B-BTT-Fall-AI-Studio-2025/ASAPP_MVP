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
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI

# Pydantic Models
class ConversationCreate(BaseModel):
    title: str
    content: str
    fileName: Optional[str] = None

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
def extract_email(text: str) -> str:
    """Extract email address using enhanced regex"""
    if not text or text.strip() == "":
        return "NA"
    
    email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    matches = re.findall(email_pattern, text)
    
    if matches:
        # Filter valid emails
        valid_emails = [email for email in matches if 
                       '.' in email and len(email) > 5 and '..' not in email]
        return valid_emails[0] if valid_emails else "NA"
    
    return "NA"

def extract_phone(text: str) -> str:
    """Extract phone number using enhanced regex"""
    if not text or text.strip() == "":
        return "NA"
    
    phone_patterns = [
        r'\(\d{3}\)\s*\d{3}-\d{4}',  # (XXX) XXX-XXXX
        r'\b\d{3}-\d{3}-\d{4}\b',    # XXX-XXX-XXXX
        r'\b\d{3}\.\d{3}\.\d{4}\b',  # XXX.XXX.XXXX
        r'\+1\s*\d{3}\s*\d{3}\s*\d{4}',  # +1 XXX XXX XXXX
        r'\+?\d[\d\s-]{8,}\d'        # General pattern
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            digits = re.sub(r'\D', '', match.group(0))
            if 10 <= len(digits) <= 11:
                return match.group(0)
    
    return "NA"

def extract_zip_code(text: str) -> str:
    """Extract ZIP code using enhanced regex"""
    if not text or text.strip() == "":
        return "NA"
    
    zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
    matches = re.findall(zip_pattern, text)
    
    if matches:
        # Validate ZIP codes (basic US range)
        valid_zips = [zip_code for zip_code in matches 
                     if 1 <= int(zip_code[:5]) <= 99999]
        return valid_zips[0] if valid_zips else "NA"
    
    return "NA"

def extract_order_id(text: str) -> str:
    """Extract order ID using comprehensive regex"""
    if not text or text.strip() == "":
        return "NA"
    
    order_patterns = [
        r'order[:\s#]*([A-Za-z0-9]+)',
        r'order\s+(?:id|number)[:\s#]*([A-Za-z0-9]+)',
        r'#([A-Za-z0-9]+)',
        r'\b([A-Z]{2,}\d{4,}|\d{6,}[A-Z]+|[A-Z]\d{5,})\b',
        r'\b(?:order|ord|ref)[:\s#-]*([A-Za-z0-9]+)',
    ]
    
    for pattern in order_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            order_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
            # Validate order ID
            if order_id and len(order_id) >= 3:
                if not re.match(r'^\d{5}$|^\d{10}$', order_id):  # Avoid ZIP/phone
                    return order_id
    
    return "NA"

def regex_extract_fields(text: str) -> Dict[str, str]:
    """Legacy format for compatibility"""
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "zipCode": extract_zip_code(text),
        "orderId": extract_order_id(text),
    }

# LLM Extraction Class
class AsyncLLMExtractor:
    def __init__(self):
        # Use environment variable or default
        openai_key = os.getenv("OPENAI_API_KEY", "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")
        
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        os.environ["OPENAI_API_KEY"] = openai_key
        
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        schema = [
            ResponseSchema(name="email", description="Email address found in text"),
            ResponseSchema(name="phone", description="Phone number found in text"),
            ResponseSchema(name="zipCode", description="ZIP code found in text"),
            ResponseSchema(name="orderId", description="Order ID found in text"),
        ]
        
        self.parser = StructuredOutputParser.from_response_schemas(schema)
        self.instructions = self.parser.get_format_instructions()
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are an intelligent assistant that extracts structured data from customer service conversations.
        
        Extract the following information:
        - email: Email address (return single best match or "NA")
        - phone: Phone number (return single best match or "NA") 
        - zipCode: ZIP code (return single best match or "NA")
        - orderId: Order ID or reference number (return single best match or "NA")
        
        Return only "NA" if no valid information is found for each field.
        
        Conversation:
        {conversation}
        
        {format_instructions}
        """)

    async def extract_async(self, text: str) -> Dict[str, str]:
        try:
            prompt_input = self.prompt.format_prompt(
                conversation=text,
                format_instructions=self.instructions
            )
            
            output = await self.llm.agenerate([prompt_input.to_messages()])
            content = output.generations[0][0].text
            
            result = self.parser.parse(content)
            
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
    
    # Combine results (prefer LLM if available and not "NA")
    final_result = {}
    for field in ["email", "phone", "zipCode", "orderId"]:
        regex_val = regex_result.get(field, "NA")
        llm_val = llm_result.get(field, "NA") if LLM_AVAILABLE else "NA"
        
        # Prefer LLM result if it's not "NA", otherwise use regex
        if llm_val != "NA":
            final_result[field] = llm_val
        else:
            final_result[field] = regex_val
    
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
    
    # Extract fields first
    extract_request = ExtractRequest(text=request.content, fileName=request.fileName)
    extraction_result = await extract_fields(extract_request)
    
    # Save to database
    conversation_data = {
        "title": request.title,
        "content": request.content,
        "fileName": request.fileName
    }
    
    extracted_fields_dict = {
        "email": extraction_result.email,
        "phone": extraction_result.phone,
        "zipCode": extraction_result.zipCode, 
        "orderId": extraction_result.orderId,
        "metadata": extraction_result.metadata
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
            "email": extraction_result.email,
            "phone": extraction_result.phone,
            "zipCode": extraction_result.zipCode,
            "orderId": extraction_result.orderId,
        },
        "createdAt": datetime.now().isoformat()
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