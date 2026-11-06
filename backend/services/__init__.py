"""
StoryVerse AI — Services Package
===================================
Exports AI service, provider abstraction, and prompt engineering utilities.
"""

from .ai_provider import (
    BaseAIProvider,
    GeminiProvider,
    MockAIProvider,
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
    sanitize_error_message,
)

from .ai_service import AIService, ai_service
from .story_service import StoryService, story_service
from .script_service import ScriptService, script_service
from .character_service import CharacterService, character_service
from .writing_assistant_service import WritingAssistantService, writing_assistant_service
from .project_service import ProjectService, project_service
from .export_service import ExportService, export_service
from .embedding_service import EmbeddingService, embedding_service
from .rag_service import RAGService, rag_service

from .prompt_service import (
    SYSTEM_INSTRUCTION_CREATIVE,
    build_story_prompt,
    build_script_prompt,
    build_character_prompt,
    build_character_variations_prompt,
    build_scene_prompt,
    build_dialogue_prompt,
    build_rewrite_prompt,
    build_expand_prompt,
    build_shorten_prompt,
    build_continue_prompt,
    build_translate_prompt,
    build_summarize_prompt,
    build_plot_twist_prompt,
    build_rag_context_block,
)

__all__ = [
    "BaseAIProvider",
    "GeminiProvider",
    "MockAIProvider",
    "get_ai_provider",
    "AIError",
    "AIConfigurationError",
    "AIAuthenticationError",
    "AIModelNotFoundError",
    "AIRateLimitError",
    "AINetworkError",
    "AITimeoutError",
    "AIEmptyResponseError",
    "AIMalformedResponseError",
    "sanitize_error_message",
    "AIService",
    "ai_service",
    "StoryService",
    "story_service",
    "ScriptService",
    "script_service",
    "CharacterService",
    "character_service",
    "WritingAssistantService",
    "writing_assistant_service",
    "ProjectService",
    "project_service",
    "ExportService",
    "export_service",
    "SYSTEM_INSTRUCTION_CREATIVE",
    "build_story_prompt",
    "build_script_prompt",
    "build_character_prompt",
    "build_scene_prompt",
    "build_dialogue_prompt",
    "build_rewrite_prompt",
    "build_expand_prompt",
    "build_shorten_prompt",
    "build_continue_prompt",
    "build_translate_prompt",
    "build_summarize_prompt",
]
