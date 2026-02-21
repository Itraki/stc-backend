import pytest
import mongomock_motor
from app.config import settings


@pytest.fixture
async def test_db():
    """Create test database using mongomock"""
    client = mongomock_motor.AsyncMongoMockClient()
    db = client.get_database("stc-db-test")
    yield db
    client.close()


@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
