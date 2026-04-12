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

### Delete Case (Archive)

Archive a case by setting its status to `archived`. This is a **soft delete** - the case remains in the database but is marked as archived.

**Endpoint**: `DELETE /api/v1/cases/{case_id}`

**Authentication**: Required (ADMIN role only)

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | integer | Optional year for multi-year case ID disambiguation |

**Behavior**:
- **Soft Delete**: Sets `status` to `archived` and updates `updated_at` timestamp
- **Data Preserved**: Case data remains in database (not permanently deleted)
- **Reversible**: Can be restored by updating status back to `open`, `closed`, or `pending`

**Response (200)**:

```json
{
  "message": "Case archived successfully",
  "case_id": "CASE-2024-001"
}
```

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden (non-admin users)
- `404`: Case not found

**Example Request**:

```bash
curl -X DELETE "http://localhost:8000/api/v1/cases/CASE-2024-001?year=2024" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Important**: To permanently delete a case, use database admin tools directly (not recommended).

---

### Get Case Statistics Summary

Get aggregated case statistics with optional filtering.

**Endpoint**: `GET /api/v1/cases/stats/summary`

**Authentication**: Required (All authenticated users)

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `county` | string | Filter by county |
| `date_from` | string | Start date (YYYY-MM-DD) |
| `date_to` | string | End date (YYYY-MM-DD) |

**Response (200)**:

```json
{
  "total_cases": [{"count": 1542}],
  "by_abuse_type": [
    {"_id": "Physical", "count": 450},
    {"_id": "Neglect", "count": 380},
    {"_id": "Sexual", "count": 312}
  ],
  "by_status": [
    {"_id": "open", "count": 234},
    {"_id": "closed", "count": 1200},
    {"_id": "archived", "count": 108}
  ],
  "by_severity": [
    {"_id": "high", "count": 89},
    {"_id": "medium", "count": 512},
    {"_id": "low", "count": 941}
  ]
}
```

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/cases/stats/summary?county=Nairobi&date_from=2024-01-01" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Get Comprehensive Statistics

Get comprehensive case statistics including Kenya API metadata.

**Endpoint**: `GET /api/v1/cases/statistics`

**Authentication**: Required (All authenticated users)

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `include_kenya` | boolean | Include Kenya API metadata (default: true) |

**Response (200)**:

```json
{
  "total_cases": 1542,
  "by_status": {
    "open": 234,
    "closed": 1200,
    "pending": 0,
    "archived": 108
  },
  "by_county": [
    {"county": "Nairobi", "count": 450},
    {"county": "Mombasa", "count": 280}
  ],
  "kenya_api_metadata": {
    "last_sync": "2024-03-15T10:30:00Z",
    "total_records": 1200,
    "counties_covered": 47
  }
}
```

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/cases/statistics?include_kenya=true" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Sync Kenya API Data

Manually trigger synchronization with Kenya Child Protection API.

**Endpoint**: `POST /api/v1/cases/sync-kenya-data`

**Authentication**: Required (ADMIN or MEMBER role)

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `county` | string | Filter by county |
| `sub_county` | string | Filter by sub-county |
| `case_category` | string | Filter by case category |

**Behavior**:
- Fetches latest data from `https://data.childprotection.go.ke/api/v2/cld/`
- Automatically integrates with existing cases (deduplicates by case_id)
- Supports filtering to sync specific regions or categories
- Useful for on-demand data refresh

**Response (200)**:

```json
{
  "message": "Kenya API data sync completed",
  "details": {
    "records_fetched": 450,
    "records_inserted": 120,
    "records_updated": 30,
    "records_skipped": 300
  }
}
```

**Errors**:
- `401`: Unauthorized
- `403`: Forbidden (VIEWER role cannot sync)
- `500`: External API error

**Example Request**:

```bash
# Sync all data
curl -X POST "http://localhost:8000/api/v1/cases/sync-kenya-data" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Sync specific county
curl -X POST "http://localhost:8000/api/v1/cases/sync-kenya-data?county=Nairobi" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Case Status Values

| Status | Description |
|--------|-------------|
| `open` | Case is active and being handled |
| `closed` | Case has been resolved |
| `pending` | Case is awaiting action/review |
| `archived` | Case has been soft-deleted (via DELETE endpoint) |

**Note**: Archived cases remain in the database and can be restored by updating their status.

---

## Next Steps

- [Analytics API](analytics.md)
- [Authentication](authentication.md)
