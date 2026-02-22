# Authentication API

Complete reference for authentication and user management endpoints.

## Overview

The authentication system uses **JWT (JSON Web Tokens)** with access and refresh token pairs for secure, stateless authentication.

**Base Path**: `/api/v1/auth`

## Token Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    
    Client->>API: POST /login (credentials)
    API->>Database: Validate user
    Database-->>API: User data
    API-->>Client: Access + Refresh tokens
    
    Client->>API: GET /cases (with access token)
    API-->>Client: Protected data
    
    Note over Client,API: Access token expires
    
    Client->>API: POST /refresh (refresh token)
    API-->>Client: New access token
```

## Endpoints

### Register User

Create a new user account.

**Endpoint**: `POST /api/v1/auth/register`

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "role": "MEMBER"
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email address (unique) |
| `password` | string | Yes | Min 8 chars, 1 uppercase, 1 number |
| `full_name` | string | Yes | User's full name |
| `role` | string | No | Role: ADMIN, MEMBER, or VIEWER (default: VIEWER) |

**Response** (201 Created):

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "MEMBER",
  "created_at": "2026-02-22T14:20:00Z",
  "is_active": true
}
```

**Errors**:

- `400 Bad Request` - Email already exists
- `422 Unprocessable Entity` - Validation error

**Example**:

=== "cURL"
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/register" \
      -H "Content-Type: application/json" \
      -d '{
        "email": "john@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe",
        "role": "MEMBER"
      }'
    ```

=== "Python"
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json={
            "email": "john@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe",
            "role": "MEMBER"
        }
    )
    user = response.json()
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch("http://localhost:8000/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "john@example.com",
        password: "SecurePass123!",
        full_name: "John Doe",
        role: "MEMBER"
      })
    });
    const user = await response.json();
    ```

---

### Login

Authenticate and receive access tokens.

**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "MEMBER"
  }
}
```

**Token Details**:

- **Access Token**: Valid for 15 minutes (default)
- **Refresh Token**: Valid for 7 days (default)
- Use access token for API requests
- Use refresh token to get new access token

**Errors**:

- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account disabled

**Example**:

```bash
# Login and save token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}' \
  | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/cases"
```

---

### Get Current User

Get the currently authenticated user's profile.

**Endpoint**: `GET /api/v1/auth/me`

**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "MEMBER",
  "created_at": "2026-01-15T10:30:00Z",
  "is_active": true
}
```

**Example**:

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### Refresh Token

Get a new access token using refresh token.

**Endpoint**: `POST /api/v1/auth/refresh`

**Request Body**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Errors**:

- `401 Unauthorized` - Invalid or expired refresh token

**Example**:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"'$REFRESH_TOKEN'"}'
```

---

### Logout

Invalidate refresh token (logout).

**Endpoint**: `POST /api/v1/auth/logout`

**Authentication**: Required

**Request Body**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):

```json
{
  "message": "Successfully logged out"
}
```

---

### Change Password

Change the authenticated user's password.

**Endpoint**: `POST /api/v1/auth/change-password`

**Authentication**: Required

**Request Body**:

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePass456!"
}
```

**Response** (200 OK):

```json
{
  "message": "Password changed successfully"
}
```

**Errors**:

- `400 Bad Request` - Current password incorrect
- `422 Unprocessable Entity` - New password doesn't meet requirements

## Authentication Headers

Include the access token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Token Storage

### Frontend Best Practices

**Recommended**: HttpOnly Cookies (most secure)

```javascript
// Server sets cookie
Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict

// Browser automatically sends with requests
```

**Alternative**: Secure localStorage

```javascript
// Store tokens
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);

// Retrieve and use
const token = localStorage.getItem('access_token');
fetch(url, {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

!!! warning "Security"
    - Never store tokens in plain cookies (use HttpOnly)
    - Clear tokens on logout
    - Implement token refresh before expiration

## Role-Based Access Control (RBAC)

### Roles

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full access to all resources and admin functions |
| **MEMBER** | Create/read/update cases, access analytics |
| **VIEWER** | Read-only access to public data |

### Permission Examples

```python
# Admin only
@router.delete("/cases/{case_id}")
async def delete_case(
    case_id: str,
    user: User = Depends(require_role("ADMIN"))
):
    pass

# Member or Admin
@router.post("/cases")
async def create_case(
    case: CaseCreate,
    user: User = Depends(require_role(["MEMBER", "ADMIN"]))
):
    pass
```

## Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (recommended)

## Security Features

- [x] **Bcrypt hashing** - Passwords never stored in plain text
- [x] **JWT tokens** - Stateless authentication
- [x] **Token expiration** - Automatic timeout
- [x] **Refresh tokens** - Long-lived sessions
- [x] **Role-based access** - Permission control
- [x] **Account lockout** - Brute force protection (optional)

## Error Responses

All authentication errors follow this format:

```json
{
  "detail": "Invalid credentials",
  "status_code": 401
}
```

Common error codes:

- `400` - Bad request (email exists, weak password)
- `401` - Unauthorized (invalid credentials, expired token)
- `403` - Forbidden (insufficient permissions, disabled account)
- `422` - Validation error (missing fields, invalid format)

## Best Practices

1. **Use HTTPS** in production
2. **Implement token refresh** before expiration
3. **Store tokens securely** (HttpOnly cookies or secure storage)
4. **Handle 401 errors** by redirecting to login
5. **Implement logout** by clearing tokens
6. **Use strong passwords** and enforce requirements
7. **Rate limit** login attempts

## Next Steps

- [Cases API](cases.md) - Manage cases
- [Analytics API](analytics.md) - View statistics
- [RBAC Guide](../features/rbac.md) - Role-based access control
- [Security Guide](../guides/security.md) - Security best practices
