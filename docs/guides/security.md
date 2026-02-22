# Security Guide

Security best practices and guidelines.

## Authentication

- Use strong JWT secrets
- Rotate tokens regularly
- Implement token refresh
- Use HTTPS in production

## Password Security

- Enforce strong password requirements
- Use bcrypt for hashing
- Never log passwords
- Implement account lockout

## API Security

- Rate limiting enabled
- CORS properly configured
- Input validation on all endpoints
- SQL injection prevention

## Environment Variables

Never commit sensitive data:

```env
# ❌ Don't commit this file
JWT_SECRET_KEY=secret-key-here
GROQ_API_KEY=api-key-here
```

Use `.env.example` as template.

## HTTPS/TLS

Always use HTTPS in production:

- Get SSL certificate (Let's Encrypt)
- Configure Nginx with TLS
- Redirect HTTP to HTTPS
- Use secure cookies

## Next Steps

- [Configuration](../getting-started/configuration.md)
- [Production Deployment](../deployment/production.md)
