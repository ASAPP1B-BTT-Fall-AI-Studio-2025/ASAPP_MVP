#!/bin/bash

# Extractify Development Setup Script

echo "🚀 Starting Extractify Development Environment"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Install Python dependencies for FastAPI backend
echo "📦 Installing FastAPI backend dependencies..."
cd backend
python3 -m pip install -r requirements.txt
cd ..

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js frontend dependencies..."
npm install

echo "✅ Dependencies installed successfully!"

# Instructions
echo ""
echo "🎯 To start the development environment:"
echo ""
echo "1. Start FastAPI backend (in one terminal):"
echo "   cd backend && python main.py"
echo ""
echo "2. Start Next.js frontend (in another terminal):"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "💡 Make sure to set your OPENAI_API_KEY in .env.local for LLM extraction!"