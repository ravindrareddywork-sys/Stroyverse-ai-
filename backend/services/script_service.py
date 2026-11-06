"""
StoryVerse AI — Script Service
================================
Core business logic for generating production-ready screenplays,
parsing sluglines, action blocks, character cues, dialogues, and scene transitions.
"""

import re
import logging
from typing import Dict, Any, List, Optional

from .ai_service import ai_service
from .prompt_service import (
    SYSTEM_INSTRUCTION_CREATIVE,
    build_script_prompt,
    build_scene_prompt,
)

logger = logging.getLogger(__name__)


class ScriptService:
    """
    Manages screenplay and scene generation workflows, industry-standard
    screenplay parsing, and scene structural breakdown.
    """

    def __init__(self, ai_svc=None):
        self.ai = ai_svc or ai_service

    def generate_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a complete multi-scene screenplay script.

        Args:
            params (dict): Validated input parameters (topic, genre, language, num_scenes, etc.)

        Returns:
            dict containing:
                - title (str)
                - logline (str)
                - characters_summary (str)
                - scenes (list of dicts)
                - scene_count (int)
                - full_script (str)
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
                        n_results=params.get("rag_n_results", 3),
                        project_id=p_id,
                        genre=params.get("genre"),
                        language=params.get("language")
                    )
                    if retrieved_context:
                        params["rag_context"] = build_rag_context_block(retrieved_context)
                except Exception as e:
                    logger.warning(f"RAG retrieval skipped or failed in script generation: {e}")

        prompt = build_script_prompt(params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.75,
            max_tokens=4096
        )

        full_script = ai_result["text"]
        parsed = self.parse_script_scenes(full_script)

        # Merge metadata
        metadata = {
            "topic": params.get("topic"),
            "genre": params.get("genre", "Thriller"),
            "language": params.get("language", "English"),
            "tone": params.get("tone", "Suspenseful"),
            "requested_scenes": params.get("num_scenes", 3),
            "detected_scenes": parsed.get("scene_count", len(parsed.get("scenes", []))),
            "provider": ai_result.get("provider", "unknown"),
            "model": ai_result.get("model", "default"),
            "tokens_used": ai_result.get("tokens_used"),
            "rag_applied": bool(params.get("rag_context")),
            "retrieved_chunks_count": len(retrieved_context)
        }

        return {
            "title": parsed["title"],
            "logline": parsed["logline"],
            "characters_summary": parsed["characters_summary"],
            "scenes": parsed["scenes"],
            "scene_count": len(parsed["scenes"]),
            "full_script": full_script,
            "retrieved_context": retrieved_context,
            "metadata": metadata
        }

    def generate_scene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates an individual focused dramatic scene.

        Args:
            params (dict): Validated input parameters (scene_goal/topic, context, genre, etc.)

        Returns:
            dict containing:
                - scene (dict): parsed scene details
                - full_text (str)
                - metadata (dict)
        """
        prompt = build_scene_prompt(params)
        ai_result = self.ai.call_ai_model(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION_CREATIVE,
            temperature=0.75,
            max_tokens=2048
        )

        full_text = ai_result["text"]
        parsed = self.parse_script_scenes(full_text)

        # Grab the first scene or build a single scene object
        if parsed.get("scenes"):
            scene_obj = parsed["scenes"][0]
        else:
            scene_obj = {
                "scene_number": 1,
                "heading": "SCENE 1",
                "action": full_text,
                "dialogues": [],
                "transition": "",
                "raw_text": full_text
            }

        metadata = {
            "scene_goal": params.get("scene_goal") or params.get("topic"),
            "genre": params.get("genre", "Drama"),
            "language": params.get("language", "English"),
            "provider": ai_result.get("provider"),
            "model": ai_result.get("model"),
            "tokens_used": ai_result.get("tokens_used")
        }

        return {
            "scene": scene_obj,
            "full_text": full_text,
            "metadata": metadata
        }

    @staticmethod
    def parse_script_scenes(text: str) -> Dict[str, Any]:
        """
        Intelligently parses screenplay text into structured metadata and scenes.

        Screenplay syntax recognized:
        - SCRIPT TITLE / TITLE:
        - LOGLINE:
        - CHARACTERS:
        - Sluglines: INT., EXT., INT./EXT., I/E.
        - Action paragraphs
        - Character cues (ALL CAPS, short lines)
        - Parentheticals: (whispering)
        - Dialogue blocks
        - Transitions: CUT TO:, FADE OUT:, etc.
        """
        result = {
            "title": "Untitled Screenplay",
            "logline": "",
            "characters_summary": "",
            "scenes": [],
            "scene_count": 0
        }

        if not text or not text.strip():
            return result

        clean_text = text.strip()

        # 1. Extract Title
        title_match = re.search(
            r"(?:(?:SCRIPT\s+)?TITLE|Title)\s*:\s*([^\n]+)",
            clean_text,
            re.IGNORECASE
        )
        if title_match:
            result["title"] = title_match.group(1).strip().strip("*\"# ")
        else:
            first_line = clean_text.split("\n")[0].strip()
            first_line_clean = re.sub(r"^[#*\-\s]+", "", first_line).strip("*\" ")
            if len(first_line_clean) < 100 and not first_line_clean.upper().startswith(("INT.", "EXT.", "SCENE")):
                result["title"] = first_line_clean

        # 2. Extract Logline
        logline_match = re.search(
            r"(?:LOGLINE|Logline|PREMISE|Premise)\s*:\s*(.*?)(?=\n\s*(?:CHARACTERS|SCENE|INT\.|EXT\.)|\Z)",
            clean_text,
            re.IGNORECASE | re.DOTALL
        )
        if logline_match:
            result["logline"] = logline_match.group(1).strip()

        # 3. Extract Characters Summary
        chars_match = re.search(
            r"(?:CHARACTERS|CAST\s+LIST|Characters)\s*:\s*(.*?)(?=\n\s*(?:SCENE\s*\d+|INT\.|EXT\.)|\Z)",
            clean_text,
            re.IGNORECASE | re.DOTALL
        )
        if chars_match:
            result["characters_summary"] = chars_match.group(1).strip()

        # 4. Split and Parse Scenes
        # Look for sluglines: INT., EXT., INT./EXT., I/E. or SCENE X headers
        slugline_pattern = re.compile(
            r"(?:^|\n)(?=(?:SCENE\s*\d+[\s\:\-]+)?(?:INT\.|EXT\.|INT\.\/EXT\.|I\/E\.)\s+[^\n]+)",
            re.IGNORECASE
        )

        parts = slugline_pattern.split(clean_text)

        scenes_list: List[Dict[str, Any]] = []
        scene_counter = 1

        for part in parts:
            part_str = part.strip()
            if not part_str:
                continue

            # Check if this part contains a slugline
            header_match = re.search(
                r"(?:SCENE\s*(\d+)[\s\:\-]+)?((?:INT\.|EXT\.|INT\.\/EXT\.|I\/E\.)\s+[^\n]+)",
                part_str,
                re.IGNORECASE
            )

            if header_match:
                slugline = header_match.group(2).strip()
                scene_num = int(header_match.group(1)) if header_match.group(1) else scene_counter
                scene_counter += 1

                # Body text after slugline
                body_start = header_match.end()
                body_text = part_str[body_start:].strip()

                # Parse action, dialogues, transitions from body_text
                scene_elements = ScriptService._parse_scene_body(body_text)

                scenes_list.append({
                    "scene_number": scene_num,
                    "heading": slugline.upper(),
                    "action": scene_elements["action"],
                    "dialogues": scene_elements["dialogues"],
                    "transition": scene_elements["transition"],
                    "raw_text": part_str
                })

        # If no standard sluglines were found, fallback to SCENE headings or chunking
        if not scenes_list:
            scene_header_pattern = re.compile(r"(?:^|\n)(?=SCENE\s*\d+)", re.IGNORECASE)
            scene_parts = scene_header_pattern.split(clean_text)
            for part in scene_parts:
                part_str = part.strip()
                if not part_str or part_str.startswith(("TITLE:", "Title:", "LOGLINE:", "CHARACTERS:")):
                    continue

                sh_match = re.search(r"SCENE\s*(\d+)[\:\s\-]*(.*?)(?=\n|$)", part_str, re.IGNORECASE)
                if sh_match:
                    s_num = int(sh_match.group(1))
                    heading = f"SCENE {s_num}"
                    if sh_match.group(2).strip():
                        heading += f" - {sh_match.group(2).strip()}"
                    body = part_str[sh_match.end():].strip()
                    elem = ScriptService._parse_scene_body(body)
                    scenes_list.append({
                        "scene_number": s_num,
                        "heading": heading,
                        "action": elem["action"],
                        "dialogues": elem["dialogues"],
                        "transition": elem["transition"],
                        "raw_text": part_str
                    })

        # Ultimate fallback: return 1 scene with entire body
        if not scenes_list:
            scenes_list.append({
                "scene_number": 1,
                "heading": "SCENE 1 - OPENING",
                "action": clean_text,
                "dialogues": [],
                "transition": "",
                "raw_text": clean_text
            })

        result["scenes"] = scenes_list
        result["scene_count"] = len(scenes_list)
        return result

    @staticmethod
    def _parse_scene_body(body_text: str) -> Dict[str, Any]:
        """
        Parses action paragraphs, character dialogues, and transitions within a scene.
        """
        lines = [line.rstrip() for line in body_text.split("\n")]
        action_paragraphs = []
        dialogues = []
        transition = ""

        current_action = []
        i = 0
        n = len(lines)

        transition_pattern = re.compile(
            r"^(CUT TO:|FADE OUT\.|FADE IN:|DISSOLVE TO:|SMASH CUT TO:|MATCH CUT TO:|FADE TO BLACK\.?)$",
            re.IGNORECASE
        )

        while i < n:
            line = lines[i].strip()

            if not line:
                if current_action:
                    action_paragraphs.append(" ".join(current_action))
                    current_action = []
                i += 1
                continue

            # Check transition at end
            if transition_pattern.match(line):
                transition = line
                i += 1
                continue

            # Check for character cue:
            # 1. Standard Latin ALL CAPS cue: "RAMESH" (len <= 35)
            # 2. Cue with colon: "RAMESH:" or Indic native cue "విక్రమ్:" / "விக்ரம்:" / "विक्रम:" (len <= 35)
            has_colon_cue = (
                line.endswith(":")
                and len(line) <= 35
                and not line.startswith(("INT.", "EXT.", "CUT TO", "FADE OUT", "SCENE", "NOTE", "LOGLINE", "TITLE", "CAST", "ACTION"))
                and i + 1 < n
                and bool(lines[i + 1].strip())
            )
            standard_caps_cue = (
                line.isupper()
                and len(line) <= 35
                and not line.startswith(("INT.", "EXT.", "CUT TO", "FADE OUT", "SCENE"))
                and i + 1 < n
                and bool(lines[i + 1].strip())
            )
            is_char_cue = has_colon_cue or standard_caps_cue

            if is_char_cue:
                if current_action:
                    action_paragraphs.append(" ".join(current_action))
                    current_action = []

                char_name = line.rstrip(":").strip()
                parenthetical = ""
                spoken_lines = []

                i += 1
                # Check parenthetical: (whispering), (smiling)
                if i < n and lines[i].strip().startswith("(") and lines[i].strip().endswith(")"):
                    parenthetical = lines[i].strip()
                    i += 1

                # Collect spoken dialogue lines
                while i < n and lines[i].strip():
                    next_line = lines[i].strip()
                    next_is_colon = (
                        next_line.endswith(":")
                        and len(next_line) <= 35
                        and not next_line.startswith(("INT.", "EXT.", "CUT TO", "FADE OUT", "SCENE"))
                    )
                    next_is_caps = (
                        next_line.isupper()
                        and len(next_line) <= 35
                        and not next_line.startswith(("INT.", "EXT.", "CUT TO", "FADE OUT", "SCENE"))
                    )
                    if transition_pattern.match(next_line) or next_is_colon or next_is_caps:
                        break
                    spoken_lines.append(next_line)
                    i += 1

                dialogues.append({
                    "character": char_name,
                    "parenthetical": parenthetical,
                    "line": " ".join(spoken_lines)
                })
            else:
                current_action.append(line)
                i += 1

        if current_action:
            action_paragraphs.append(" ".join(current_action))

        return {
            "action": "\n\n".join(action_paragraphs),
            "dialogues": dialogues,
            "transition": transition
        }


# Global default instance
script_service = ScriptService()
