# Project Structure

Understanding the codebase organization and architecture.

## Directory Structure

```
SaveTheChildren_Backend/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── api/                    # API layer
│   │   └── v1/                 # API version 1
│   │       ├── endpoints/      # Route handlers
│   │       │   ├── auth.py     # Authentication endpoints
│   │       │   ├── cases.py    # Case management
│   │       │   ├── analytics.py # Analytics endpoints
│   │       │   ├── chatbot.py  # AI chatbot
│   │       │   └── files.py    # File upload
│   │       └── router.py       # Route aggregation
│   ├── core/                   # Core functionality
│   │   ├── security.py         # JWT & password handling
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging.py          # Logging configuration
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── db/                     # Database layer
│   │   ├── client.py           # MongoDB connection
│   │   ├── postgres.py         # PostgreSQL connection
│   │   ├── redis.py            # Redis connection
│   │   └── models.py           # Database models
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py             # Auth request/response
│   │   ├── case.py             # Case schemas
│   │   ├── user.py             # User schemas
│   │   └── analytics.py        # Analytics schemas
│   ├── services/               # Business logic
│   │   ├── auth_service.py     # Authentication service
│   │   ├── case_service.py     # Case management
│   │   ├── analytics_service.py # Analytics
│   │   ├── chatbot_service.py  # AI chatbot
│   │   └── cache_service.py    # Caching
│   ├── integrations/           # External integrations
│   │   ├── kenya_api.py        # Kenya API client
│   │   ├── overpass.py         # Overpass API
│   │   └── embeddings.py       # Embedding providers
│   ├── utils/                  # Utility functions
│   │   ├── validators.py       # Input validation
│   │   ├── formatters.py       # Data formatting
│   │   └── helpers.py          # Helper functions
│   ├── tasks/                  # Background tasks
│   │   ├── geocoding.py        # Geocoding tasks
│   │   └── data_sync.py        # Data synchronization
│   └── config.py               # Configuration
├── docs/                       # MkDocs documentation
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Pytest configuration
├── logs/                       # Application logs
├── uploads/                    # Uploaded files
├── data/                       # Data files
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose config
├── .env.example                # Environment template
├── mkdocs.yml                  # Documentation config
└── README.md                   # Project README
```

## Core Components

### Application Entry Point (`main.py`)

```python
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.logging import setup_logging

app = FastAPI(title="Save The Children API")
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    # Initialize connections
    await setup_databases()

@app.on_event("shutdown")
async def shutdown():
    # Cleanup connections
    await cleanup()
```

### Configuration (`app/config.py`)

Uses Pydantic Settings for type-safe configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DB_URI: str
    DB_NAME: str
    
    # JWT
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### API Layer (`app/api/v1/`)

RESTful endpoints organized by resource:

- **`endpoints/auth.py`** - User registration, login, token management
- **`endpoints/cases.py`** - CRUD operations for cases
- **`endpoints/analytics.py`** - Statistical queries and aggregations
- **`endpoints/chatbot.py`** - AI chat interface
- **`router.py`** - Combines all endpoint routers

### Database Layer (`app/db/`)

Manages database connections and models:

- **`client.py`** - MongoDB async connection pool
- **`postgres.py`** - PostgreSQL with pgvector
- **`redis.py`** - Redis caching layer
- **`models.py`** - Pydantic models for documents

### Services Layer (`app/services/`)

Business logic and data operations:

```python
# app/services/case_service.py
class CaseService:
    async def create_case(self, case_data: CaseCreate) -> Case:
        # Validation
        # Data enrichment (geocoding)
        # Database insertion
        # Cache invalidation
        pass
```

### Schemas (`app/schemas/`)

Pydantic models for request/response validation:

```python
# app/schemas/case.py
class CaseCreate(BaseModel):
    case_id: str
    location: str
    severity: str
    
class CaseResponse(BaseModel):
    id: str
    case_id: str
    created_at: datetime
```

## Architecture Patterns

### Layered Architecture

```
┌─────────────────────────────────────┐
│     API Layer (FastAPI Routes)      │ ← HTTP Requests
├─────────────────────────────────────┤
│     Service Layer (Business Logic)  │ ← Orchestration
├─────────────────────────────────────┤
│     Database Layer (Data Access)    │ ← Persistence
└─────────────────────────────────────┘
```

### Dependency Injection

Using FastAPI's dependency injection:

```python
from fastapi import Depends
from app.core.security import get_current_user

@router.get("/cases")
async def get_cases(
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    return await CaseService(db).get_cases(user)
```

### Async/Await Pattern

All I/O operations use async:

```python
async def get_case(case_id: str):
    case = await db.cases.find_one({"case_id": case_id})
    return case
```

## Key Files

### `main.py`

Application initialization and lifecycle management.

### `app/config.py`

Centralized configuration using Pydantic Settings.

### `app/api/v1/router.py`

Aggregates all API routes:

```python
from app.api.v1.endpoints import auth, cases, analytics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
```

### `app/core/security.py`

Authentication and authorization:

- JWT token creation/validation
- Password hashing
- User permission checks

### `app/db/client.py`

Database connection management:

```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(settings.DB_URI)
db = client[settings.DB_NAME]
```

## Design Principles

### 1. Separation of Concerns

Each layer has a specific responsibility:
- **API**: HTTP request/response handling
- **Services**: Business logic
- **Database**: Data persistence

### 2. Single Responsibility

Each module focuses on one thing:
- `auth.py` - Authentication only
- `cases.py` - Case management only

### 3. Dependency Inversion

High-level modules don't depend on low-level modules:

```python
# Service depends on abstract database interface
class CaseService:
    def __init__(self, db: Database):
        self.db = db
```

### 4. DRY (Don't Repeat Yourself)

Common functionality in utilities:
- `validators.py` - Reusable validation
- `formatters.py` - Data formatting

## Testing Structure

```
tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_case_service.py
│   └── test_validators.py
├── integration/
│   ├── test_auth_endpoints.py
│   ├── test_case_endpoints.py
│   └── test_database.py
└── conftest.py  # Pytest fixtures
```

## Configuration Files

### `docker-compose.yml`

Local development environment:

```yaml
services:
  fastapi_app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
      - postgres
```

### `Dockerfile`

Multi-stage build for optimization:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### `.env.example`

Configuration template (committed to git).

### `.gitignore`

Excludes sensitive and generated files:

```
.env
__pycache__/
*.pyc
venv/
.pytest_cache/
```

## Code Style

### Formatting

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting

Run formatters:

```bash
black app/
isort app/
flake8 app/
```

### Type Hints

All functions use type hints:

```python
async def get_case(case_id: str) -> Optional[Case]:
    pass
```

### Docstrings

Google-style docstrings:

```python
def calculate_statistics(cases: List[Case]) -> Dict[str, Any]:
    """Calculate case statistics.
    
    Args:
        cases: List of case objects
        
    Returns:
        Dictionary with statistical metrics
        
    Raises:
        ValueError: If cases list is empty
    """
    pass
```

## Next Steps

- [Code Reference](code-reference.md) - Detailed API documentation
- [Testing](testing.md) - Testing guide
- [Contributing](contributing.md) - Contribution guidelines
