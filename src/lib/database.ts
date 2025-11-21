import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.join(process.cwd(), 'data', 'extractify.db');

// Initialize database
const db = new Database(dbPath);

// Create tables
const initDb = () => {
  // Conversations table
  db.exec(`
    CREATE TABLE IF NOT EXISTS conversations (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      fileName TEXT,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Extracted fields table
  db.exec(`
    CREATE TABLE IF NOT EXISTS extracted_fields (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      conversationId TEXT NOT NULL,
      email TEXT,
      phone TEXT,
      zipCode TEXT,
      orderId TEXT,
      metadata TEXT,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (conversationId) REFERENCES conversations(id)
    )
  `);

  // Users table for future authentication
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE,
      name TEXT,
      provider TEXT,
      providerId TEXT,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
      updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  console.log('Database initialized successfully');
};

// Initialize on import
initDb();

// Database operations
export const dbOps = {
  // Conversations
  createConversation: (conversation: {
    id: string;
    title: string;
    content: string;
    fileName?: string;
  }) => {
    const stmt = db.prepare(`
      INSERT INTO conversations (id, title, content, fileName)
      VALUES (?, ?, ?, ?)
    `);
    return stmt.run(conversation.id, conversation.title, conversation.content, conversation.fileName);
  },

  getConversations: () => {
    const stmt = db.prepare(`
      SELECT c.*, ef.email, ef.phone, ef.zipCode, ef.orderId, ef.metadata
      FROM conversations c
      LEFT JOIN extracted_fields ef ON c.id = ef.conversationId
      ORDER BY c.createdAt DESC
    `);
    return stmt.all();
  },

  getConversationById: (id: string) => {
    const stmt = db.prepare(`
      SELECT c.*, ef.email, ef.phone, ef.zipCode, ef.orderId, ef.metadata
      FROM conversations c
      LEFT JOIN extracted_fields ef ON c.id = ef.conversationId
      WHERE c.id = ?
    `);
    return stmt.get(id);
  },

  deleteConversation: (id: string) => {
    const deleteFields = db.prepare('DELETE FROM extracted_fields WHERE conversationId = ?');
    const deleteConvo = db.prepare('DELETE FROM conversations WHERE id = ?');
    
    const transaction = db.transaction(() => {
      deleteFields.run(id);
      deleteConvo.run(id);
    });
    
    return transaction();
  },

  // Extracted fields
  createExtractedFields: (fields: {
    conversationId: string;
    email: string;
    phone: string;
    zipCode: string;
    orderId: string;
    metadata?: string;
  }) => {
    const stmt = db.prepare(`
      INSERT INTO extracted_fields (conversationId, email, phone, zipCode, orderId, metadata)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    return stmt.run(
      fields.conversationId,
      fields.email,
      fields.phone,
      fields.zipCode,
      fields.orderId,
      fields.metadata
    );
  },

  // Users (for future auth)
  createUser: (user: {
    id: string;
    email: string;
    name: string;
    provider: string;
    providerId: string;
  }) => {
    const stmt = db.prepare(`
      INSERT INTO users (id, email, name, provider, providerId)
      VALUES (?, ?, ?, ?, ?)
    `);
    return stmt.run(user.id, user.email, user.name, user.provider, user.providerId);
  },

  getUserByEmail: (email: string) => {
    const stmt = db.prepare('SELECT * FROM users WHERE email = ?');
    return stmt.get(email);
  },
};

export default db;