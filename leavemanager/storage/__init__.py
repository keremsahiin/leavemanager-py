"""Kalıcılık: şimdilik bellekte, sonra SQL (seçim ADR ile)."""

from leavemanager.storage.memory import InMemoryRepository
from leavemanager.storage.repository import LeaveRepository

__all__ = ["InMemoryRepository", "LeaveRepository"]
