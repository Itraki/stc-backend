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
  "status": "open",
  "severity": "high",
  "location": "Nairobi",
  "description": "Case description",
  "child_demographics": {
    "age": 12,
    "gender": "Female"
  }
}
```

### Update Case

Update an existing case.

**Endpoint**: `PUT /api/v1/cases/{case_id}`

**Authentication**: Required (MEMBER or ADMIN role)

### Delete Case

Delete a case.

**Endpoint**: `DELETE /api/v1/cases/{case_id}`

**Authentication**: Required (ADMIN role only)

## Next Steps

- [Analytics API](analytics.md)
- [Authentication](authentication.md)
