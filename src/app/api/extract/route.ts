import { NextRequest, NextResponse } from 'next/server';
import { extractAllFieldsWithMetadata } from '@/lib/enhancedFieldExtractor';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { text, fileName } = body;

    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: 'Text content is required' },
        { status: 400 }
      );
    }

    // Extract fields from the conversation text using enhanced extractor
    const extractedFields = extractAllFieldsWithMetadata(text, fileName);

    return NextResponse.json(extractedFields);
  } catch (error) {
    console.error('Error processing extraction:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}