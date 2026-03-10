import os
import pytest
from fastapi.testclient import TestClient

# Use testnet and dummy keys for tests (no real calls if we mock)
os.environ.setdefault("BYBIT_TESTNET", "true")
os.environ.setdefault("BYBIT_API_KEY", "test_key")
os.environ.setdefault("BYBIT_API_SECRET", "test_secret")


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)
