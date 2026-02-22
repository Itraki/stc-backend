# Production Deployment

Guide for deploying to production environments.

## Prerequisites

- VPS with Ubuntu 22.04+
- Domain name configured
- SSL certificate (Let's Encrypt recommended)

## Deployment Steps

1. **Server Setup**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

2. **Clone and Configure**

```bash
git clone https://github.com/itraki/SaveTheChildren_Backend.git
cd SaveTheChildren_Backend
cp .env.example .env
nano .env  # Configure production values
```

3. **Deploy**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## SSL/TLS Configuration

Use Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Monitoring

Check service health:

```bash
docker-compose ps
docker-compose logs -f backend
```

## Backups

Regular MongoDB backups:

```bash
docker-compose exec mongodb mongodump --out /backup
```

## Next Steps

- [Docker Deployment](docker.md)
- [Security Guide](../guides/security.md)
