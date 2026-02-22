# Frequently Asked Questions

Common questions and answers.

## General

**Q: What databases are required?**

A: MongoDB for case data, PostgreSQL with pgvector for embeddings, and optionally Redis for caching.

**Q: Can I use this without AI features?**

A: Yes, AI features are optional. The core case management works independently.

**Q: What Python version is required?**

A: Python 3.12 or higher is recommended.

## Deployment

**Q: Can I deploy on shared hosting?**

A: No, you need a VPS or cloud instance with Docker support.

**Q: How much does deployment cost?**

A: Minimum $5-10/month for a basic VPS. API keys (Groq, Google) may have costs.

**Q: Is HTTPS required?**

A: Yes, for production. Development can use HTTP.

## Features

**Q: How do I add new users?**

A: Use the `/api/v1/auth/register` endpoint or admin panel.

**Q: Can I import existing case data?**

A: Yes, use the data loading scripts or import via API.

**Q: How do I backup data?**

A: Use `mongodump` for MongoDB and `pg_dump` for PostgreSQL.

## Troubleshooting

**Q: Why is the chatbot not working?**

A: Check your GROQ_API_KEY and GOOGLE_API_KEY in `.env`.

**Q: How do I reset the admin password?**

A: Use the MongoDB shell or password reset endpoint.

## Next Steps

- [Troubleshooting](troubleshooting.md)
- [Getting Started](../getting-started/quickstart.md)
