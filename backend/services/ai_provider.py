"""
StoryVerse AI — AI Provider Abstraction
==========================================
Defines the base interface for AI models and implementations for
both Google Gemini and a Mock provider for automated testing.

Architecture:
  BaseAIProvider (Abstract)
    ├── GeminiProvider (Google Gen AI SDK)
    └── MockAIProvider (Automated testing & quota-free dev)
"""

import os
import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Ensure local .env in backend directory is loaded
_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(_env_path):
    load_dotenv(_env_path)


# ============================================================
# Domain Exceptions (Clean & Safe — Never Leak Keys)
# ============================================================

class AIError(Exception):
    """Base exception for all AI operations."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "AI_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class AIConfigurationError(AIError):
    """Raised when the AI provider or API key is missing or misconfigured."""
    def __init__(self, message: str = "AI service configuration error."):
        super().__init__(message, status_code=500, error_code="CONFIG_ERROR")


class AIAuthenticationError(AIError):
    """Raised when authentication with the AI provider fails (e.g. invalid key)."""
    def __init__(self, message: str = "AI service authentication failed. Please verify your credentials."):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR")


class AIModelNotFoundError(AIError):
    """Raised when the requested AI model is unknown or unsupported."""
    def __init__(self, message: str = "The requested AI model was not found."):
        super().__init__(message, status_code=404, error_code="MODEL_NOT_FOUND")


class AIRateLimitError(AIError):
    """Raised when the AI provider rate limit or quota is exceeded."""
    def __init__(self, message: str = "AI service rate limit exceeded. Please wait a moment and try again."):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT")


class AINetworkError(AIError):
    """Raised when connection to the AI provider fails."""
    def __init__(self, message: str = "Unable to reach the AI service due to a network error."):
        super().__init__(message, status_code=503, error_code="NETWORK_ERROR")


class AITimeoutError(AIError):
    """Raised when an AI request times out."""
    def __init__(self, message: str = "The AI generation request timed out. Please try again."):
        super().__init__(message, status_code=504, error_code="TIMEOUT")


class AIEmptyResponseError(AIError):
    """Raised when the AI returns an empty or whitespace-only response."""
    def __init__(self, message: str = "The AI provider returned an empty response."):
        super().__init__(message, status_code=502, error_code="EMPTY_RESPONSE")


class AIMalformedResponseError(AIError):
    """Raised when the AI response cannot be parsed or lacks expected structure."""
    def __init__(self, message: str = "The AI provider returned a malformed response."):
        super().__init__(message, status_code=502, error_code="MALFORMED_RESPONSE")


# ============================================================
# Security Helper: Sanitize Error Messages
# ============================================================

def sanitize_error_message(raw_msg: str) -> str:
    """
    Strips potential API keys, sensitive tokens, and system paths from error messages.
    """
    if not raw_msg:
        return "An unknown error occurred in the AI service."
    # Censor standard 39-character Google API keys (AIza...)
    sanitized = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_API_KEY]', str(raw_msg))
    # Censor generic api_key=... patterns
    sanitized = re.sub(r'(api_?key["\']?\s*[:=]\s*["\']?)([^"\'\s,]+)', r'\1[REDACTED]', sanitized, flags=re.IGNORECASE)
    return sanitized


# ============================================================
# Provider Base Interface
# ============================================================

class BaseAIProvider(ABC):
    """Abstract interface that all AI providers must implement."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generates text using the provider.

        Returns:
            dict containing:
                - text: str (generated content)
                - provider: str ("gemini" | "mock")
                - model: str
                - finish_reason: str
                - tokens_used: int or None
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured and ready."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the provider name identifier."""
        pass


# ============================================================
# Google Gemini Provider (Official google-genai SDK)
# ============================================================

class GeminiProvider(BaseAIProvider):
    """
    Official Google GenAI SDK Provider.
    Communicates with Gemini models using google.genai Client.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30
    ):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()

        if model is not None:
            self.model_name = model.strip()
        else:
            self.model_name = (os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")).strip()

        self.timeout = timeout
        self._client = None
        self.last_prompt = None
        self.call_count = 0

        if self.api_key:
            self._init_client()

    def get_masked_key(self) -> str:
        """Returns a safely masked key string (e.g. 'AQ...EmQ') without revealing the key."""
        if not self.api_key:
            return "Not Configured"
        k = self.api_key.strip()
        if len(k) <= 8:
            return "***"
        return f"{k[:4]}...{k[-4:]}"

    def _init_client(self):
        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=self.timeout * 1000)
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google GenAI client: {sanitize_error_message(str(e))}")
            self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def get_provider_name(self) -> str:
        return "gemini"

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """Calls Gemini API using the official Google Gen AI SDK."""
        if not self.is_available():
            raise AIConfigurationError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment or .env file."
            )

        if not prompt or not prompt.strip():
            raise AIEmptyResponseError("Cannot generate content with an empty prompt.")

        self.last_prompt = prompt
        self.call_count += 1

        if self._client is None:
            self._init_client()
            if self._client is None:
                raise AIConfigurationError("Failed to initialize Google Gen AI client.")

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction if system_instruction else None
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Check if response text is present
            text = getattr(response, "text", None)
            if text is None:
                # Some safety blocks or empty candidates may not populate .text
                candidates = getattr(response, "candidates", [])
                if candidates:
                    parts = getattr(candidates[0].content, "parts", [])
                    if parts and hasattr(parts[0], "text"):
                        text = parts[0].text

            if not text or not str(text).strip():
                raise AIEmptyResponseError("Gemini returned an empty response. The content may have triggered safety filters.")

            # Extract token metadata if available
            tokens_used = None
            usage = getattr(response, "usage_metadata", None)
            if usage:
                tokens_used = getattr(usage, "total_token_count", None)

            finish_reason = "STOP"
            if hasattr(response, "candidates") and response.candidates:
                finish_reason = str(getattr(response.candidates[0], "finish_reason", "STOP"))

            return {
                "text": text.strip(),
                "provider": "gemini",
                "model": self.model_name,
                "finish_reason": finish_reason,
                "tokens_used": tokens_used
            }

        except AIError:
            raise
        except Exception as err:
            err_str = str(err)
            sanitized = sanitize_error_message(err_str)
            logger.error(f"Gemini API invocation failure: {sanitized}")

            # Map common error scenarios
            lower = err_str.lower()
            if "api_key_invalid" in lower or "api key not valid" in lower or "permission_denied" in lower or "unauthenticated" in lower:
                raise AIAuthenticationError("Invalid or unauthorized Gemini API key.")
            elif "not_found" in lower or "model not found" in lower:
                raise AIModelNotFoundError(f"Gemini model '{self.model_name}' was not found or is unavailable.")
            elif "resource_exhausted" in lower or "rate limit" in lower or "quota" in lower or "429" in lower:
                raise AIRateLimitError("Gemini API rate limit or quota exceeded. Please try again later.")
            elif "timeout" in lower or "timed out" in lower:
                raise AITimeoutError("Gemini API request timed out.")
            elif "connection" in lower or "failed to connect" in lower or "dns" in lower:
                raise AINetworkError("Network error while connecting to Gemini API.")
            else:
                raise AIError(f"Gemini generation error: {sanitized}")


# ============================================================
# Mock Provider (Automated Testing & Offline Development)
# ============================================================

class MockAIProvider(BaseAIProvider):
    """
    Safe Mock AI Provider for automated tests.
    Never calls external networks or consumes Gemini API quota.
    Can be configured to simulate errors or return specific text.
    """

    def __init__(self, default_response: Optional[str] = None):
        self.default_response = default_response
        self.simulation_mode: Optional[str] = None  # E.g. 'rate_limit', 'timeout', 'network_error', 'empty'
        self.last_prompt: Optional[str] = None
        self.call_count: int = 0

    def is_available(self) -> bool:
        return True

    def get_provider_name(self) -> str:
        return "mock"

    def simulate_error(self, error_type: Optional[str]):
        """Configures the mock to raise a simulated error on next calls."""
        self.simulation_mode = error_type

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """Generates predictable mocked text or simulates errors for testing."""
        # Check simulation modes
        if self.simulation_mode == "rate_limit":
            raise AIRateLimitError("Simulated rate limit exceeded.")
        elif self.simulation_mode == "timeout":
            raise AITimeoutError("Simulated generation timeout.")
        elif self.simulation_mode == "network_error":
            raise AINetworkError("Simulated network connection failure.")
        elif self.simulation_mode == "auth_error":
            raise AIAuthenticationError("Simulated authentication failure.")
        elif self.simulation_mode == "model_not_found":
            raise AIModelNotFoundError("Simulated model not found error.")
        elif self.simulation_mode == "empty":
            raise AIEmptyResponseError("Simulated empty response.")
        elif self.simulation_mode == "malformed":
            raise AIMalformedResponseError("Simulated malformed response.")

        if not prompt or not prompt.strip():
            raise AIEmptyResponseError("Cannot generate content with an empty prompt.")

        self.last_prompt = prompt
        self.call_count += 1

        if self.default_response:
            generated_text = self.default_response
        else:
            # Deterministic, structured response for test verification
            generated_text = (
                f"[MOCK_GENERATION]\n"
                f"Prompt Received: {prompt[:80]}...\n"
                f"Content: In a world shaped by imagination, the journey began with purpose.\n"
                f"Status: Validated test output."
            )

        return {
            "text": generated_text,
            "provider": "mock",
            "model": "mock-model-v1",
            "finish_reason": "STOP",
            "tokens_used": 128
        }


# ============================================================
# Factory Function: get_ai_provider()
# ============================================================

def get_ai_provider(
    provider_name: Optional[str] = None,
    mock_mode: Optional[bool] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = None
) -> BaseAIProvider:
    """
    Factory function returning the configured AI provider.

    Selection Logic:
    1. If mock_mode is explicitly True or AI_MOCK_MODE is enabled in env -> MockAIProvider
    2. If provider_name is 'mock' or AI_PROVIDER is 'mock' -> MockAIProvider
    3. Default -> GeminiProvider
    """
    is_mock = mock_mode
    selected_provider = (provider_name or os.environ.get("AI_PROVIDER", "gemini")).lower()

    # Check Flask app configuration if within request/app context
    try:
        from flask import current_app, has_app_context
        if has_app_context() and current_app:
            if is_mock is None:
                is_mock = current_app.config.get("AI_MOCK_MODE")
            if not provider_name:
                selected_provider = str(current_app.config.get("AI_PROVIDER", selected_provider)).lower()
            if not api_key:
                api_key = current_app.config.get("GEMINI_API_KEY")
            if not model:
                model = current_app.config.get("GEMINI_MODEL")
            if timeout is None:
                timeout = current_app.config.get("AI_REQUEST_TIMEOUT", 30)
    except Exception:
        pass

    if timeout is None:
        timeout = int(os.environ.get("AI_REQUEST_TIMEOUT", 30))

    if is_mock is None:
        is_mock = os.environ.get("AI_MOCK_MODE", "false").lower() in ("true", "1", "yes")

    if is_mock or selected_provider == "mock":
        return MockAIProvider()

    if selected_provider == "gemini":
        return GeminiProvider(api_key=api_key, model=model, timeout=timeout)

    # Fallback to mock with warning if unknown provider specified
    logger.warning(f"Unknown AI provider '{selected_provider}'. Falling back to MockAIProvider.")
    return MockAIProvider()
