# Save The Children - FastAPI Backend

Welcome to the comprehensive documentation for the **Save The Children Child Protection Dashboard Backend**.

## Overview

A production-ready FastAPI backend designed for managing child protection cases with advanced features including AI-powered chatbot, real-time analytics, and geospatial capabilities.

## Key Features

### 🚀 Core Technology
- **FastAPI** - Modern async Python web framework
- **MongoDB** - NoSQL database with async motor driver
- **PostgreSQL + pgvector** - Local vector database for RAG/embeddings
- **Redis** - Caching layer for performance optimization

### 🔐 Security & Authentication
- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **RBAC** - Role-based access control (Admin, Member, Viewer)
- **Password Encryption** - Bcrypt hashing for secure password storage

### 🤖 AI & Intelligence
- **AI Chatbot** - LangChain + Groq LLM with RAG capabilities
- **Multi-Provider Embeddings** - Google AI, OpenAI, or local sentence-transformers
- **Document Processing** - PDF, DOCX upload with semantic search
- **Real-time Streaming** - Server-Sent Events (SSE) for chat responses

### 📊 Analytics & Data
- **Advanced Analytics** - Case statistics, trends, and demographics
- **Geospatial Support** - Location-based queries and mapping
- **Data Aggregation** - MongoDB aggregation pipelines with caching
- **Performance Optimization** - Indexed queries and Redis caching

### 🌍 Regional Integration
- **Kenya API Integration** - Direct connection to Kenya's case management system
- **Geocoding** - Automatic location enrichment
- **Overpass API** - Points of interest and facility mapping

## Quick Links

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } **Quick Start**

    ---

    Get up and running in minutes with Docker Compose

    [:octicons-arrow-right-24: Getting Started](getting-started/quickstart.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API documentation with examples

    [:octicons-arrow-right-24: API Docs](api/overview.md)

-   :material-docker:{ .lg .middle } **Deployment**

    ---

    Production deployment guides for Docker and VPS

    [:octicons-arrow-right-24: Deploy](deployment/docker.md)

-   :material-code-braces:{ .lg .middle } **Development**

    ---

    Project structure and development guidelines

    [:octicons-arrow-right-24: Dev Guide](development/structure.md)

</div>

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/SSE
┌───────────────────────────▼─────────────────────────────────┐
│                    FastAPI Backend (Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth & RBAC  │  │  Case Mgmt   │  │  AI Chatbot  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────┬──────────────┬──────────────────┬─────────────────┘
          │              │                  │
    ┌─────▼─────┐  ┌────▼─────┐     ┌─────▼──────┐
    │  MongoDB  │  │PostgreSQL│     │   Redis    │
    │  (Cases)  │  │(Vectors) │     │ (Cache)    │
    └───────────┘  └──────────┘     └────────────┘
```

## System Requirements

- **Python**: 3.12 or higher
- **MongoDB**: 4.4+ (for case data storage)
- **PostgreSQL**: 16+ with pgvector extension (for embeddings)
- **Redis**: 6.0+ (optional, for caching)
- **Docker**: 20.10+ and Docker Compose 2.0+ (recommended)

## Project Status

✅ **Production Ready** - All core features implemented and tested

- Authentication & Authorization ✓
- Case Management CRUD ✓
- Analytics Dashboard ✓
- AI Chatbot with RAG ✓
- File Upload & Processing ✓
- Geospatial Features ✓
- Performance Optimization ✓
- Docker Deployment ✓

## Support & Contributing

For issues, questions, or contributions:

- 📧 Contact the development team
- 🐛 [Report Issues](https://github.com/yourusername/SaveTheChildren_Backend/issues)
- 📖 Read the [Contributing Guidelines](development/contributing.md)

## License

MIT License - See [LICENSE](https://github.com/yourusername/SaveTheChildren_Backend/blob/main/LICENSE) file for details.
