# Role-Based Access Control (RBAC)

Complete guide to the RBAC system.

## Overview

The system implements three roles with different permission levels:

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full access to all resources |
| **MEMBER** | Create, read, update cases and analytics |
| **VIEWER** | Read-only access |

## Role Hierarchy

```
ADMIN
  ├─ Full system access
  ├─ User management
  ├─ Delete cases
  └─ System configuration

MEMBER
  ├─ Create cases
  ├─ Update cases
  ├─ View analytics
  └─ Use chatbot

VIEWER
  ├─ View cases (limited)
  └─ View public analytics
```

## Usage in Code

```python
from app.auth.dependencies import require_role

@router.delete("/cases/{case_id}")
async def delete_case(
    case_id: str,
    user: User = Depends(require_role("ADMIN"))
):
    # Only admins can delete
    pass

@router.post("/cases")
async def create_case(
    case: CaseCreate,
    user: User = Depends(require_role(["MEMBER", "ADMIN"]))
):
    # Members and admins can create
    pass
```

## Setting User Roles

### During Registration

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "MEMBER"
}
```

### Updating Roles (Admin Only)

```bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/{user_id}/role" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"role": "ADMIN"}'
```

## Next Steps

- [Authentication API](../api/authentication.md)
- [Security Guide](../guides/security.md)
