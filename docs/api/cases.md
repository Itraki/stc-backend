# Cases API

Complete reference for case management endpoints.

**Base Path**: `/api/v1/cases`

## Overview

The Cases API provides full CRUD operations for child protection case management with advanced filtering, pagination, and search capabilities.

## Endpoints

### List Cases

Get a paginated list of cases with optional filtering.

**Endpoint**: `GET /api/v1/cases`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 20, max: 100) |
| `status` | string | Filter by status |
| `severity` | string | Filter by severity |
| `start_date` | string | Filter from date (ISO 8601) |
| `end_date` | string | Filter to date (ISO 8601) |
| `location` | string | Filter by location |
| `search` | string | Full-text search |

**Response**:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

### Get Case Details

Retrieve detailed information about a specific case.

**Endpoint**: `GET /api/v1/cases/{case_id}`

**Authentication**: Required

**Response**:

```json
{
  "case_id": "CASE-2024-001",
  "status": "open",
  "severity": "high",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-02-20T14:20:00Z",
  "location": "Nairobi",
  "description": "Case description...",
  "child_demographics": {
    "age": 12,
    "gender": "Female"
  }
}
```

### Create Case

Create a new child protection case.

**Endpoint**: `POST /api/v1/cases`

**Authentication**: Required (MEMBER or ADMIN role)

**Request Body**:

```json
{
  "case_id": "string (unique)",
  "case_date": "2024-01-15T00:00:00Z",
  "county": "string",
  "subcounty": "string",
  "child_age": 12,
  "child_sex": "M|F",
  "abuse_type": "string",
  "description": "string",
  "severity": "low|medium|high|unknown",
  "latitude": 0.0,
  "longitude": 0.0
}
```

**Response (201)**:

```json
{
  "id": "string",
  "case_id": "CASE-2024-001",
  "message": "Case created successfully",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors**:
- `400`: Invalid input data
- `401`: Unauthorized
- `403`: Forbidden (insufficient permissions)
- `422`: Validation error (e.g., duplicate case_id)

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/v1/cases" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "KE-2024-001234",
    "case_date": "2024-01-15T00:00:00Z",
    "county": "Nairobi",
    "subcounty": "Westlands",
    "child_age": 12,
    "child_sex": "F",
    "abuse_type": "Physical",
    "description": "Case details...",
    "severity": "high",
    "latitude": -1.2921,
    "longitude": 36.8219
  }'
```

---

### Update Case

Update an existing case.

**Endpoint**: `PUT /api/v1/cases/{case_id}`

**Authentication**: Required (MEMBER or ADMIN role)

**Request Body**:

```json
{
  "case_date": "2024-01-15T00:00:00Z (optional)",
  "status": "open|closed|pending|archived (optional)",
  "severity": "low|medium|high|unknown (optional)",
  "description": "string (optional)"
}
```

**Response (200)**:

```json
{
  "id": "string",
  "message": "Case updated successfully",
  "updated_at": "2024-01-15T12:45:00Z"
}
```

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Case not found
- `422`: Validation error

**Example Request**:

```bash
curl -X PUT "http://localhost:8000/api/v1/cases/CASE-2024-001" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "closed",
    "severity": "medium"
  }'
```

---

### Delete Case

Delete a case (admin only).

**Endpoint**: `DELETE /api/v1/cases/{case_id}`

**Authentication**: Required (ADMIN role only)

**Response (204)**:
No content

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden (non-admin users)
- `404`: Case not found

**Example Request**:

```bash
curl -X DELETE "http://localhost:8000/api/v1/cases/CASE-2024-001" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Next Steps

- [Analytics API](analytics.md)
- [Authentication](authentication.md)
