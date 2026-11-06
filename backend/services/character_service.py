"""
StoryVerse AI — Character Service
===================================
Core business logic for generating 3-dimensional psychological character profiles,
parsing profile bibles into 19 structured narrative dimensions,
and generating character variations/concepts for story ensembles.
"""

import re
import logging
from typing import Dict, Any, List, Optional

from .ai_service import ai_service
from .prompt_service import (
    SYSTEM_INSTRUCTION_CREATIVE,
    build_character_prompt,
    build_character_variations_prompt,
)

logger = logging.getLogger(__name__)


class CharacterService:
    """
    Manages character generation workflows, structured profile bible parsing,
    and ensemble concept generation.
    """

    def __init__(self, ai_svc=None):
        self.ai = ai_svc or ai_service

    def generate_character(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a 3-dimensional character profile bible.

        Args:
            params (dict): Validated input parameters (genre, role, archetype, description, etc.)

        Returns:
            dict containing:
                - 19 structured character dimensions
                - full_profile (str)
                - metadata (dict)
        """
        retrieved_context = []
        if params.get("use_rag") or params.get("rag_query") or params.get("project_id"):
            if not params.get("rag_context"):
                try:
                    from .rag_service import rag_service
                    from .prompt_service import build_rag_context_block
                    query = params.get("rag_query") or params.get("description") or params.get("character_name") or params.get("background") or params.get("character_role") or ""
                    p_id = params.get("project_id") or params.get("rag_project_id")
                    retrieved_context = rag_service.retrieve_context(
                        query=query,
                        n_results=params.get("rag_n_results", 3),
                        project_id=p_id,
                        genre=params.get("genre"),
                        language=params.get("language")
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except Exception as e:
                    logger.warning(f"RAG retrieval skipped or failed in character generation: {e}")

        prompt = build_character_prompt(params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.75,
            max_tokens=4096
        )

        full_profile = ai_result["text"]
        sections = self.parse_character_profile(full_profile)

        # Merge metadata
        metadata = {
            "requested_name": params.get("character_name") or params.get("name"),
            "genre": params.get("genre", "Drama"),
            "character_role": params.get("character_role", "Protagonist"),
            "language": params.get("language", "English"),
            "tone": params.get("tone", "Emotional"),
            "provider": ai_result.get("provider", "unknown"),
            "model": ai_result.get("model", "default"),
            "tokens_used": ai_result.get("tokens_used"),
            "rag_applied": bool(params.get("rag_context")),
            "retrieved_chunks_count": len(retrieved_context)
        }

        return {
            **sections,
            "full_profile": full_profile,
            "retrieved_context": retrieved_context,
            "metadata": metadata
        }

    def generate_character_variations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates multiple distinct character concepts based on a story premise.

        Args:
            params (dict): Validated parameters (premise, genre, count, language, role)

        Returns:
            dict containing:
                - variations (list of concept dicts)
                - count (int)
                - full_text (str)
                - metadata (dict)
        """
        retrieved_context = []
        if params.get("use_rag") or params.get("rag_query") or params.get("project_id"):
            if not params.get("rag_context"):
                try:
                    from .rag_service import rag_service
                    from .prompt_service import build_rag_context_block
                    query = params.get("rag_query") or params.get("premise") or params.get("story_context") or ""
                    p_id = params.get("project_id") or params.get("rag_project_id")
                    retrieved_context = rag_service.retrieve_context(
                        query=query,
                        n_results=params.get("rag_n_results", 3),
                        project_id=p_id,
                        genre=params.get("genre"),
                        language=params.get("language")
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except Exception as e:
                    logger.warning(f"RAG retrieval skipped in character variations: {e}")

        prompt = build_character_variations_prompt(params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.8,
            max_tokens=3000
        )

        full_text = ai_result["text"]
        variations = self.parse_character_variations(full_text)

        metadata = {
            "premise": params.get("premise") or params.get("story_context"),
            "genre": params.get("genre", "Drama"),
            "language": params.get("language", "English"),
            "requested_count": params.get("count", 3),
            "generated_count": len(variations),
            "provider": ai_result.get("provider"),
            "model": ai_result.get("model"),
            "tokens_used": ai_result.get("tokens_used"),
            "rag_applied": bool(params.get("rag_context")),
            "retrieved_chunks_count": len(retrieved_context)
        }

        return {
            "variations": variations,
            "count": len(variations),
            "full_text": full_text,
            "retrieved_context": retrieved_context,
            "metadata": metadata
        }

    @staticmethod
    def parse_character_profile(text: str) -> Dict[str, Any]:
        """
        Parses a character profile response into 19 structured narrative sections.
        """
        sections = {
            "character_name": "Unnamed Character",
            "age": "Adult",
            "gender": "Not Specified",
            "character_role": "Protagonist",
            "character_archetype": "Hero",
            "physical_appearance": "",
            "personality_traits": "",
            "psychological_profile": "",
            "strengths": "",
            "weaknesses": "",
            "fatal_flaw": "",
            "backstory": "",
            "motivations_and_goals": "",
            "fears": "",
            "secrets": "",
            "relationships": "",
            "internal_conflict": "",
            "external_conflict": "",
            "character_arc": "",
            "role_in_story": ""
        }

        if not text or not text.strip():
            return sections

        clean_text = text.strip()

        # Regular expression patterns mapping to keys
        field_patterns = [
            ("character_name", r"(?:1\.\s*)?(?:NAME|FULL\s+NAME(?:\s*&\s*EPITHET)?|Character\s+Name)\s*:\s*(.*?)(?=\n\s*(?:2\.\s*)?(?:AGE|Age|GENDER|Gender)|$)"),
            ("age", r"(?:2\.\s*)?(?:AGE|Age)\s*:\s*(.*?)(?=\n\s*(?:3\.\s*)?(?:GENDER|Gender|ROLE|Role)|$)"),
            ("gender", r"(?:3\.\s*)?(?:GENDER|Gender)\s*:\s*(.*?)(?=\n\s*(?:4\.\s*)?(?:ROLE|Role|ARCHETYPE|Archetype)|$)"),
            ("character_role", r"(?:4\.\s*)?(?:ROLE|CHARACTER\s+ROLE|Role)\s*:\s*(.*?)(?=\n\s*(?:5\.\s*)?(?:ARCHETYPE|Archetype)|$)"),
            ("character_archetype", r"(?:5\.\s*)?(?:ARCHETYPE|CHARACTER\s+ARCHETYPE|Archetype)\s*:\s*(.*?)(?=\n\s*(?:6\.\s*)?(?:PHYSICAL\s+APPEARANCE|APPEARANCE|Appearance)|$)"),
            ("physical_appearance", r"(?:6\.\s*)?(?:PHYSICAL\s+APPEARANCE|APPEARANCE|Appearance)\s*:\s*(.*?)(?=\n\s*(?:7\.\s*)?(?:PERSONALITY\s+TRAITS|PERSONALITY|Personality)|$)"),
            ("personality_traits", r"(?:7\.\s*)?(?:PERSONALITY\s+TRAITS|PERSONALITY|Personality)\s*:\s*(.*?)(?=\n\s*(?:8\.\s*)?(?:PSYCHOLOGICAL\s+PROFILE|PSYCHOLOGY|Psychological)|$)"),
            ("psychological_profile", r"(?:8\.\s*)?(?:PSYCHOLOGICAL\s+PROFILE|PSYCHOLOGY|Psychological(?:\s+Profile)?)\s*:\s*(.*?)(?=\n\s*(?:9\.\s*)?(?:STRENGTHS|Strengths)|$)"),
            ("strengths", r"(?:9\.\s*)?(?:STRENGTHS|Strengths)\s*:\s*(.*?)(?=\n\s*(?:10\.\s*)?(?:WEAKNESSES|Weaknesses)|$)"),
            ("weaknesses", r"(?:10\.\s*)?(?:WEAKNESSES|Weaknesses)\s*:\s*(.*?)(?=\n\s*(?:11\.\s*)?(?:FATAL\s+FLAW|Fatal\s+Flaw)|$)"),
            ("fatal_flaw", r"(?:11\.\s*)?(?:FATAL\s+FLAW|Fatal\s+Flaw)\s*:\s*(.*?)(?=\n\s*(?:12\.\s*)?(?:BACKSTORY|Backstory)|$)"),
            ("backstory", r"(?:12\.\s*)?(?:BACKSTORY(?:\s*&\s*FORMATIVE\s+TRAUMA)?|Backstory)\s*:\s*(.*?)(?=\n\s*(?:13\.\s*)?(?:MOTIVATIONS\s+AND\s+GOALS|MOTIVATIONS|Motivations)|$)"),
            ("motivations_and_goals", r"(?:13\.\s*)?(?:MOTIVATIONS\s+AND\s+GOALS|MOTIVATIONS|GOALS|Motivations)\s*:\s*(.*?)(?=\n\s*(?:14\.\s*)?(?:FEARS|Fears)|$)"),
            ("fears", r"(?:14\.\s*)?(?:FEARS|Fears)\s*:\s*(.*?)(?=\n\s*(?:15\.\s*)?(?:SECRETS|Secrets)|$)"),
            ("secrets", r"(?:15\.\s*)?(?:SECRETS|Secrets)\s*:\s*(.*?)(?=\n\s*(?:16\.\s*)?(?:RELATIONSHIPS|Relationships)|$)"),
            ("relationships", r"(?:16\.\s*)?(?:RELATIONSHIPS(?:\s*&\s*DYNAMICS)?|Relationships)\s*:\s*(.*?)(?=\n\s*(?:17\.\s*)?(?:INTERNAL\s+CONFLICT|Internal\s+Conflict)|$)"),
            ("internal_conflict", r"(?:17\.\s*)?(?:INTERNAL\s+CONFLICT|Internal\s+Conflict)\s*:\s*(.*?)(?=\n\s*(?:18\.\s*)?(?:EXTERNAL\s+CONFLICT|External\s+Conflict)|$)"),
            ("external_conflict", r"(?:18\.\s*)?(?:EXTERNAL\s+CONFLICT|External\s+Conflict)\s*:\s*(.*?)(?=\n\s*(?:19\.\s*)?(?:CHARACTER\s+DEVELOPMENT\s+ARC|CHARACTER\s+ARC|Character\s+Arc)|$)"),
            ("character_arc", r"(?:19\.\s*)?(?:CHARACTER\s+DEVELOPMENT\s+ARC|CHARACTER\s+ARC|Character\s+Arc)\s*:\s*(.*?)(?=\n\s*(?:20\.\s*)?(?:ROLE\s+IN\s+THE\s+STORY|ROLE\s+IN\s+STORY|Role\s+in\s+the\s+Story)|$)"),
            ("role_in_story", r"(?:20\.\s*)?(?:ROLE\s+IN\s+THE\s+STORY|ROLE\s+IN\s+STORY|Role\s+in\s+the\s+Story)\s*:\s*(.*?)$"),
        ]

        matched_any = False
        matched_fields = set()
        for key, pattern in field_patterns:
            match = re.search(pattern, clean_text, flags=re.DOTALL | re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                val = re.sub(r"^[*_\"#\-]+\s*", "", val)
                val = re.sub(r"\s*[*_\"#]+$", "", val)
                if val:
                    sections[key] = val
                    matched_any = True
                    matched_fields.add(key)

        # Preserve structured profile data when Gemini translates section labels.
        field_order = (
            "character_name", "age", "gender", "character_role", "character_archetype",
            "physical_appearance", "personality_traits", "psychological_profile",
            "strengths", "weaknesses", "fatal_flaw", "backstory",
            "motivations_and_goals", "fears", "secrets", "relationships",
            "internal_conflict", "external_conflict", "character_arc", "role_in_story"
        )
        numbered_sections = list(re.finditer(
            r"(?m)^\s*(?:\*\*)?(\d{1,2})\s*[.)]\s*(?:\*\*)?([^:\n]{1,100}?)(?:\*\*)?\s*:\s*",
            clean_text
        ))
        for index, heading in enumerate(numbered_sections):
            section_number = int(heading.group(1))
            if not 1 <= section_number <= len(field_order):
                continue
            key = field_order[section_number - 1]
            if key in matched_fields:
                continue
            end = (
                numbered_sections[index + 1].start()
                if index + 1 < len(numbered_sections)
                else len(clean_text)
            )
            value = clean_text[heading.end():end].strip()
            if value:
                sections[key] = value
                matched_any = True
                matched_fields.add(key)

        # Fallback for Name if not matched
        if sections["character_name"] == "Unnamed Character":
            first_line = clean_text.split("\n")[0].strip()
            first_line_clean = re.sub(r"^(?:Name|Title|#|1\.)\s*:\s*", "", first_line, flags=re.IGNORECASE).strip("#*\" ")
            if len(first_line_clean) < 100:
                sections["character_name"] = first_line_clean

        # Fallback for unformatted prose
        if not matched_any:
            sections["backstory"] = clean_text

        return sections

    @staticmethod
    def parse_character_variations(text: str) -> List[Dict[str, Any]]:
        """
        Parses multi-character variations into a list of concept objects.
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        variations = []

        # Split by CONCEPT 1, CONCEPT 2, etc.
        concept_pattern = re.compile(
            r"(?:^|\n)(?:CONCEPT\s*(\d+)[\:\s\-]*)",
            re.IGNORECASE
        )

        parts = concept_pattern.split(clean_text)

        # parts typically: [preamble, '1', content1, '2', content2, ...]
        if len(parts) >= 3:
            i = 1
            while i < len(parts):
                concept_num = parts[i]
                concept_body = parts[i + 1] if i + 1 < len(parts) else ""
                i += 2

                parsed_concept = CharacterService._parse_concept_body(concept_body, concept_num)
                variations.append(parsed_concept)
        else:
            # Fallback: look for numbered list like "1. Name", "2. Name"
            numbered_splits = re.split(r"(?:^|\n)(?=\d+\.\s+)", clean_text)
            for idx, chunk in enumerate(numbered_splits):
                chunk_str = chunk.strip()
                if not chunk_str:
                    continue
                parsed_concept = CharacterService._parse_concept_body(chunk_str, str(idx + 1))
                variations.append(parsed_concept)

        # If still empty, return single concept
        if not variations:
            variations.append({
                "concept_number": 1,
                "name": "Concept 1",
                "role": "Protagonist",
                "archetype": "Character",
                "logline": clean_text[:200] + "...",
                "motivation": "",
                "fatal_flaw": "",
                "key_trait": "",
                "raw_text": clean_text
            })

        return variations

    @staticmethod
    def _parse_concept_body(body: str, concept_num: str) -> Dict[str, Any]:
        """
        Parses individual concept fields.
        """
        concept = {
            "concept_number": int(concept_num) if concept_num.isdigit() else 1,
            "name": f"Character Concept {concept_num}",
            "role": "Protagonist",
            "archetype": "Archetype",
            "logline": "",
            "motivation": "",
            "fatal_flaw": "",
            "key_trait": "",
            "raw_text": body.strip()
        }

        # Name
        name_m = re.search(r"(?:NAME|Name)\s*:\s*([^\n]+)", body, re.IGNORECASE)
        if name_m:
            concept["name"] = name_m.group(1).strip().strip("*# ")

        # Role
        role_m = re.search(r"(?:ROLE|Role)\s*:\s*([^\n]+)", body, re.IGNORECASE)
        if role_m:
            concept["role"] = role_m.group(1).strip().strip("*# ")

        # Archetype
        arch_m = re.search(r"(?:ARCHETYPE|Archetype)\s*:\s*([^\n]+)", body, re.IGNORECASE)
        if arch_m:
            concept["archetype"] = arch_m.group(1).strip().strip("*# ")

        # Logline / Hook
        log_m = re.search(r"(?:LOGLINE|HOOK|Logline|Hook)\s*:\s*(.*?)(?=\n\s*(?:CORE\s+MOTIVATION|MOTIVATION|FATAL\s+FLAW)|$)", body, re.DOTALL | re.IGNORECASE)
        if log_m:
            concept["logline"] = log_m.group(1).strip().strip("*# ")

        # Motivation
        mot_m = re.search(r"(?:CORE\s+MOTIVATION|MOTIVATION|Motivation)\s*:\s*(.*?)(?=\n\s*(?:FATAL\s+FLAW|KEY\s+TRAIT)|$)", body, re.DOTALL | re.IGNORECASE)
        if mot_m:
            concept["motivation"] = mot_m.group(1).strip().strip("*# ")

        # Fatal Flaw
        flaw_m = re.search(r"(?:FATAL\s+FLAW|FLAW|Fatal\s+Flaw)\s*:\s*(.*?)(?=\n\s*(?:KEY\s+TRAIT)|$)", body, re.DOTALL | re.IGNORECASE)
        if flaw_m:
            concept["fatal_flaw"] = flaw_m.group(1).strip().strip("*# ")

        # Key Trait
        trait_m = re.search(r"(?:KEY\s+TRAIT|TRAIT|Key\s+Trait)\s*:\s*(.*?)$", body, re.DOTALL | re.IGNORECASE)
        if trait_m:
            concept["key_trait"] = trait_m.group(1).strip().strip("*# ")

        return concept


# Global default instance
character_service = CharacterService()
