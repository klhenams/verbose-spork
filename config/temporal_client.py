import os
from typing import ClassVar

from temporalio.client import Client


class TemporalClientManager:
    """Manager for maintaining a shared async Temporal client instance."""

    _instance: ClassVar[Client | None] = None

    @classmethod
    async def get_client(cls) -> Client:
        """Returns or lazily initializes the shared Temporal client connection."""
        if cls._instance is None:
            temporal_host = os.environ.get("TEMPORAL_HOST", "temporal:7233")
            cls._instance = await Client.connect(temporal_host)
        return cls._instance
