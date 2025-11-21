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

## Technology Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes
- **Icons**: Lucide React
- **Machine Learning**: Custom regex-based field extraction (based on Jupyter notebook analysis)

## 🏗️ Project Structure

```
ASAPP_MVP/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── conversations/
│   │   │   │   ├── [id]/            # Individual conversation details
│   │   │   │   └── route.ts         # CRUD operations for conversations
│   │   │   └── extract/
│   │   │       └── route.ts         # Field extraction API
│   │   ├── globals.css              # Global styles with gradients
│   │   ├── layout.tsx
│   │   └── page.tsx                 # Main application page
│   ├── components/
│   │   ├── ConversationHistory.tsx  # Left sidebar conversation list
│   │   ├── ConversationInput.tsx    # Text input component
│   │   ├── ExtractedFieldsDisplay.tsx # Right sidebar results
│   │   ├── FileUpload.tsx           # Drag & drop file upload
│   │   └── Header.tsx               # Navigation with Extractify branding
│   └── lib/
│       ├── database.ts              # SQLite database operations
│       ├── fieldExtractor.ts        # Basic extraction logic
│       ├── enhancedFieldExtractor.ts # Advanced extraction with FastAPI integration
│       └── ml/                      # Original ML analysis notebooks
├── data/
│   └── extractify.db                # SQLite database file
├── sample-data/
│   └── sample-conversation.txt      # Test data for extraction
└── public/                          # Static assets
```

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ASAPP_MVP
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

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

## API Endpoints

### POST /api/extract
Extract fields from conversation text.

**Request Body:**
```json
{
  "text": "conversation text here",
  "fileName": "optional-file-name.txt"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "phone": "(555) 123-4567",
  "zipCode": "12345",
  "orderId": "ORD123456",
  "metadata": {
    "fileName": "conversation.txt",
    "processedAt": "2024-01-01T00:00:00.000Z",
    "textLength": 150
  }
}
```

### GET /api/conversations
Retrieve all stored conversations.

### POST /api/conversations
Store a new conversation with extracted fields.

### DELETE /api/conversations?id=<id>
Delete a specific conversation.

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
