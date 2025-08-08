"""
Pytest configuration for django-i18n-noprefix tests.
"""

import os
import sys
from pathlib import Path

import django
import pytest
from django.conf import settings

# Add project root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def pytest_configure(config):
    """Configure Django settings for tests."""
    if not settings.configured:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_project.settings")
        django.setup()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    This avoids having to mark every test with @pytest.mark.django_db
    """
    pass


@pytest.fixture
def client():
    """Django test client fixture."""
    from django.test import Client

    return Client()


@pytest.fixture
def rf():
    """Django RequestFactory fixture."""
    from django.test import RequestFactory

    return RequestFactory()


@pytest.fixture
def user(db):
    """Create a test user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def languages_settings():
    """Common language settings for tests."""
    return [
        ("ko", "Korean"),
        ("en", "English"),
        ("ja", "Japanese"),
    ]


@pytest.fixture
def mock_request(rf):
    """Create a mock request with common attributes."""

    def _make_request(path="/", method="GET", **kwargs):
        request_method = getattr(rf, method.lower())
        request = request_method(path, **kwargs)

        # Add session-like dictionary with minimal SessionBase interface
        class MockSession(dict):
            """Mock session that behaves like Django's SessionBase."""

            def __init__(self):
                super().__init__()
                self.modified = False

            def save(self):
                self.modified = True

        request.session = MockSession()

        # Add COOKIES
        request.COOKIES = {}

        # Add META headers
        if "headers" in kwargs:
            for key, value in kwargs["headers"].items():
                request.META[f'HTTP_{key.upper().replace("-", "_")}'] = value

        return request

    return _make_request


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    from unittest.mock import Mock

    class MockResponse:
        def __init__(self):
            self.cookies = {}
            self.status_code = 200
            self.content = b""
            self._headers = {}
            # Create a Mock for set_cookie that also updates cookies
            self.set_cookie = Mock(side_effect=self._set_cookie)

        def _set_cookie(self, key, value, **kwargs):
            self.cookies[key] = value

        def delete_cookie(self, key):
            if key in self.cookies:
                del self.cookies[key]

        def __setitem__(self, key, value):
            self._headers[key] = value

        def __getitem__(self, key):
            return self._headers.get(key)

    return MockResponse()
