# Analytics API

Statistical data and aggregation endpoints.

**Base Path**: `/api/v1/analytics`

## Overview

The Analytics API provides comprehensive statistical insights into case data including trends, demographics, and geospatial analysis.

All analytics endpoints support optional date range filtering and are cached for 5 minutes to improve performance.

## Endpoints

### Summary Statistics

Get overall statistics.

**Endpoint**: `GET /api/v1/analytics/summary`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date (ISO 8601, optional) |
| `end_date` | string | End date (ISO 8601, optional) |

**Response (200)**:

```json
{
  "total_cases": 1250,
  "active_cases": 450,
  "closed_cases": 750,
  "pending_cases": 50,
  "severity_breakdown": {
    "high": 300,
    "medium": 600,
    "low": 250,
    "unknown": 100
  },
  "counties": 47,
  "avg_age": 12.5,
  "gender_distribution": {
    "M": 620,
    "F": 630
  },
  "status_distribution": {
    "open": 450,
    "closed": 750,
    "pending": 50,
    "archived": 0
  }
}
```

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Trend Analysis

Analyze case trends over time.

**Endpoint**: `GET /api/v1/analytics/trends`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date (ISO 8601, **required**) |
| `end_date` | string | End date (ISO 8601, **required**) |
| `interval` | string | Grouping interval: `day`, `week`, `month` (default: `month`) |

**Response (200)**:

```json
{
  "period": "2024-01-01 to 2024-12-31",
  "interval": "month",
  "data": [
    {
      "period": "2024-01",
      "total": 105,
      "high_severity": 25,
      "medium_severity": 50,
      "low_severity": 30,
      "growth_rate": 5.2
    },
    {
      "period": "2024-02",
      "total": 98,
      "high_severity": 22,
      "medium_severity": 48,
      "low_severity": 28,
      "growth_rate": -6.7
    }
  ]
}
```

**Errors**:
- `401`: Unauthorized
- `422`: Invalid date range (start_date > end_date)

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/trends?start_date=2024-01-01&end_date=2024-12-31&interval=month" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Demographics

Demographic breakdown of cases.

**Endpoint**: `GET /api/v1/analytics/demographics`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date (ISO 8601, optional) |
| `end_date` | string | End date (ISO 8601, optional) |

**Response (200)**:

```json
{
  "age_distribution": {
    "0-5": 150,
    "6-9": 280,
    "10-14": 520,
    "15-18": 300
  },
  "gender_distribution": {
    "M": 620,
    "F": 630
  },
  "abuse_types": {
    "Physical": 450,
    "Emotional": 320,
    "Neglect": 280,
    "Sexual": 200
  },
  "county_distribution": {
    "Nairobi": 250,
    "Mombasa": 180,
    "Kisumu": 150,
    "...": "..."
  }
}
```

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/demographics" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Severity Analysis

Analyze severity distribution.

**Endpoint**: `GET /api/v1/analytics/severity`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `county` | string | Filter by county (optional) |
| `start_date` | string | Start date (ISO 8601, optional) |
| `end_date` | string | End date (ISO 8601, optional) |

**Response (200)**:

```json
{
  "total": 1250,
  "high": 300,
  "medium": 600,
  "low": 250,
  "unknown": 100,
  "percentage": {
    "high": 24.0,
    "medium": 48.0,
    "low": 20.0,
    "unknown": 8.0
  },
  "by_county": [
    {
      "county": "Nairobi",
      "high": 60,
      "medium": 120,
      "low": 50
    }
  ]
}
```

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/severity?county=Nairobi" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Geospatial Data

Location-based case distribution.

**Endpoint**: `GET /api/v1/analytics/geospatial`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `county` | string | Filter by county (optional) |
| `start_date` | string | Start date (ISO 8601, optional) |
| `end_date` | string | End date (ISO 8601, optional) |

**Response (200)**:

GeoJSON FeatureCollection format for mapping:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [36.8219, -1.2921]
      },
      "properties": {
        "case_id": "KE-2024-001234",
        "county": "Nairobi",
        "severity": "high",
        "abuse_type": "Physical",
        "created_at": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

**Example Request**:

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/geospatial?county=Nairobi" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Caching

Analytics endpoints are cached for improved performance:

- **Cache Duration**: 5 minutes (300 seconds)
- **Cache Key**: Based on endpoint + query parameters
- **Cache Invalidation**: Automatic on data updates (case creation/update/deletion)

**Cache Headers**:

```
X-Cache: HIT
X-Cache-TTL: 285
```

---

## Performance Considerations

### Aggregation Pipeline

Analytics use MongoDB aggregation pipelines optimized for performance:

```javascript
// Example: Summary statistics aggregation
db.cases.aggregate([
  { $match: { case_date: { $gte: start_date, $lte: end_date } } },
  { $group: {
      _id: "$severity",
      count: { $sum: 1 }
    }
  }
])
```

### Indexes

The following indexes improve analytics query performance:

- `case_date` (for date range filters)
- `county` (for location filters)
- `severity` (for severity grouping)
- `status` (for status grouping)

---

## Business Logic

### Growth Rate Calculation

Trend analysis includes growth rate calculation:

```python
growth_rate = ((current - previous) / previous) * 100 if previous > 0 else 0
```

### Age Range Classification

Ages are grouped into standard brackets:

- **0-5**: Early childhood
- **6-9**: Middle childhood
- **10-14**: Early adolescence
- **15-18**: Late adolescence

---

## Next Steps

- [Cases API](cases.md)
- [Authentication](authentication.md)
- [Data Models](../development/data-models.md)
