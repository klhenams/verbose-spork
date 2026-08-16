"""Pytest configuration for products app tests."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def authenticated_user(db):
    """Create and return an authenticated user."""
    return User.objects.create_user(
        email="test@example.com",
        password="test-password-123",  # noqa: S106
    )


@pytest.fixture
def authenticated_client(client, authenticated_user):
    """Create an authenticated client."""
    client.force_login(authenticated_user)
    return client
