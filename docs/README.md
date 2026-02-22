# MkDocs Documentation

This directory contains the documentation for the Save The Children Backend project, built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## 📚 Documentation Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Getting started guides
│   ├── quickstart.md          # Quick start guide
│   ├── installation.md        # Detailed installation
│   └── configuration.md       # Configuration guide
├── api/                       # API documentation
│   ├── overview.md            # API overview
│   ├── authentication.md      # Auth endpoints
│   ├── cases.md               # Case endpoints
│   ├── analytics.md           # Analytics endpoints
│   ├── chatbot.md             # Chatbot endpoints
│   └── file-upload.md         # File upload endpoints
├── features/                  # Feature documentation
│   ├── rbac.md                # Role-based access control
│   ├── caching.md             # Caching system
│   ├── vector-database.md     # Vector database
│   ├── geospatial.md          # Geospatial features
│   └── sse.md                 # Server-sent events
├── deployment/                # Deployment guides
│   ├── docker.md              # Docker deployment
│   ├── production.md          # Production setup
│   └── self-hosted.md         # Self-hosted deployment
├── data/                      # Data management
│   ├── loading.md             # Data loading
│   ├── migrations.md          # Database migrations
│   └── kenya-api.md           # Kenya API integration
├── development/               # Development docs
│   ├── structure.md           # Project structure
│   ├── code-reference.md      # Code documentation
│   ├── testing.md             # Testing guide
│   └── performance.md         # Performance optimization
└── guides/                    # How-to guides
    ├── security.md            # Security best practices
    ├── monitoring.md          # Monitoring & logging
    └── troubleshooting.md     # Common issues
```

## 🚀 Quick Start

### Prerequisites

Install MkDocs and required plugins:

```bash
# Using pip in virtual environment
pip install -r requirements.txt

# Or install just documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-awesome-pages-plugin
```

### Development Server

Start a local development server with live reload:

```bash
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

The documentation will automatically reload when you save changes to any `.md` file.

### Build Documentation

Build static HTML files:

```bash
mkdocs build
```

Output will be in the `site/` directory.

## 📝 Writing Documentation

### Creating a New Page

1. Create a new Markdown file in the appropriate directory:

```bash
touch docs/guides/new-guide.md
```

2. Add the page to `mkdocs.yml` navigation:

```yaml
nav:
  - Guides:
      - New Guide: guides/new-guide.md
```

3. Write your content using Markdown and Material extensions.

### Markdown Extensions

We support many useful Markdown extensions:

#### Code Blocks with Syntax Highlighting

```python
def hello_world():
    print("Hello, World!")
```

#### Admonitions (Callouts)

```markdown
!!! note "Optional Title"
    This is a note.

!!! warning
    This is a warning.

!!! tip
    This is a tip.

!!! danger
    This is important!
```

#### Tabs

```markdown
=== "Python"
    ```python
    print("Hello")
    ```

=== "JavaScript"
    ```javascript
    console.log("Hello");
    ```
```

#### Code Annotations

```python
def example():  # (1)!
    pass
```

1. This is an annotation

### Auto-Generated API Documentation

Use `mkdocstrings` to auto-generate documentation from docstrings:

```markdown
::: app.services.auth_service.AuthService
    options:
      show_source: true
      members:
        - login
        - register
```

## 🎨 Customization

### Theme Configuration

Edit `mkdocs.yml` to customize:

```yaml
theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - search.suggest
```

### Adding Custom CSS

1. Create `docs/stylesheets/extra.css`
2. Add to `mkdocs.yml`:

```yaml
extra_css:
  - stylesheets/extra.css
```

### Adding Custom JavaScript

1. Create `docs/javascripts/extra.js`
2. Add to `mkdocs.yml`:

```yaml
extra_javascript:
  - javascripts/extra.js
```

## 🚢 Deployment

### GitHub Pages

Deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

This builds the docs and pushes to the `gh-pages` branch.

### Manual Deployment

Build and deploy manually:

```bash
# Build
mkdocs build

# Deploy to your server
rsync -avz site/ user@server:/var/www/docs/
```

### Docker

Build docs in Docker:

```dockerfile
FROM squidfunk/mkdocs-material

WORKDIR /docs
COPY . /docs

EXPOSE 8000
CMD ["serve", "--dev-addr=0.0.0.0:8000"]
```

Run:

```bash
docker build -t docs .
docker run -p 8000:8000 docs
```

## 🔍 Search

Search is enabled by default using the `search` plugin. To customize:

```yaml
plugins:
  - search:
      lang: en
      separator: '[\s\-\.]+'
```

## 📊 Analytics

Add Google Analytics:

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## ✅ Best Practices

### 1. Keep it Simple

- Use clear, concise language
- Break content into digestible sections
- Use headings hierarchically (H1 → H2 → H3)

### 2. Use Examples

Always provide code examples:

```python
# Good: Shows actual usage
response = await client.get_cases()

# Better: Shows complete context
from app.services import CaseService

async def example():
    service = CaseService()
    cases = await service.get_cases(limit=10)
    return cases
```

### 3. Link Related Content

```markdown
See also: [Authentication Guide](../api/authentication.md)
```

### 4. Keep it Updated

- Review docs when code changes
- Update examples with breaking changes
- Mark deprecated features

### 5. Use Admonitions

Guide users with helpful callouts:

```markdown
!!! tip "Performance Tip"
    Enable Redis caching for 10x faster queries

!!! warning "Breaking Change"
    This API changed in version 2.0
```

## 🛠️ Maintenance

### Update Dependencies

```bash
pip install --upgrade mkdocs mkdocs-material mkdocstrings
```

### Check for Broken Links

```bash
# Install linkchecker
pip install linkchecker

# Build and check
mkdocs build
linkchecker site/
```

### Validate Build

```bash
# Build with strict mode
mkdocs build --strict
```

This fails on warnings (useful for CI/CD).

## 📚 Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)

## 🤝 Contributing

When contributing documentation:

1. Follow the existing structure
2. Use consistent formatting
3. Test locally with `mkdocs serve`
4. Submit a pull request

## 📄 License

Documentation is licensed under the same license as the project (MIT License).
