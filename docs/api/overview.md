# API Overview

The Save The Children Backend provides a comprehensive RESTful API for managing child protection cases, analytics, and AI-powered assistance.

## Base URL

```
Local Development: http://localhost:8000
Production: https://api.yoursite.com
```

## Interactive Documentation

- **Swagger UI**: `/docs` - Interactive API testing
- **ReDoc**: `/redoc` - Beautiful API documentation

## API Versioning

All endpoints are versioned under `/api/v1/`:

```
/api/v1/auth/...      # Authentication
/api/v1/cases/...     # Case management
/api/v1/analytics/... # Analytics & reporting
/api/v1/chatbot/...   # AI chatbot
```

## Authentication

Most endpoints require authentication using JWT tokens:

```bash
curl -X GET "http://localhost:8000/api/v1/cases" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

See [Authentication Guide](authentication.md) for details.

## Endpoint Categories

### 🔐 Authentication (`/api/v1/auth/`)

User registration, login, and token management.

- `POST /register` - Create new user account
- `POST /login` - Login and get tokens
- `GET /me` - Get current user profile
- `POST /refresh` - Refresh access token
- `POST /logout` - Logout user

[Authentication API Documentation →](authentication.md)

### 📋 Cases (`/api/v1/cases/`)

CRUD operations for child protection cases.

- `GET /cases` - List cases with filtering
- `POST /cases` - Create new case
- `GET /cases/{id}` - Get case details
- `PUT /cases/{id}` - Update case
- `DELETE /cases/{id}` - Delete case

[Cases API Documentation →](cases.md)

### 📊 Analytics (`/api/v1/analytics/`)

Statistical data and aggregations.

- `GET /summary` - Overall statistics
- `GET /trends` - Trend analysis
- `GET /demographics` - Demographic breakdown
- `GET /severity` - Severity distribution
- `GET /geospatial` - Geospatial data

[Analytics API Documentation →](analytics.md)

### 🤖 Chatbot (`/api/v1/chatbot/`)

AI-powered assistance with RAG capabilities.

- `POST /sse` - Stream chat responses (SSE)
- `POST /query` - Ask questions about cases
- `POST /upload` - Upload documents for RAG

[Chatbot API Documentation →](chatbot.md)

### 📁 Files (`/api/v1/files/`)

Document upload and management.

- `POST /upload` - Upload PDF/DOCX files
- `GET /files` - List uploaded files
- `DELETE /files/{id}` - Delete file

[File Upload API Documentation →](file-upload.md)

## Response Format

All responses follow a consistent JSON format:

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "detail": "Error message here",
  "status_code": 400
}
```

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Rate Limiting

Default rate limits:

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Admin**: 5000 requests/hour

## Pagination

List endpoints support pagination:

```bash
GET /api/v1/cases?page=1&limit=20
```

Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

## Filtering

Most list endpoints support filtering:

```bash
# Filter by date range
GET /api/v1/cases?start_date=2024-01-01&end_date=2024-12-31

# Filter by multiple fields
GET /api/v1/cases?status=open&severity=high&location=Nairobi
```

## Sorting

Use `sort_by` and `order` parameters:

```bash
GET /api/v1/cases?sort_by=created_at&order=desc
```

## CORS

CORS is enabled for trusted origins. Configure in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com
```

## API Clients

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
cases = requests.get(f"{BASE_URL}/api/v1/cases", headers=headers)
print(cases.json())
```

### JavaScript/TypeScript

```javascript
const BASE_URL = "http://localhost:8000";

// Login
const loginResponse = await fetch(`${BASE_URL}/api/v1/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "user@example.com",
    password: "password123"
  })
});
const { access_token } = await loginResponse.json();

// Make authenticated request
const casesResponse = await fetch(`${BASE_URL}/api/v1/cases`, {
  headers: { "Authorization": `Bearer ${access_token}` }
});
const cases = await casesResponse.json();
```

### cURL

```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Use token
curl -X GET "http://localhost:8000/api/v1/cases" \
  -H "Authorization: Bearer $TOKEN"
```

## OpenAPI Specification

Download the OpenAPI specification:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

Use with tools like:
- Postman (import OpenAPI spec)
- Insomnia (import OpenAPI spec)
- OpenAPI Generator (generate client SDKs)

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (HttpOnly cookies or secure storage)
3. **Implement token refresh** before expiration
4. **Handle rate limits** gracefully
5. **Validate input** on the client side
6. **Use pagination** for large datasets
7. **Cache responses** when appropriate

## Next Steps

- [Authentication API →](authentication.md)
- [Cases API →](cases.md)
- [Analytics API →](analytics.md)
- [Chatbot API →](chatbot.md)
