import { NextRequest, NextResponse } from 'next/server';
import { dbOps } from '@/lib/database';

interface DatabaseConversation {
  id: string;
  title: string;
  content: string;
  fileName?: string;
  createdAt: string;
  email?: string;
  phone?: string;
  zipCode?: string;
  orderId?: string;
  metadata?: string;
}

export async function GET() {
  try {
    const conversations = dbOps.getConversations() as DatabaseConversation[];
    
    // Transform database results to match frontend expectations
    const formattedConversations = conversations.map((conv) => ({
      id: conv.id,
      title: conv.title,
      date: new Date(conv.createdAt).toLocaleDateString(),
      preview: conv.content.substring(0, 100) + '...',
      content: conv.content,
      extractedFields: {
        email: conv.email || 'NA',
        phone: conv.phone || 'NA',
        zipCode: conv.zipCode || 'NA',
        orderId: conv.orderId || 'NA',
      },
      fileName: conv.fileName,
      createdAt: conv.createdAt,
    }));

    return NextResponse.json(formattedConversations);
  } catch (error) {
    console.error('Error fetching conversations:', error);
    return NextResponse.json(
      { error: 'Failed to fetch conversations' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, content, extractedFields, fileName } = body;

    if (!title || !content || !extractedFields) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Generate conversation ID
    const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Save conversation
    dbOps.createConversation({
      id: conversationId,
      title,
      content,
      fileName,
    });

    // Save extracted fields
    dbOps.createExtractedFields({
      conversationId,
      email: extractedFields.email || 'NA',
      phone: extractedFields.phone || 'NA',
      zipCode: extractedFields.zipCode || 'NA',
      orderId: extractedFields.orderId || 'NA',
      metadata: JSON.stringify(extractedFields.metadata || {}),
    });

    const newConversation = {
      id: conversationId,
      title,
      date: new Date().toLocaleDateString(),
      preview: content.substring(0, 100) + '...',
      content,
      extractedFields,
      fileName,
      createdAt: new Date().toISOString(),
    };

    return NextResponse.json(newConversation);
  } catch (error) {
    console.error('Error creating conversation:', error);
    return NextResponse.json(
      { error: 'Failed to create conversation' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'Conversation ID is required' },
        { status: 400 }
      );
    }

    dbOps.deleteConversation(id);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting conversation:', error);
    return NextResponse.json(
      { error: 'Failed to delete conversation' },
      { status: 500 }
    );
  }
}