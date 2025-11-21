# Deployment Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) to view the application.

3. **Test the application:**
   - Use the sample conversation file in `/sample-data/sample-conversation.txt`
   - Try uploading the file or copying the text into the input area
   - Verify that the extracted fields show:
     - Email: john.smith@email.com
     - Phone: (555) 987-6543
     - ZIP Code: 90210
     - Order ID: ORD789123

## Production Deployment

### Vercel (Recommended)
```bash
npm run build
npx vercel --prod
```

### Other Platforms
1. Build the application:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

## Environment Variables

For production deployment, consider setting up:
- `DATABASE_URL` - for persistent storage
- `NEXTAUTH_SECRET` - for authentication
- `NEXTAUTH_URL` - for authentication callbacks

## Database Setup

Currently using in-memory storage. For production:

1. Set up a PostgreSQL or MongoDB database
2. Replace the in-memory arrays in `/src/app/api/conversations/route.ts`
3. Implement proper database models and migrations

## Authentication Integration

The UI includes placeholders for:
- GitHub OAuth
- Google OAuth  
- Email/Password authentication

Implement using NextAuth.js or similar authentication library.