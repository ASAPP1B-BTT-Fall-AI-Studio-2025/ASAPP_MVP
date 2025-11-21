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

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const conversation = dbOps.getConversationById(params.id) as DatabaseConversation;
    
    if (!conversation) {
      return NextResponse.json(
        { error: 'Conversation not found' },
        { status: 404 }
      );
    }

    const formattedConversation = {
      id: conversation.id,
      title: conversation.title,
      content: conversation.content,
      extractedFields: {
        email: conversation.email || 'NA',
        phone: conversation.phone || 'NA',
        zipCode: conversation.zipCode || 'NA',
        orderId: conversation.orderId || 'NA',
      },
      fileName: conversation.fileName,
      createdAt: conversation.createdAt,
      metadata: conversation.metadata ? JSON.parse(conversation.metadata) : null,
    };

    return NextResponse.json(formattedConversation);
  } catch (error) {
    console.error('Error fetching conversation:', error);
    return NextResponse.json(
      { error: 'Failed to fetch conversation' },
      { status: 500 }
    );
  }
}