# Chatbot API

AI-powered assistance with RAG capabilities.

**Base Path**: `/api/v1/chatbot`

## Overview

The Chatbot API provides AI-powered question-answering using LangChain, Groq LLM, and RAG (Retrieval Augmented Generation) for context-aware responses.

## Endpoints

### Stream Chat Response (SSE)

Real-time streaming chat responses using Server-Sent Events.

**Endpoint**: `POST /api/v1/chatbot/sse`

**Authentication**: Required

**Request Body**:

```json
{
  "message": "What are the recent high-severity cases?",
  "conversation_id": "optional-conversation-id"
}
```

**Response**: Server-Sent Events stream

```
event: message
data: {"chunk": "Based on the data, there are..."}

event: message
data: {"chunk": " 15 high-severity cases..."}

event: done
data: {"message": "Stream complete"}
```

**JavaScript Example**:

```javascript
const eventSource = new EventSource('/api/v1/chatbot/sse', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'What are the recent cases?'
  })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.chunk);
};
```

### Query

Non-streaming query endpoint.

**Endpoint**: `POST /api/v1/chatbot/query`

**Authentication**: Required

**Request Body**:

```json
{
  "query": "How many cases are in Nairobi?"
}
```

**Response**:

```json
{
  "answer": "There are 234 cases in Nairobi...",
  "sources": [...],
  "confidence": 0.92
}
```

### Upload Document

Upload documents for RAG context.

**Endpoint**: `POST /api/v1/chatbot/upload`

**Authentication**: Required (MEMBER or ADMIN)

**Request**: Multipart form data

```
file: document.pdf
```

**Response**:

```json
{
  "file_id": "507f1f77bcf86cd799439011",
  "filename": "document.pdf",
  "chunks_processed": 45
}
```

## Features

- **Real-time streaming** via SSE
- **RAG integration** with pgvector
- **Multi-provider embeddings** (Google AI, OpenAI, local)
- **Document processing** (PDF, DOCX)
- **Conversation history**

## Next Steps

- [File Upload API](file-upload.md)
- [Getting Started](../getting-started/quickstart.md)
