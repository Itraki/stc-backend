# Data Models

Complete reference for data structures and schemas used in the API.

## Table of Contents

1. [User Model](#user-model)
2. [Case Model](#case-model)
3. [File Model](#file-model)
4. [Conversation Model](#conversation-model)
5. [Enumerations](#enumerations)

---

## User Model

**Collection**: `users`

**Description**: Represents system users with role-based access.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `_id` | ObjectId | Primary Key | MongoDB auto-generated ID |
| `username` | String | Unique, 3-50 chars | User's username for login |
| `email` | EmailStr | Unique, Valid Email | User's email address |
| `password_hash` | String | Required | Bcrypt hashed password |
| `full_name` | String | Required | User's full display name |
| `role` | Enum | admin\|member\|viewer | User's access role |
| `is_active` | Boolean | Default: True | Account activation status |
| `created_at` | DateTime | Auto-generated | Account creation timestamp |
| `updated_at` | DateTime | Auto-updated | Last modification timestamp |

### Example Document

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password_hash": "$2b$12$KIXxLVqE...",
  "full_name": "John Doe",
  "role": "member",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Pydantic Schema

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: UserRole = UserRole.VIEWER

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
```

---

## Case Model

**Collection**: `cases`

**Description**: Child protection case records.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `_id` | ObjectId | Primary Key | MongoDB auto-generated ID |
| `case_id` | String | Unique, Required | Unique case identifier |
| `case_year` | Integer | Optional | Year extracted from case_date |
| `case_date` | DateTime | Required | Date when case occurred |
| `county` | String | Required | Kenyan county name |
| `subcounty` | String | Optional | Sub-county/constituency |
| `child_age` | Integer | 0-18 | Age of child victim |
| `age_range` | String | Optional | Computed age bracket (0-5, 6-9, 10-14, 15-18) |
| `child_sex` | String | M\|F | Gender of child |
| `abuse_type` | String | Required | Type of abuse reported |
| `description` | String | Optional | Detailed description |
| `intervention` | String | Optional | Intervention taken |
| `status` | Enum | open\|closed\|pending\|archived | Current case status |
| `severity` | Enum | low\|medium\|high\|unknown | Severity assessment |
| `latitude` | Float | Optional | Location latitude |
| `longitude` | Float | Optional | Location longitude |
| `created_at` | DateTime | Auto-generated | Record creation timestamp |
| `updated_at` | DateTime | Auto-updated | Last modification timestamp |

### Computed Fields

- **`age_range`**: Automatically computed from `child_age`
  - 0-5, 6-9, 10-14, 15-18
- **`case_year`**: Extracted from `case_date`

### Example Document

```json
{
  "_id": "507f1f77bcf86cd799439012",
  "case_id": "KE-2024-001234",
  "case_year": 2024,
  "case_date": "2024-01-15T00:00:00Z",
  "county": "Nairobi",
  "subcounty": "Westlands",
  "child_age": 12,
  "age_range": "10-14",
  "child_sex": "F",
  "abuse_type": "Physical",
  "description": "Case details...",
  "intervention": "Counseling provided",
  "status": "open",
  "severity": "high",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Pydantic Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime

class CaseCreate(BaseModel):
    case_id: str
    case_date: datetime
    county: str
    subcounty: str
    child_age: int = Field(..., ge=0, le=18)
    child_sex: str
    abuse_type: str
    description: str
    severity: SeverityLevel
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CaseResponse(BaseModel):
    id: str = Field(alias="_id")
    case_id: str
    case_year: Optional[int] = None
    case_date: datetime
    county: str
    subcounty: Optional[str] = None
    child_age: Optional[int] = None
    age_range: Optional[str] = None
    child_sex: Optional[str] = None
    abuse_type: str
    description: Optional[str] = None
    intervention: Optional[str] = None
    status: CaseStatus
    severity: SeverityLevel
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime
```

### Indexes

```javascript
// MongoDB indexes for performance
db.cases.createIndex({ "case_id": 1 }, { unique: true })
db.cases.createIndex({ "case_date": 1 })
db.cases.createIndex({ "county": 1 })
db.cases.createIndex({ "status": 1 })
db.cases.createIndex({ "severity": 1 })
db.cases.createIndex({ "created_at": -1 })
db.cases.createIndex({ "latitude": 1, "longitude": 1 }) // Geospatial
```

---

## File Model

**Collection**: `files`

**Description**: Uploaded document metadata.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `_id` | ObjectId | Primary Key | MongoDB auto-generated ID |
| `file_id` | String | Unique | Unique file identifier |
| `filename` | String | Required | Original filename |
| `size` | Integer | Required | File size in bytes |
| `content_type` | String | Required | MIME type |
| `storage_path` | String | Required | Path in storage system |
| `uploaded_by` | ObjectId | Foreign Key → users | User who uploaded |
| `uploaded_at` | DateTime | Auto-generated | Upload timestamp |
| `metadata` | Object | Optional | Additional metadata |

### Example Document

```json
{
  "_id": "507f1f77bcf86cd799439013",
  "file_id": "file_abc123",
  "filename": "report.pdf",
  "size": 1024567,
  "content_type": "application/pdf",
  "storage_path": "/uploads/2024/01/report.pdf",
  "uploaded_by": "507f1f77bcf86cd799439011",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "checksum": "sha256:abc123...",
    "indexed": true
  }
}
```

---

## Conversation Model

**Collection**: `conversations`

**Description**: AI chatbot conversation history.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `_id` | ObjectId | Primary Key | MongoDB auto-generated ID |
| `conversation_id` | String | Unique | Unique conversation identifier |
| `user_id` | ObjectId | Foreign Key → users | User who owns conversation |
| `messages` | Array[Message] | Required | List of messages |
| `created_at` | DateTime | Auto-generated | Conversation start time |
| `updated_at` | DateTime | Auto-updated | Last message time |

### Message Sub-document

```json
{
  "role": "user|assistant",
  "content": "string",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Example Document

```json
{
  "_id": "507f1f77bcf86cd799439014",
  "conversation_id": "conv_abc123",
  "user_id": "507f1f77bcf86cd799439011",
  "messages": [
    {
      "role": "user",
      "content": "Show me high-severity cases in Nairobi",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I found 23 high-severity cases in Nairobi...",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:05Z"
}
```

---

## Enumerations

### UserRole

```python
class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
```

**Hierarchy**:
- **ADMIN**: Full access (create, read, update, delete all resources)
- **MEMBER**: Create, read, update (no delete)
- **VIEWER**: Read-only access

---

### CaseStatus

```python
class CaseStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
    ARCHIVED = "archived"
```

**Lifecycle**:
```
OPEN → PENDING → CLOSED → ARCHIVED
```

---

### SeverityLevel

```python
class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"
```

**Criteria**:
- **HIGH**: Serious injuries, sexual abuse, immediate danger
- **MEDIUM**: Physical or emotional abuse, moderate risk
- **LOW**: Neglect, minor incidents
- **UNKNOWN**: Insufficient information

---

## Validation Rules

### User Validation

```python
# Username: 3-50 characters, alphanumeric + underscore
username_pattern = r'^[a-zA-Z0-9_]{3,50}$'

# Email: Valid email format
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Password: Minimum 8 characters
password_min_length = 8
```

### Case Validation

```python
# Child age: 0-18 years
assert 0 <= child_age <= 18

# Date: Not in future
assert case_date <= datetime.now()

# County: Must be valid Kenyan county
assert county in KENYAN_COUNTIES

# Coordinates: Valid lat/lon
assert -90 <= latitude <= 90
assert -180 <= longitude <= 180
```

---

## Entity Relationships

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ _id (PK)        │───┐
│ username        │   │
│ email           │   │
│ role            │   │
└─────────────────┘   │
                      │ 1
                      │
                      │ N
                      ├──────────────────────────────┐
                      │                              │
                      │                              │
                ┌─────▼──────────┐          ┌────────▼────────┐
                │     Files      │          │  Conversations  │
                ├────────────────┤          ├─────────────────┤
                │ _id (PK)       │          │ _id (PK)        │
                │ uploaded_by(FK)│          │ user_id (FK)    │
                │ filename       │          │ messages[]      │
                └────────────────┘          └─────────────────┘


┌─────────────────┐
│     Cases       │
├─────────────────┤
│ _id (PK)        │
│ case_id (UK)    │
│ county          │
│ abuse_type      │
│ severity        │
│ status          │
└─────────────────┘
```

**Relationships**:
1. **Users → Files**: One-to-Many (One user uploads many files)
2. **Users → Conversations**: One-to-Many (One user has many conversations)
3. **Cases**: Independent (no direct foreign keys)

---

## Next Steps

- [Cases API](../api/cases.md) - API endpoints for case management
- [Analytics API](../api/analytics.md) - Statistical queries
- [Project Structure](../development/structure.md) - Code organization
- [RBAC Guide](../features/rbac.md) - Role-based access control
