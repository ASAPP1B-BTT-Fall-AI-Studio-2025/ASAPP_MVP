# Extractify

A beautiful, modern Next.js application that uses advanced AI/ML techniques to extract structured data from unstructured conversation text. Extractify provides an intuitive interface for uploading conversation files or inputting text directly to extract key information like email addresses, phone numbers, ZIP codes, and order IDs.

## ✨ Features

- **🎨 Modern UI/UX**: Beautiful gradient design with smooth animations and transitions
- **📁 File Upload**: Intuitive drag-and-drop interface supporting .txt, .csv, .json files
- **✍️ Text Input**: Direct text input for real-time conversation processing
- **🤖 AI-Powered Extraction**: Enhanced regex patterns with optional LLM integration
- **📊 Conversation Management**: Persistent storage with SQLite database
- **💾 Data Export**: Download extracted fields as JSON
- **📱 Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **⚡ Real-time Processing**: Instant field extraction and validation

## 🎨 Design Philosophy

Extractify features a modern gradient-based design with:
- **Smooth Color Transitions**: Blue to purple gradients throughout the interface
- **Interactive Elements**: Hover effects, scale transforms, and smooth transitions
- **Accessibility First**: Clear contrast ratios and semantic HTML structure
- **Component-Based Architecture**: Modular, reusable React components

## 🛠️ Technology Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python) with SQLite database
- **AI/ML**: 
  - Enhanced regex patterns for fast extraction
  - OpenAI GPT-4o-mini for intelligent LLM extraction
  - Hybrid approach combining both methods
- **Icons**: Lucide React
- **Database**: SQLite with async operations

## 🏗️ Project Structure

```
Extractify/
├── frontend (Next.js)
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css              # Global styles with gradients
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx                 # Main application page
│   │   ├── components/
│   │   │   ├── ConversationHistory.tsx  # Left sidebar conversation list
│   │   │   ├── ConversationInput.tsx    # Text input component
│   │   │   ├── ExtractedFieldsDisplay.tsx # Right sidebar results
│   │   │   ├── FileUpload.tsx           # Drag & drop file upload
│   │   │   └── Header.tsx               # Navigation with Extractify branding
│   │   └── lib/
│   │       ├── fieldExtractor.ts        # Basic extraction logic
│   │       ├── enhancedFieldExtractor.ts # Advanced extraction patterns
│   │       └── fastApiIntegration.ts    # FastAPI integration utilities
├── backend/ (FastAPI)
│   ├── main.py                          # FastAPI server with hybrid extraction
│   ├── requirements.txt                 # Python dependencies
│   └── data/
│       └── extractify_fastapi.db        # SQLite database
├── sample-data/
│   └── sample-conversation.txt          # Test data for extraction
├── setup.sh                             # Development setup script
└── .env.local                           # Environment configuration
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.x or later
- **Python** 3.8 or later
- **OpenAI API Key** (for LLM extraction)

### Quick Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd Extractify
   ./setup.sh
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local and add your OPENAI_API_KEY
   ```

3. **Start the backend (FastAPI):**
   ```bash
   npm run backend
   # Or manually: cd backend && python main.py
   ```

4. **Start the frontend (Next.js) in another terminal:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Manual Setup

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend Setup:**
```bash
npm install
npm run dev
```

## Usage

### Text Input Method
1. Type or paste conversation text into the "Input Conversation" section
2. Click "Extract Fields" to process the text
3. View extracted fields in the right sidebar

### File Upload Method
1. Drag and drop a file into the upload area or click "browse" to select a file
2. Supported formats: .txt, .csv, .json
3. The file will be automatically processed upon upload
4. View extracted fields and conversation history

### Field Extraction

The application extracts four main types of fields:

- **Email**: Standard email address patterns
- **Phone**: Phone numbers with format (XXX) XXX-XXXX
- **ZIP Code**: 5-digit US ZIP codes
- **Order ID**: Various order ID formats including:
  - "order" followed by alphanumeric
  - "order id/number" patterns
  - Hash symbol followed by alphanumeric
  - Standalone alphanumeric order-like strings

### Conversation Management

- All processed conversations are stored in memory (production should use a database)
- Click on conversation history items to view previous extractions
- Conversations include metadata like processing date and file information

## 🎯 API Architecture

### FastAPI Backend Endpoints

- **GET** `/` - API status and health check
- **POST** `/extract` - Extract fields from conversation text
- **GET** `/conversations` - Retrieve all conversations
- **GET** `/conversations/{id}` - Get specific conversation
- **POST** `/conversations` - Create new conversation with extraction
- **DELETE** `/conversations/{id}` - Delete conversation
- **GET** `/health` - Backend health and LLM availability check

### Extraction Methods

1. **Regex Extraction** (Always available):
   - Fast pattern matching for common formats
   - Enhanced patterns based on your notebook analysis
   - Handles emails, phones, ZIP codes, order IDs

2. **LLM Extraction** (Optional with OpenAI API):
   - GPT-4o-mini for intelligent field extraction
   - Context-aware understanding
   - Better handling of complex conversation formats

3. **Hybrid Approach** (Best of both):
   - Combines regex speed with LLM intelligence
   - Fallback to regex if LLM unavailable
   - Prioritizes LLM results when available

## Development

### Running Tests
```bash
npm test
```

### Building for Production
```bash
npm run build
npm start
```

### Linting
```bash
npm run lint
```

## Future Enhancements

Based on the mockup design, planned features include:

1. **Authentication System**
   - GitHub OAuth integration
   - Google OAuth integration
   - Email/password authentication

2. **Advanced Analytics**
   - Batch conversation processing
   - EDA visualizations
   - Extraction accuracy metrics

3. **Database Integration**
   - Persistent conversation storage
   - User management
   - Audit trails

4. **Enhanced ML Models**
   - Integration with more sophisticated NLP models
   - Custom field type definitions
   - Confidence scoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
