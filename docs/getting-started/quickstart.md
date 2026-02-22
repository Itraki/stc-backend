# Quick Start Guide

Get the Save The Children Backend up and running in minutes!

## Prerequisites

Before you begin, ensure you have:

- [x] Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop/))
- [x] Docker Compose (included with Docker Desktop)
- [x] Git
- [x] 4GB+ RAM available

!!! tip "Optional but Recommended"
    - Python 3.12+ for local development
    - A code editor (VS Code, PyCharm, etc.)

## 🚀 Quick Start with Docker (Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SaveTheChildren_Backend.git
cd SaveTheChildren_Backend
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

**Minimum required variables:**

```env
# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-super-secret-key-here

# Database
DB_URI=mongodb://mongodb:27017
DB_NAME=stc-db

# LLM API (get free key from https://console.groq.com)
GROQ_API_KEY=your-groq-api-key-here
```

### 3. Start All Services

```bash
# Start MongoDB, PostgreSQL, Redis, and FastAPI
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME                    STATUS              PORTS
fastapi_app             running             0.0.0.0:8000->8000/tcp
mongodb                 running             0.0.0.0:27017->27017/tcp
postgres                running             0.0.0.0:5432->5432/tcp
redis                   running             0.0.0.0:6379->6379/tcp
```

### 4. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-22T14:20:00.000Z"
}
```

### 5. Create Your First User

Using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "full_name": "Admin User",
    "role": "ADMIN"
  }'
```

Or visit the interactive docs at `http://localhost:8000/docs`

## 🎉 You're Done!

Your backend is now running and ready to use!

### What's Next?

- 📖 [Explore the API](../api/overview.md)
- 🔐 [Configure Authentication](../api/authentication.md)
- 📊 [Load Sample Data](../data/loading.md)
- 🤖 [Set up the AI Chatbot](../api/chatbot.md)

## 📱 Useful Commands

```bash
# View logs
docker-compose logs -f fastapi_app

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Update to latest code
git pull && docker-compose up -d --build
```

## 🐛 Common Issues

### Port Already in Use

If port 8000 is already in use:

```bash
# Edit docker-compose.yml and change the port
ports:
  - "8001:8000"  # Use 8001 instead
```

### Database Connection Failed

```bash
# Check if MongoDB is running
docker-compose ps mongodb

# View MongoDB logs
docker-compose logs mongodb
```

### Slow Startup

First startup may take 2-5 minutes to download images. Subsequent starts are much faster.

## 🔧 Local Development (Without Docker)

For local Python development:

```bash
# Install dependencies
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start MongoDB and PostgreSQL separately
docker-compose up -d mongodb postgres redis

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Additional Resources

- [Installation Guide](installation.md) - Detailed installation instructions
- [Configuration Guide](configuration.md) - All environment variables explained
- [Docker Deployment](../deployment/docker.md) - Advanced Docker setup
- [Troubleshooting](../guides/troubleshooting.md) - Common problems and solutions

## 💡 Tips

!!! success "Performance Tip"
    Enable Redis caching for 10x faster analytics queries. It's already included in `docker-compose.yml`!

!!! info "Free Tier API Keys"
    - **Groq**: 7,000 free requests/day ([Sign up](https://console.groq.com))
    - **Google AI**: 1,500 embeddings/day ([Get API key](https://makersuite.google.com))

!!! warning "Production Deployment"
    For production, see the [Production Deployment Guide](../deployment/production.md) for security best practices.
