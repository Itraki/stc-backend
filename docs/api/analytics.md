# Analytics API

Statistical data and aggregation endpoints.

**Base Path**: `/api/v1/analytics`

## Overview

The Analytics API provides comprehensive statistical insights into case data including trends, demographics, and geospatial analysis.

## Endpoints

### Summary Statistics

Get overall statistics.

**Endpoint**: `GET /api/v1/analytics/summary`

**Authentication**: Required

**Response**:

```json
{
  "total_cases": 1542,
  "open_cases": 234,
  "closed_cases": 1308,
  "high_severity": 89,
  "by_status": {
    "open": 234,
    "closed": 1308
  }
}
```

### Trend Analysis

Analyze case trends over time.

**Endpoint**: `GET /api/v1/analytics/trends`

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date (ISO 8601) |
| `end_date` | string | End date (ISO 8601) |
| `interval` | string | Grouping interval (day, week, month) |

### Demographics

Demographic breakdown of cases.

**Endpoint**: `GET /api/v1/analytics/demographics`

**Response**:

```json
{
  "age_distribution": {...},
  "gender_distribution": {...},
  "location_distribution": {...}
}
```

### Geospatial Data

Location-based case distribution.

**Endpoint**: `GET /api/v1/analytics/geospatial`

**Response**:

```json
{
  "locations": [
    {
      "name": "Nairobi",
      "coordinates": [-1.286389, 36.817223],
      "count": 234
    }
  ]
}
```

## Caching

Analytics endpoints are cached for improved performance. Cache TTL is 5 minutes by default.

## Next Steps

- [Cases API](cases.md)
- [Authentication](authentication.md)
