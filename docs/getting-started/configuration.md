# Configuration Guide

Complete guide to configuring the Save The Children Backend.

## Environment Variables

All configuration is done through environment variables in the `.env` file.

### Creating Configuration File

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

## Core Settings

### Application Settings

```env
# Environment: development, staging, production
ENVIRONMENT=production

# Enable debug mode (never in production!)
DEBUG=false

# API Base URL
API_BASE_URL=http://localhost:8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com
```

## Database Configuration

### MongoDB

```env
# MongoDB connection string
DB_URI=mongodb://localhost:27017

# Database name
DB_NAME=stc-db

# For MongoDB Atlas (cloud):
# DB_URI=mongodb+srv://username:password@cluster.mongodb.net
```

!!! tip "MongoDB Atlas"
    For production, use MongoDB Atlas for managed database hosting with automatic backups.

### PostgreSQL (Vector Database)

```env
# PostgreSQL connection for pgvector
POSTGRES_URI=postgresql+asyncpg://stc_user:stc_password@localhost:5432/stc_vectors

# Individual components (alternative)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=stc_vectors
POSTGRES_USER=stc_user
POSTGRES_PASSWORD=stc_password
```

### Redis (Caching)

```env
# Redis connection
REDIS_URI=redis://localhost:6379/0

# Cache TTL (seconds)
CACHE_TTL=3600  # 1 hour
```

## Authentication & Security

### JWT Configuration

```env
# JWT Secret Key (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-super-secret-random-key-here-minimum-32-characters

# Algorithm
JWT_ALGORITHM=HS256

# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

!!! danger "Security Warning"
    Never commit your `JWT_SECRET_KEY` to version control. Generate a new one for each environment.

**Generate a secure key:**

```bash
# Using OpenSSL
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Password Security

```env
# Bcrypt rounds (higher = more secure but slower)
BCRYPT_ROUNDS=12
```

## AI & LLM Configuration

### Groq API (Chat)

```env
# Get free API key from https://console.groq.com
GROQ_API_KEY=gsk_your_groq_api_key_here

# Model selection
GROQ_MODEL=llama-3.3-70b-versatile
```

!!! info "Free Tier"
    Groq offers 7,000 free requests per day - perfect for development and small deployments.

### Embedding Provider

```env
# Options: auto, local, google, openai
EMBEDDING_PROVIDER=auto

# Google AI (1,500 free requests/day)
GOOGLE_API_KEY=your_google_api_key

# OpenAI (paid)
OPENAI_API_KEY=sk-your_openai_api_key
```

**Embedding Provider Options:**

| Provider | Cost | Speed | Quality | Offline |
|----------|------|-------|---------|---------|
| `local` | Free | Medium | Good | ✅ Yes |
| `google` | Free tier | Fast | Excellent | ❌ No |
| `openai` | Paid | Fast | Excellent | ❌ No |
| `auto` | Mixed | Variable | Good | Partial |

## Regional APIs

### Kenya API Integration

```env
# Kenya case management API
KENYA_API_BASE_URL=https://api.kenya.example.com
KENYA_API_KEY=your_kenya_api_key

# Enable/disable
ENABLE_KENYA_API=true
```

### Geocoding

```env
# Overpass API for geospatial data
OVERPASS_API_URL=https://overpass-api.de/api/interpreter

# Alternative mirrors (comma-separated)
OVERPASS_MIRRORS=https://overpass.kumi.systems/api/interpreter
```

## File Upload Configuration

```env
# Upload directory
UPLOAD_DIR=./uploads

# Max file size (bytes)
MAX_UPLOAD_SIZE=10485760  # 10MB

# Allowed file types
ALLOWED_FILE_TYPES=pdf,docx,txt
```

## Logging

```env
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file path
LOG_FILE=logs/app.log

# Log format
LOG_FORMAT=json  # or: text
```

## Performance Tuning

### Connection Pools

```env
# MongoDB connection pool
MONGO_MIN_POOL_SIZE=10
MONGO_MAX_POOL_SIZE=100

# PostgreSQL connection pool
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=10
```

### Caching

```env
# Enable query caching
ENABLE_CACHING=true

# Cache backend: redis, memory
CACHE_BACKEND=redis

# Default cache TTL (seconds)
DEFAULT_CACHE_TTL=3600
```

## Docker-Specific Configuration

### docker-compose.yml

```yaml
environment:
  - DB_URI=mongodb://mongodb:27017
  - POSTGRES_URI=postgresql+asyncpg://stc_user:stc_password@postgres:5432/stc_vectors
  - REDIS_URI=redis://redis:6379/0
```

!!! note
    When using Docker Compose, use service names (`mongodb`, `postgres`, `redis`) instead of `localhost`.

## Environment-Specific Configs

### Development

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000
```

### Staging

```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yoursite.com
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yoursite.com
ENABLE_CACHING=true
```

## Configuration Validation

The application validates configuration on startup:

```bash
# Check configuration
python -c "from app.config import settings; print(settings)"
```

## Configuration Priority

Environment variables are loaded in this order:

1. System environment variables
2. `.env` file
3. Default values in `app/config.py`

## Security Best Practices

### ✅ Do's

- ✅ Use environment variables for secrets
- ✅ Generate strong random keys
- ✅ Use different secrets per environment
- ✅ Enable HTTPS in production
- ✅ Restrict CORS origins
- ✅ Use managed database services

### ❌ Don'ts

- ❌ Commit `.env` files to git
- ❌ Use default or weak secrets
- ❌ Share secrets between environments
- ❌ Enable DEBUG in production
- ❌ Allow all CORS origins (`*`)

## Example Configurations

### Minimal (Development)

```env
JWT_SECRET_KEY=dev-secret-key-change-in-production
DB_URI=mongodb://localhost:27017
DB_NAME=stc-db
GROQ_API_KEY=gsk_your_key_here
```

### Full (Production)

```env
# Application
ENVIRONMENT=production
DEBUG=false
API_BASE_URL=https://api.yoursite.com
CORS_ORIGINS=https://yoursite.com

# Databases
DB_URI=mongodb+srv://user:pass@cluster.mongodb.net
DB_NAME=stc-prod
POSTGRES_URI=postgresql+asyncpg://user:pass@postgres.yoursite.com/vectors
REDIS_URI=redis://redis.yoursite.com:6379/0

# Security
JWT_SECRET_KEY=<64-character-random-string>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM & AI
GROQ_API_KEY=gsk_production_key
GOOGLE_API_KEY=your_google_key
EMBEDDING_PROVIDER=google

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json
```

## Configuration Files

### .env.example

Template file with all available options (committed to git).

### .env

Your actual configuration (never committed to git).

### .gitignore

Ensure `.env` is ignored:

```gitignore
.env
.env.local
.env.*.local
```

## Troubleshooting

### Missing Environment Variables

If you see errors about missing variables:

```bash
# Check what's loaded
python -c "from app.config import settings; print(settings.model_dump())"
```

### Database Connection Failed

```bash
# Test MongoDB connection
mongosh "$DB_URI"

# Test PostgreSQL connection
psql "$POSTGRES_URI"
```

### Invalid JWT Secret

Regenerate with:

```bash
openssl rand -hex 32
```

## Next Steps

- [Installation Guide](installation.md)
- [Quick Start](quickstart.md)
- [Security Guide](../guides/security.md)
- [Production Deployment](../deployment/production.md)
