# Testing Guide

Guide for running and writing tests.

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/
```

## Test Structure

```
tests/
├── test_auth.py          # Authentication tests
├── test_cases.py         # Case management tests
├── test_analytics.py     # Analytics tests
└── test_chatbot.py       # Chatbot tests
```

## Writing Tests

Example test:

```python
def test_create_case(client, auth_headers):
    response = client.post(
        "/api/v1/cases",
        json={"status": "open", "severity": "high"},
        headers=auth_headers
    )
    assert response.status_code == 201
```

## Next Steps

- [Project Structure](structure.md)
- [Contributing](contributing.md)
