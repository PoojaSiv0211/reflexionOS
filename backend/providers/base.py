"""
ReflexionOS — Provider abstraction
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Abstract interface every LLM provider must implement."""

    @abstractmethod
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Call the underlying model and return parsed JSON.

        Raises:
            ValueError: if the response cannot be parsed as JSON.
            RuntimeError: on provider-level errors.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider identifier."""
        ...
