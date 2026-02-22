# Troubleshooting Guide

Common issues and solutions.

## Database Connection Issues

**Problem**: Cannot connect to MongoDB

**Solution**:
```bash
# Check MongoDB is running
docker-compose ps

# Check connection string
echo $MONGODB_URI

# View logs
docker-compose logs mongodb
```

## Authentication Errors

**Problem**: 401 Unauthorized errors

**Solution**:
- Check token expiration
- Verify Authorization header format
- Ensure JWT secret matches

## Performance Issues

**Problem**: Slow API responses

**Solution**:
- Enable Redis caching
- Check database indexes
- Review query performance
- Increase worker count

## API Key Issues

**Problem**: AI features not working

**Solution**:
- Verify API keys in `.env`
- Check quota limits
- Test API key validity

## Port Conflicts

**Problem**: Port already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Change port in docker-compose.yml
```

## Next Steps

- [FAQ](faq.md)
- [Configuration](../getting-started/configuration.md)
