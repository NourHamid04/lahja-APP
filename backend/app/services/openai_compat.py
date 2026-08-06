"""Small compatibility layer so mock-mode tests can run without the OpenAI SDK installed."""

try:
    from openai import (
        APIConnectionError,
        APIError,
        AuthenticationError,
        OpenAI,
        RateLimitError,
    )
    OPENAI_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - used only in minimal/mock environments
    OPENAI_SDK_AVAILABLE = False
    OpenAI = None  # type: ignore[assignment]

    class APIError(Exception):
        pass

    class APIConnectionError(APIError):
        pass

    class AuthenticationError(APIError):
        pass

    class RateLimitError(APIError):
        pass
