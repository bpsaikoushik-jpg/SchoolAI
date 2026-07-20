"""Provider-agnostic data types for the AI Provider Layer."""
from dataclasses import dataclass, field
from typing import List, Literal, Optional, AsyncIterator

Role = Literal["system", "user", "assistant"]


@dataclass
class AIMessage:
    role: Role
    content: str


@dataclass
class AICompletion:
    """Normalized non-streaming completion result."""
    content: str
    provider: str
    model: str
    raw: Optional[dict] = field(default=None, repr=False)
    usage: Optional[dict] = None


class AIProviderError(Exception):
    """Raised when a provider call fails after retries are exhausted."""

    def __init__(self, provider: str, message: str, retriable: bool = False):
        self.provider = provider
        self.retriable = retriable
        super().__init__(f"[{provider}] {message}")


class AIAllProvidersFailedError(Exception):
    """Raised when the primary provider and all configured fallbacks fail."""

    def __init__(self, attempts: List[AIProviderError]):
        self.attempts = attempts
        summary = "; ".join(str(a) for a in attempts)
        super().__init__(f"All AI providers failed: {summary}")
