# Installation Guide

Detailed installation instructions for all deployment scenarios.

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB
- **OS**: Linux, macOS, or Windows

### Recommended for Production

- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **OS**: Ubuntu 22.04 LTS or newer

## Software Dependencies

### Required

- **Python**: 3.12 or higher
- **MongoDB**: 4.4+ or MongoDB Atlas
- **PostgreSQL**: 16+ with pgvector extension
- **Docker**: 20.10+ (recommended)
- **Docker Compose**: 2.0+

### Optional

- **Redis**: 6.0+ (for caching)
- **Nginx**: 1.18+ (for reverse proxy)
- **Git**: For version control

## Installation Methods

Choose the method that best fits your needs:

1. **[Docker Compose](#docker-compose-recommended)** - Fastest, includes all services
2. **[Manual Installation](#manual-installation)** - More control, local development
3. **[Production Setup](#production-deployment)** - VPS deployment

## Docker Compose (Recommended)

### 1. Install Docker

=== "Ubuntu/Debian"
    ```bash
    # Update package index
    sudo apt update
    
    # Install Docker
    sudo apt install -y docker.io docker-compose
    
    # Start Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add your user to docker group (optional)
    sudo usermod -aG docker $USER
    newgrp docker
    ```

=== "macOS"
    ```bash
    # Install via Homebrew
    brew install --cask docker
    
    # Or download from:
    # https://www.docker.com/products/docker-desktop/
    ```

=== "Windows"
    Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/SaveTheChildren_Backend.git
cd SaveTheChildren_Backend
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your values
```

Minimum configuration:

```env
JWT_SECRET_KEY=$(openssl rand -hex 32)
GROQ_API_KEY=your_groq_api_key
DB_URI=mongodb://mongodb:27017
DB_NAME=stc-db
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Access documentation
open http://localhost:8000/docs
```

## Manual Installation

For local development without Docker.

### 1. Install Python 3.12

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3-pip
    ```

=== "macOS"
    ```bash
    brew install python@3.12
    ```

=== "Windows"
    Download from [python.org](https://www.python.org/downloads/)

### 2. Install MongoDB

=== "Ubuntu/Debian"
    ```bash
    # Import MongoDB public GPG key
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
       sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
    
    # Add MongoDB repository
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
       sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    # Install MongoDB
    sudo apt update
    sudo apt install -y mongodb-org
    
    # Start MongoDB
    sudo systemctl start mongod
    sudo systemctl enable mongod
    ```

=== "macOS"
    ```bash
    brew tap mongodb/brew
    brew install mongodb-community@7.0
    brew services start mongodb-community@7.0
    ```

=== "Docker"
    ```bash
    docker run -d -p 27017:27017 --name mongodb mongo:latest
    ```

### 3. Install PostgreSQL with pgvector

=== "Ubuntu/Debian"
    ```bash
    # Install PostgreSQL 16
    sudo apt install -y postgresql-16 postgresql-client-16
    
    # Install build dependencies for pgvector
    sudo apt install -y postgresql-server-dev-16 build-essential git
    
    # Install pgvector
    cd /tmp
    git clone https://github.com/pgvector/pgvector.git
    cd pgvector
    make
    sudo make install
    
    # Start PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql <<EOF
    CREATE USER stc_user WITH PASSWORD 'stc_password';
    CREATE DATABASE stc_vectors OWNER stc_user;
    \c stc_vectors
    CREATE EXTENSION vector;
    GRANT ALL PRIVILEGES ON DATABASE stc_vectors TO stc_user;
    EOF
    ```

=== "macOS"
    ```bash
    brew install postgresql@16
    brew services start postgresql@16
    
    # Install pgvector
    cd /tmp
    git clone https://github.com/pgvector/pgvector.git
    cd pgvector
    make
    make install
    
    # Create database
    createdb stc_vectors
    psql stc_vectors -c "CREATE EXTENSION vector;"
    ```

=== "Docker"
    ```bash
    docker run -d \
      -p 5432:5432 \
      -e POSTGRES_USER=stc_user \
      -e POSTGRES_PASSWORD=stc_password \
      -e POSTGRES_DB=stc_vectors \
      --name postgres \
      ankane/pgvector
    ```

### 4. Install Redis (Optional)

=== "Ubuntu/Debian"
    ```bash
    sudo apt install -y redis-server
    sudo systemctl start redis
    sudo systemctl enable redis
    ```

=== "macOS"
    ```bash
    brew install redis
    brew services start redis
    ```

=== "Docker"
    ```bash
    docker run -d -p 6379:6379 --name redis redis:latest
    ```

### 5. Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/yourusername/SaveTheChildren_Backend.git
cd SaveTheChildren_Backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

### 6. Initialize Database

```bash
# Initialize PostgreSQL vector database
python init_postgres_vectors.py

# (Optional) Load sample data
python load_data.py
```

### 7. Run Application

```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or with Gunicorn (production)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Production Deployment

### VPS Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.12 python3.12-venv python3-pip nginx certbot python3-certbot-nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clone repository
cd /opt
sudo git clone https://github.com/yourusername/SaveTheChildren_Backend.git
sudo chown -R $USER:$USER SaveTheChildren_Backend
cd SaveTheChildren_Backend

# Configure environment
cp .env.example .env
nano .env  # Set production values

# Start with Docker
docker-compose -f docker-compose.prod.yml up -d

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/api
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d api.yoursite.com
```

## Verification

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-22T14:20:00.000Z",
  "version": "1.0.0"
}
```

### Database Connections

```bash
# Test MongoDB
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('MongoDB OK')"

# Test PostgreSQL
python -c "import psycopg2; conn = psycopg2.connect('postgresql://stc_user:stc_password@localhost/stc_vectors'); print('PostgreSQL OK')"

# Test Redis
python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping() and print('Redis OK')"
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Database Connection Failed

```bash
# Check MongoDB status
sudo systemctl status mongod

# Check PostgreSQL status
sudo systemctl status postgresql

# View logs
sudo journalctl -u mongod -f
sudo journalctl -u postgresql -f
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

- [Configuration Guide](configuration.md) - Configure your installation
- [Quick Start](quickstart.md) - Get started quickly
- [Data Loading](../data/loading.md) - Load initial data
- [Production Deployment](../deployment/production.md) - Deploy to production

## Getting Help

- Check [Troubleshooting Guide](../guides/troubleshooting.md)
- Review [FAQ](../guides/faq.md)
- Contact support team
