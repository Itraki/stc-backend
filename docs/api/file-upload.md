# File Upload API

Document upload and management endpoints.

**Base Path**: `/api/v1/files`

## Overview

The File Upload API handles PDF and DOCX document uploads with automatic text extraction and vectorization for RAG.

## Endpoints

### Upload File

Upload a document file.

**Endpoint**: `POST /api/v1/files/upload`

**Authentication**: Required (MEMBER or ADMIN)

**Request**: Multipart form-data

```
file: document.pdf
metadata: {"category": "report", "tags": ["annual"]}
```

**Response**:

```json
{
  "file_id": "507f1f77bcf86cd799439011",
  "filename": "document.pdf",
  "size": 2048576,
  "content_type": "application/pdf",
  "uploaded_at": "2024-02-22T14:30:00Z",
  "chunks_created": 45
}
```

**cURL Example**:

```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"
```

### List Files

List all uploaded files.

**Endpoint**: `GET /api/v1/files`

**Authentication**: Required

**Response**:

```json
{
  "files": [
    {
      "file_id": "507f1f77bcf86cd799439011",
      "filename": "document.pdf",
      "size": 2048576,
      "uploaded_at": "2024-02-22T14:30:00Z"
    }
  ]
}
```

### Delete File

Delete an uploaded file.

**Endpoint**: `DELETE /api/v1/files/{file_id}`

**Authentication**: Required (ADMIN or file owner)

## Supported Formats

- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain text (`.txt`)

## File Size Limits

- Maximum file size: 10 MB
- Maximum files per user: 100

## Processing

Uploaded files are automatically:

1. **Text extracted** using appropriate parser
2. **Chunked** into semantic segments
3. **Embedded** using configured provider
4. **Stored** in vector database for RAG

## Next Steps

- [Chatbot API](chatbot.md)
- [Getting Started](../getting-started/quickstart.md)
