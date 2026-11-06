"""
StoryVerse AI — Writing Assistant Service
============================================
Core business logic for AI-assisted writing tools:
  - Text rewriting (clarity, grammar, professional, creative, engaging, simplify)
  - Literary translation (English, Telugu, Tamil, Hindi)
  - Variable-length summarization (short, medium, detailed)
  - Dynamic dialogue generation
  - Shocking plot twist generation
  - Seamless narrative continuation
"""

import logging
from typing import Dict, Any, Optional

from .ai_service import ai_service
from .prompt_service import (
    SYSTEM_INSTRUCTION_CREATIVE,
    build_rewrite_prompt,
    build_translate_prompt,
    build_summarize_prompt,
    build_dialogue_prompt,
    build_plot_twist_prompt,
    build_continue_prompt,
)

logger = logging.getLogger(__name__)


class WritingAssistantService:
    """
    Coordinates modular AI writing assistant capabilities.
    """

    def __init__(self, ai_svc=None):
        self.ai = ai_svc or ai_service

    def rewrite(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rewrites provided text according to style instructions.
        """
        content = (params.get("content") or params.get("text") or "").strip()
        style = (params.get("style") or params.get("mode") or "improve clarity").strip()
        language = params.get("language")

        prompt = build_rewrite_prompt(content=content, style_instructions=style, language=language)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.7
        )

        rewritten = ai_result["text"]

        return {
            "original": content,
            "rewritten": rewritten,
            "style": style,
            "operation": "rewrite",
            "metadata": {
                "language": language or "English",
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used")
            }
        }

    def translate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Culturally nuanced literary translation into English, Telugu, Tamil, or Hindi.
        """
        content = (params.get("content") or params.get("text") or "").strip()
        target_lang = (params.get("target_language") or params.get("language") or "English").strip()

        prompt = build_translate_prompt(content=content, target_language=target_lang)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.4
        )

        translation = ai_result["text"]

        return {
            "original": content,
            "translation": translation,
            "target_language": target_lang,
            "operation": "translate",
            "metadata": {
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used")
            }
        }

    def summarize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarizes text in selectable lengths (short, medium, detailed).
        """
        content = (params.get("content") or params.get("text") or "").strip()
        length = (params.get("length") or params.get("summary_length") or "medium").strip()
        language = params.get("language")

        prompt = build_summarize_prompt(content=content, summary_length=length, language=language)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.5
        )

        summary = ai_result["text"]

        return {
            "original": content,
            "summary": summary,
            "length": length,
            "operation": "summarize",
            "metadata": {
                "language": language or "English",
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used")
            }
        }

    def generate_dialogue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates realistic character dialogue based on context, tone, and character dynamics.
        """
        context = (params.get("context") or params.get("topic") or params.get("content") or "").strip()
        characters = params.get("characters", "Two characters")
        if isinstance(characters, list):
            characters = ", ".join(str(c).strip() for c in characters)

        retrieved_context = []
        if params.get("use_rag") or params.get("rag_query") or params.get("project_id"):
            if not params.get("rag_context"):
                try:
                    from .rag_service import rag_service
                    from .prompt_service import build_rag_context_block
                    query = params.get("rag_query") or context or str(characters)
                    p_id = params.get("project_id") or params.get("rag_project_id")
                    retrieved_context = rag_service.retrieve_context(
                        query=query,
                        n_results=params.get("rag_n_results", 3),
                        project_id=p_id,
                        language=params.get("language")
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except Exception as e:
                    logger.warning(f"RAG retrieval skipped in generate_dialogue: {e}")

        dialogue_params = {
            "context": context,
            "characters": characters,
            "topic": params.get("topic") or context,
            "subtext": params.get("subtext", "Unspoken stakes and emotional tension"),
            "tone": params.get("tone", "Tense"),
            "genre": params.get("genre", "Drama"),
            "language": params.get("language", "English"),
            "rag_context": params.get("rag_context")
        }

        prompt = build_dialogue_prompt(dialogue_params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.8
        )

        dialogue = ai_result["text"]

        return {
            "dialogue": dialogue,
            "context": context,
            "characters": characters,
            "retrieved_context": retrieved_context,
            "operation": "generate-dialogue",
            "metadata": {
                "genre": dialogue_params["genre"],
                "tone": dialogue_params["tone"],
                "language": dialogue_params["language"],
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used"),
                "rag_applied": bool(params.get("rag_context")),
                "retrieved_chunks_count": len(retrieved_context)
            }
        }

    def generate_plot_twist(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates shocking yet logically consistent plot twists.
        """
        premise = (
            params.get("premise")
            or params.get("plot")
            or params.get("context")
            or params.get("content")
            or ""
        ).strip()

        twist_params = {
            "premise": premise,
            "genre": params.get("genre", "Thriller"),
            "characters": params.get("characters", ""),
            "tone": params.get("tone", "Suspenseful"),
            "language": params.get("language", "English")
        }

        prompt = build_plot_twist_prompt(twist_params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.85
        )

        plot_twists = ai_result["text"]

        return {
            "premise": premise,
            "plot_twists": plot_twists,
            "operation": "generate-plot-twist",
            "metadata": {
                "genre": twist_params["genre"],
                "tone": twist_params["tone"],
                "language": twist_params["language"],
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used")
            }
        }

    def continue_writing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Seamlessly continues narrative or script from where it ended.
        """
        content = (params.get("content") or params.get("text") or "").strip()
        direction = params.get("direction") or params.get("instructions")
        language = params.get("language")

        retrieved_context = []
        if params.get("use_rag") or params.get("rag_query") or params.get("project_id"):
            if not params.get("rag_context"):
                try:
                    from .rag_service import rag_service
                    from .prompt_service import build_rag_context_block
                    query = params.get("rag_query") or direction or content[:300]
                    p_id = params.get("project_id") or params.get("rag_project_id")
                    retrieved_context = rag_service.retrieve_context(
                        query=query,
                        n_results=params.get("rag_n_results", 3),
                        project_id=p_id,
                        language=language
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except Exception as e:
                    logger.warning(f"RAG retrieval skipped in continue_writing: {e}")

        prompt = build_continue_prompt(
            content=content,
            direction=direction,
            language=language,
            rag_context=params.get("rag_context")
        )
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.75
        )

        continuation = ai_result["text"]
        combined = f"{content}\n\n{continuation}".strip()

        return {
            "original": content,
            "continuation": continuation,
            "combined_text": combined,
            "retrieved_context": retrieved_context,
            "operation": "continue-writing",
            "metadata": {
                "language": language or "English",
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used"),
                "rag_applied": bool(params.get("rag_context")),
                "retrieved_chunks_count": len(retrieved_context)
            }
        }


# Global default instance
writing_assistant_service = WritingAssistantService()
