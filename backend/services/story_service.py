"""
StoryVerse AI — Story Service
================================
Core business logic for story generation, section parsing,
and iterative story editing operations (regenerate, expand, shorten, continue).
"""

import re
import logging
from typing import Dict, Any, Optional

from .ai_service import ai_service
from .rag_errors import RAGUnavailableError
from .prompt_service import (
    SYSTEM_INSTRUCTION_CREATIVE,
    build_story_prompt,
    build_rewrite_prompt,
    build_expand_prompt,
    build_shorten_prompt,
    build_continue_prompt,
)

logger = logging.getLogger(__name__)


class StoryService:
    """
    Manages story generation workflows, structured output parsing,
    and editing operations.
    """

    def __init__(self, ai_svc=None):
        self.ai = ai_svc or ai_service

    def generate_story(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a complete, structured story using the configured AI provider.

        Args:
            params (dict): Validated input parameters (topic, genre, language, etc.)

        Returns:
            dict containing:
                - title (str)
                - summary (str)
                - setting (str)
                - characters (str)
                - introduction (str)
                - main_plot (str)
                - conflict (str)
                - climax (str)
                - conclusion (str)
                - moral (str)
                - full_text (str)
                - metadata (dict)
        """
        retrieved_context = []
        if params.get("use_rag") or params.get("rag_query") or params.get("project_id"):
            if not params.get("rag_context"):
                try:
                    from .rag_service import rag_service
                    from .prompt_service import build_rag_context_block
                    query = params.get("rag_query") or params.get("topic") or ""
                    p_id = params.get("project_id") or params.get("rag_project_id")
                    retrieved_context = rag_service.retrieve_context(
                        query=query,
                        n_results=params.get("rag_n_results", rag_service.default_top_k),
                        project_id=p_id,
                        genre=params.get("genre")
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except RAGUnavailableError:
                    raise
                except Exception as e:
                    logger.exception("RAG retrieval failed in story generation.")
                    raise RAGUnavailableError("RAG retrieval is unavailable.") from e

        prompt = build_story_prompt(params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.75
        )

        full_text = ai_result["text"]
        sections = self.parse_story_sections(full_text)

        # Merge metadata
        metadata = {
            "topic": params.get("topic"),
            "genre": params.get("genre", "Fantasy"),
            "language": params.get("language", "English"),
            "tone": params.get("tone", "Emotional"),
            "length": params.get("length", "Medium"),
            "audience": params.get("audience", "General Audience"),
            "provider": ai_result.get("provider", "unknown"),
            "model": ai_result.get("model", "default"),
            "tokens_used": ai_result.get("tokens_used"),
            "rag_applied": bool(params.get("rag_context")),
            "retrieved_chunks_count": len(retrieved_context)
        }

        return {
            **sections,
            "full_text": full_text,
            "retrieved_context": retrieved_context,
            "metadata": metadata
        }

    def regenerate_story(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Regenerates a story based on previous content or modified instructions.
        """
        content = params.get("content", "").strip()
        instructions = params.get("instructions", "").strip()
        language = params.get("language")

        if content:
            style_guide = instructions if instructions else "Provide a fresh, creative retelling with elevated drama and pacing."
            prompt = build_rewrite_prompt(content=content, style_instructions=style_guide, language=language)
            ai_result = self.ai.call_ai_model(prompt=prompt, system_instruction=SYSTEM_INSTRUCTION_CREATIVE)
            full_text = ai_result["text"]
            sections = self.parse_story_sections(full_text)
            return {
                **sections,
                "full_text": full_text,
                "operation": "regenerate",
                "metadata": {
                    "language": language or "English",
                    "provider": ai_result.get("provider"),
                    "model": ai_result.get("model"),
                    "tokens_used": ai_result.get("tokens_used")
                }
            }
        else:
            # Fall back to generate_story with parameters
            return self.generate_story(params)

    def expand_story(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expands an existing story with deeper sensory and emotional details.
        """
        content = params.get("content", "").strip()
        focus_area = params.get("focus_area") or params.get("instructions")
        language = params.get("language")

        prompt = build_expand_prompt(content=content, focus_area=focus_area, language=language)
        ai_result = self.ai.call_ai_model(prompt=prompt, system_instruction=SYSTEM_INSTRUCTION_CREATIVE)
        expanded_text = ai_result["text"]

        return {
            "full_text": expanded_text,
            "operation": "expand",
            "metadata": {
                "language": language or "English",
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used")
            }
        }

    def shorten_story(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Condenses an existing story while preserving critical plot points.
        """
        content = params.get("content", "").strip()
        target_reduction = params.get("target_reduction", "50%")

        prompt = build_shorten_prompt(content=content, target_reduction=target_reduction)
        ai_result = self.ai.call_ai_model(prompt=prompt, system_instruction=SYSTEM_INSTRUCTION_CREATIVE)
        condensed_text = ai_result["text"]

        return {
            "full_text": condensed_text,
            "operation": "shorten",
            "metadata": {
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used")
            }
        }

    def continue_story(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Seamlessly continues a narrative from its current endpoint.
        """
        content = params.get("content", "").strip()
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
                        n_results=params.get("rag_n_results", rag_service.default_top_k),
                        project_id=p_id
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except RAGUnavailableError:
                    raise
                except Exception as e:
                    logger.exception("RAG retrieval failed in continue_story.")
                    raise RAGUnavailableError("RAG retrieval is unavailable.") from e

        prompt = build_continue_prompt(
            content=content,
            direction=direction,
            language=language,
            rag_context=params.get("rag_context")
        )
        ai_result = self.ai.call_ai_model(prompt=prompt, system_instruction=SYSTEM_INSTRUCTION_CREATIVE)
        continuation_text = ai_result["text"]

        combined_text = f"{content}\n\n{continuation_text}".strip()

        return {
            "continuation": continuation_text,
            "full_text": combined_text,
            "retrieved_context": retrieved_context,
            "operation": "continue",
            "metadata": {
                "language": language or "English",
                "provider": ai_result.get("provider"),
                "model": ai_result.get("model"),
                "tokens_used": ai_result.get("tokens_used"),
                "rag_applied": bool(params.get("rag_context")),
                "retrieved_chunks_count": len(retrieved_context)
            }
        }

    @staticmethod
    def parse_story_sections(text: str) -> Dict[str, str]:
        """
        Robustly parses a story text into 10 structured sections.
        If a section is missing from explicit headings, handles gracefully.
        """
        sections = {
            "title": "Untitled Story",
            "summary": "",
            "setting": "",
            "characters": "",
            "introduction": "",
            "main_plot": "",
            "conflict": "",
            "climax": "",
            "conclusion": "",
            "moral": ""
        }

        if not text or not text.strip():
            return sections

        # Section pattern mappings
        patterns = [
            ("title", r"(?:1\.\s*)?(?:TITLE|Title)\s*:\s*(.*?)(?=\n\s*(?:2\.\s*)?(?:SYNOPSIS|Synopsis|SUMMARY|Summary)|$)"),
            ("summary", r"(?:2\.\s*)?(?:SYNOPSIS|Synopsis|SUMMARY|Summary)\s*:\s*(.*?)(?=\n\s*(?:3\.\s*)?(?:SETTING|Setting)|$)"),
            ("setting", r"(?:3\.\s*)?(?:SETTING|Setting)\s*:\s*(.*?)(?=\n\s*(?:4\.\s*)?(?:CHARACTERS|Characters)|$)"),
            ("characters", r"(?:4\.\s*)?(?:CHARACTERS|Characters)\s*:\s*(.*?)(?=\n\s*(?:5\.\s*)?(?:ACT\s*I|Act\s*I|INTRODUCTION|Introduction)|$)"),
            ("introduction", r"(?:5\.\s*)?(?:ACT\s*I(?:\s*-\s*THE\s*BEGINNING)?|Act\s*I|INTRODUCTION|Introduction)\s*:\s*(.*?)(?=\n\s*(?:6\.\s*)?(?:ACT\s*II|Act\s*II|MAIN\s*PLOT|Main\s*Plot)|$)"),
            ("main_plot", r"(?:6\.\s*)?(?:ACT\s*II(?:\s*-\s*THE\s*CONFLICT)?|Act\s*II|MAIN\s*PLOT|Main\s*Plot)\s*:\s*(.*?)(?=\n\s*(?:7\.\s*)?(?:CONFLICT|Conflict)|$)"),
            ("conflict", r"(?:7\.\s*)?(?:CONFLICT|Conflict)\s*:\s*(.*?)(?=\n\s*(?:8\.\s*)?(?:ACT\s*III|Act\s*III|CLIMAX|Climax)|$)"),
            ("climax", r"(?:8\.\s*)?(?:ACT\s*III(?:\s*-\s*THE\s*CLIMAX)?|Act\s*III|CLIMAX|Climax)\s*:\s*(.*?)(?=\n\s*(?:9\.\s*)?(?:CONCLUSION|Conclusion|RESOLUTION|Resolution)|$)"),
            ("conclusion", r"(?:9\.\s*)?(?:CONCLUSION|Conclusion|RESOLUTION|Resolution)\s*:\s*(.*?)(?=\n\s*(?:10\.\s*)?(?:MORAL|Moral|THEME|Theme)|$)"),
            ("moral", r"(?:10\.\s*)?(?:MORAL(?:\s*\/\s*CORE\s*THEME)?|Moral|THEME|Theme)\s*:\s*(.*?)$"),
        ]

        matched_any = False
        for key, pattern in patterns:
            match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                # Clean leading formatting like markdown bold, quotes, or dashes
                extracted = re.sub(r"^[*_\"#\-]+\s*", "", extracted)
                extracted = re.sub(r"\s*[*_\"#]+$", "", extracted)
                if extracted:
                    sections[key] = extracted
                    matched_any = True

        # If title wasn't extracted by pattern, look for first line
        if sections["title"] == "Untitled Story":
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if lines:
                first_line = lines[0]
                first_line_clean = re.sub(r"^(?:Title|#|1\.)\s*:\s*", "", first_line, flags=re.IGNORECASE).strip("#*\" ")
                if len(first_line_clean) < 150:
                    sections["title"] = first_line_clean

        # If no structured headings were matched at all (e.g. raw prose), place full text in main_plot
        if not matched_any:
            sections["main_plot"] = text.strip()

        return sections


# Global default instance
story_service = StoryService()
