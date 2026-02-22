# Docker Deployment

Complete guide for deploying using Docker and Docker Compose.

## Quick Start

```bash
# Clone repository
git clone https://github.com/itraki/SaveTheChildren_Backend.git
cd SaveTheChildren_Backend

# Copy environment file
cp .env.example .env

# Edit configuration
nano .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Docker Compose Services

The `docker-compose.yml` includes:

- **FastAPI Backend** - Python application
- **MongoDB** - Case data storage
- **PostgreSQL + pgvector** - Vector embeddings
- **Redis** - Caching layer
- **Nginx** - Reverse proxy (production)

## Configuration

Edit `.env` file:

```env
# Database
MONGODB_URI=mongodb://mongodb:27017
POSTGRES_URI=postgresql://user:pass@postgres:5432/db

# Security
JWT_SECRET_KEY=your-secret-key-here

# AI Services
GROQ_API_KEY=your-groq-key
GOOGLE_API_KEY=your-google-key
```

## Production Deployment

Use the production compose file:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Next Steps

- [Production Deployment](production.md)
- [Configuration](../getting-started/configuration.md)
