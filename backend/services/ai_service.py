"""
StoryVerse AI — AI Service Orchestrator
==========================================
Central service providing high-level generation, response parsing,
and unified error handling across all application operations.

Responsibilities:
  - call_ai_model(): Invokes the underlying provider with telemetry.
  - generate_text(): High-level text generation helper.
  - parse_ai_response(): Validates and extracts structured payload.
  - handle_api_error(): Converts exceptions into standardized JSON responses.
"""

import logging
from typing import Dict, Any, Optional, Tuple

from .ai_provider import (
    BaseAIProvider,
    get_ai_provider,
    AIError,
    AIConfigurationError,
    AIAuthenticationError,
    AIModelNotFoundError,
    AIRateLimitError,
    AINetworkError,
    AITimeoutError,
    AIEmptyResponseError,
    AIMalformedResponseError,
    sanitize_error_message
)
from .rag_errors import RAGUnavailableError
from utils.response import (
    error_response,
    server_error_response,
    ai_error_response,
    rate_limit_response
)

logger = logging.getLogger(__name__)


class AIService:
    """
    Orchestrates AI model calls, sanitizes outputs, and provides
    centralized error formatting for API routes.
    """

    def __init__(self, provider: Optional[BaseAIProvider] = None):
        self._provider = provider

    @property
    def provider(self) -> BaseAIProvider:
        """Lazy-loads the provider so configuration changes take effect dynamically."""
        if self._provider is None:
            self._provider = get_ai_provider()
        return self._provider

    def set_provider(self, provider: BaseAIProvider):
        """Allows injecting custom or mock providers for testing."""
        self._provider = provider

    def call_ai_model(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes the AI generation via the active provider.

        Returns:
            dict containing 'text', 'provider', 'model', 'finish_reason', 'tokens_used'
        """
        if not prompt or not prompt.strip():
            raise AIEmptyResponseError("Cannot generate content with an empty prompt.")

        logger.info(f"Invoking AI provider '{self.provider.get_provider_name()}'...")
        result = self.provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return self.parse_ai_response(result)

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Convenience wrapper returning just the cleaned generated string.
        """
        payload = self.call_ai_model(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return payload["text"]

    def parse_ai_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates that the AI returned a valid text payload.

        Args:
            raw_response (dict): Output from the provider's generate() method.

        Returns:
            dict: Cleaned and verified response dictionary.
        """
        if not isinstance(raw_response, dict):
            raise AIMalformedResponseError("AI provider returned a non-dictionary response.")

        text = raw_response.get("text")
        if text is None or not str(text).strip():
            raise AIEmptyResponseError("AI provider returned empty content.")

        clean_text = str(text).strip()

        return {
            "text": clean_text,
            "provider": raw_response.get("provider", "unknown"),
            "model": raw_response.get("model", "default"),
            "finish_reason": raw_response.get("finish_reason", "STOP"),
            "tokens_used": raw_response.get("tokens_used")
        }

    @staticmethod
    def handle_api_error(err: Exception) -> Tuple[Any, int]:
        """
        Translates domain AI exceptions into safe, standardized Flask JSON responses.
        Prevents leaking API keys or internal stack traces.
        """
        logger.error(f"AI Service Exception: {type(err).__name__} - {sanitize_error_message(str(err))}")

        if isinstance(err, RAGUnavailableError):
            return error_response(
                message=str(err),
                errors={"rag": "Semantic retrieval is unavailable."},
                status_code=503
            )

        if isinstance(err, AIConfigurationError):
            return error_response(
                message=err.message,
                errors={"configuration": "AI provider is not configured properly."},
                status_code=500
            )

        if isinstance(err, AIAuthenticationError):
            return error_response(
                message="AI authentication failed. Please check your API credentials.",
                errors={"authentication": "Invalid or expired API credentials."},
                status_code=401
            )

        if isinstance(err, AIModelNotFoundError):
            return error_response(
                message="The requested AI model is unavailable or does not exist.",
                errors={"model": err.message},
                status_code=404
            )

        if isinstance(err, AIRateLimitError):
            return rate_limit_response(
                message="AI service rate limit exceeded. Please wait a moment and try again."
            )

        if isinstance(err, AITimeoutError):
            return error_response(
                message="The AI service request timed out. Please try again.",
                errors={"timeout": "Request exceeded time limit."},
                status_code=504
            )

        if isinstance(err, AINetworkError):
            return ai_error_response(
                message="Network error while communicating with the AI service. Please check your internet connection."
            )

        if isinstance(err, AIEmptyResponseError):
            return error_response(
                message="The AI provider returned an empty response. Please adjust your prompt and retry.",
                errors={"content": "Empty generation response."},
                status_code=502
            )

        if isinstance(err, AIMalformedResponseError):
            return ai_error_response(
                message="Received a malformed response from the AI provider."
            )

        # Fallback for unexpected exceptions
        return server_error_response(
            message="An unexpected error occurred during AI content generation."
        )


# Global default instance
ai_service = AIService()
