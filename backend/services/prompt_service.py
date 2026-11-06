"""
StoryVerse AI — Prompt Engineering Service
============================================
Creates modular, structured prompt templates for all creative writing operations.

Each template instructs the AI to:
  - Strictly write in the specified language (English, Telugu, Tamil, Hindi).
  - Embody the designated genre and emotional tone.
  - Tailor complexity for the target audience.
  - Maintain narrative consistency and avoid repetition.
  - Format output cleanly with clear section headings.
"""

from typing import Dict, Any, Optional


# ============================================================
# System Instructions
# ============================================================

SYSTEM_INSTRUCTION_CREATIVE = (
    "You are StoryVerse AI, an expert creative novelist, Hollywood screenplay writer, "
    "and master literary editor. You produce vivid, emotionally resonant, and rigorously "
    "structured literature and scripts. You strictly adhere to the requested language, "
    "genre conventions, tone, and audience maturity level without breaking character."
)


# ============================================================
# RAG Context Block Builder
# ============================================================

def build_rag_context_block(retrieved_chunks: Any) -> str:
    """
    Formats retrieved semantic knowledge chunks into a grounding block for prompt injection.
    Supports both list of chunk dictionaries and pre-formatted strings.
    """
    if not retrieved_chunks:
        return ""

    if isinstance(retrieved_chunks, str):
        return retrieved_chunks.strip()

    if not isinstance(retrieved_chunks, list):
        return ""

    lines = [
        "=== [RETRIEVED KNOWLEDGE CONTEXT — GROUND TRUTH] ===",
        "The following established worldbuilding lore, character profiles, or reference notes were retrieved from the knowledge base:",
    ]
    for idx, chunk in enumerate(retrieved_chunks, 1):
        title = chunk.get("document_title") or chunk.get("title") or "Reference Document"
        doc_type = chunk.get("doc_type") or "lore"
        score = chunk.get("similarity_score", 1.0)
        text = chunk.get("text", "").strip()
        lines.append(f'\n[Source {idx}: "{title}" | Type: {doc_type} | Relevance: {score}]')
        lines.append(text)

    lines.append("\n=== [END RETRIEVED KNOWLEDGE CONTEXT] ===")
    lines.append(
        "MANDATORY KNOWLEDGE GROUNDING INSTRUCTIONS:\n"
        "You must strictly incorporate, reference, and adhere to the facts, terminology, character traits, and worldbuilding rules established in the RETRIEVED KNOWLEDGE CONTEXT above. Do not contradict this ground truth."
    )
    return "\n".join(lines)


# ============================================================
# Prompt Builders
# ============================================================

def build_story_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a comprehensive prompt for full-length structured story generation.
    """
    topic = params.get("topic", "").strip()
    genre = params.get("genre", "Fantasy")
    language = params.get("language", "English")
    tone = params.get("tone", "Emotional")
    length = params.get("length", "Medium")
    audience = params.get("audience", "General Audience")
    character_count = params.get("character_count", 2)
    character_names = params.get("character_names")
    c_names_str = ""
    if isinstance(character_names, list) and character_names:
        c_names_str = ", ".join(str(n).strip() for n in character_names if str(n).strip())
    elif isinstance(character_names, str) and character_names.strip():
        c_names_str = character_names.strip()

    setting = params.get("setting", "").strip()
    instructions = params.get("additional_instructions", "").strip()

    word_guide = {
        "short": "approximately 600 - 900 words",
        "medium": "approximately 1,200 - 1,800 words",
        "long": "approximately 2,000 - 3,000 words"
    }.get(str(length).lower(), "approximately 1,200 - 1,800 words")

    prompt = f"""Generate an original, structured story based on the following parameters:

CORE SPECIFICATIONS:
- Premise / Topic: {topic}
- Genre: {genre}
- Language: {language} (You MUST write the ENTIRE story in {language})
- Emotional Tone: {tone}
- Target Audience: {audience}
- Desired Length: {length} ({word_guide})
- Main Characters: Approximately {character_count} primary characters
{f"- Character Names: {c_names_str}" if c_names_str else ""}
{f"- Setting / World Building: {setting}" if setting else ""}
{f"- Special Creative Instructions: {instructions}" if instructions else ""}

REQUIRED OUTPUT STRUCTURE:
Please format your response clearly using the following structured sections:
1. TITLE: An engaging, genre-appropriate title.
2. SYNOPSIS: A 2-3 sentence overview of the core narrative.
3. SETTING: World building and atmosphere description.
4. CHARACTERS: Brief descriptions of the primary characters.
5. ACT I - THE BEGINNING: Introduction to characters, ordinary world, and inciting incident.
6. ACT II - THE CONFLICT: Rising stakes, complications, obstacles, and internal struggles.
7. ACT III - THE CLIMAX: The dramatic peak where choices determine the final outcome.
8. CONCLUSION: Resolution of the central arc and character transformations.
9. MORAL / CORE THEME: The underlying thematic takeaway or resonant insight.

CRITICAL WRITING DIRECTIVES:
- Write exclusively in {language}.
- Embody the {tone} tone and {genre} genre throughout.
- Show, don't tell: use sensory descriptions and meaningful dialogue.
- Ensure narrative logic and emotional satisfaction.
"""

    rag_context = (params.get("rag_context") or "").strip()
    if rag_context:
        return f"{rag_context}\n\n{prompt.strip()}"

    return prompt.strip()


def build_script_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a prompt for generating properly formatted screenplays.
    """
    topic = params.get("topic", "").strip()
    genre = params.get("genre", "Thriller")
    language = params.get("language", "English")
    tone = params.get("tone", "Suspenseful")
    num_scenes = params.get("num_scenes", 3)
    characters = params.get("characters", "")
    if isinstance(characters, list):
        characters = ", ".join(str(c).strip() for c in characters if str(c).strip())
    elif isinstance(characters, str):
        characters = characters.strip()
    else:
        characters = ""

    setting = params.get("setting", "")
    if isinstance(setting, str):
        setting = setting.strip()
    else:
        setting = ""

    instructions = params.get("additional_instructions", "")
    if isinstance(instructions, str):
        instructions = instructions.strip()
    else:
        instructions = ""

    multilingual_notes = ""
    if language and str(language).strip().lower() != "english":
        multilingual_notes = (
            f"\nMULTILINGUAL SCREENPLAY DIRECTIVES ({str(language).upper()}):\n"
            f"- All character dialogue must be written authentically and fluently in {language}.\n"
            f"- Scene action descriptions and dramatic moments must be written in {language}.\n"
            f"- Standard industry screenplay sluglines (INT. / EXT., DAY / NIGHT) and character cue headings should be preserved in standard format, with dialogue and parentheticals in {language}.\n"
        )

    prompt = f"""Generate a professionally formatted Hollywood-style screenplay script:

SCRIPT SPECIFICATIONS:
- Premise / Logline: {topic}
- Genre: {genre}
- Language: {language} (Write action lines and dialogues in {language})
- Tone & Pacing: {tone}
- Number of Scenes: {num_scenes} distinct scenes
{f"- Character List: {characters}" if characters else ""}
{f"- Key Locations: {setting}" if setting else ""}
{f"- Special Directives: {instructions}" if instructions else ""}

INDUSTRY SCREENPLAY FORMAT RULES:
1. SCRIPT TITLE & LOGLINE: At the beginning.
2. CHARACTERS: Brief character cast list with ages and roles.
3. SCENE HEADINGS (Sluglines): In capital letters (e.g., INT. COFFEE SHOP - DAY or EXT. ROOFTOP - NIGHT).
4. ACTION BLOCKS: Present-tense visual and auditory descriptions (3 lines max per block).
5. CHARACTER CUES: Character names centered/capitalized above their spoken lines.
6. PARENTHETICALS: (whispering), (pointing gun) used sparingly when needed.
7. DIALOGUE: Spoken lines formatted directly below the character cue.
8. SCENE TRANSITIONS: (CUT TO:, FADE OUT:) between distinct scene changes.
{multilingual_notes}
CRITICAL DIRECTIVES:
- Write strictly in {language}.
- Deliver exactly {num_scenes} complete, connected dramatic scenes.
"""
    rag_context = (params.get("rag_context") or "").strip()
    if rag_context:
        return f"{rag_context}\n\n{prompt.strip()}"

    return prompt.strip()


def build_character_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a prompt for crafting a 3-dimensional, comprehensive character profile bible
    with all 19 narrative dimensions.
    """
    description = (
        params.get("description")
        or params.get("story_context")
        or params.get("concept")
        or ""
    ).strip()
    name = (params.get("character_name") or params.get("name") or "").strip()
    age = str(params.get("age") or "").strip()
    gender = (params.get("gender") or "").strip()
    genre = params.get("genre") or "Drama"
    role = params.get("character_role") or "Protagonist"
    archetype = (params.get("character_archetype") or params.get("personality_type") or params.get("archetype") or "").strip()
    background = (params.get("background") or "").strip()
    setting = (params.get("setting") or "").strip()
    language = params.get("language") or "English"
    tone = params.get("tone") or "Emotional"
    instructions = (params.get("additional_instructions") or "").strip()

    prompt = f"""Generate an in-depth, 3-dimensional psychological character profile bible:

CHARACTER SPECIFICATIONS:
- Core Concept / Premise: {description or 'Create an original dramatic character.'}
{f"- Name: {name}" if name else "- Name: Invent an evocative, genre-appropriate name."}
{f"- Age: {age}" if age else "- Age: Determine an appropriate age."}
{f"- Gender: {gender}" if gender else ""}
- Role in Narrative: {role}
{f"- Archetype / Personality Type: {archetype}" if archetype else "- Archetype: Formulate a compelling narrative archetype."}
- Story Genre: {genre}
- Tone: {tone}
- Language: {language} (Profile must be written strictly in {language})
{f"- Personal Background / Origin: {background}" if background else ""}
{f"- World / Setting: {setting}" if setting else ""}
{f"- Special Creative Directives: {instructions}" if instructions else ""}

REQUIRED OUTPUT SECTIONS:
Please format your response clearly using the following structured sections:
1. NAME: Full character name and any alias, title, or epithet.
2. AGE: Numerical age or physical life stage.
3. GENDER: Gender identity.
4. ROLE: Narrative function ({role}).
5. ARCHETYPE: Psychological or mythic archetype (e.g. Reluctant Hero, Shadow, Outlaw, Mentor).
6. PHYSICAL APPEARANCE: Face, build, posture, distinguishing scars/tattoos, clothing style, and mannerisms.
7. PERSONALITY TRAITS: 4-5 dominant behavioral traits with real-world examples.
8. PSYCHOLOGICAL PROFILE:
   - Core Want (External Goal): Conscious desire driving action.
   - Core Need (Internal Truth): Subconscious lesson required for growth.
   - The Lie They Believe: False belief about themselves or the world.
   - Fatal Flaw & Vulnerability: Psychological blindspot that threatens their ruin.
9. STRENGTHS: Key competencies, skills, and moral assets.
10. WEAKNESSES: Critical vulnerabilities and personality blindspots.
11. FATAL FLAW: The specific hubris, obsession, or trauma that threatens their ruin.
12. BACKSTORY: Formative past event or trauma that shaped their worldview.
13. MOTIVATIONS AND GOALS: Primary short-term objectives and overarching life quest.
14. FEARS: Deepest existential or situational terror.
15. SECRETS: The hidden fact or deed they dread anyone discovering.
16. RELATIONSHIPS: Key dynamics with allies, rivals, mentors, and loved ones.
17. INTERNAL CONFLICT: War waged between their desires, values, and guilt.
18. EXTERNAL CONFLICT: The outside antagonists, societal forces, or physical obstacles opposing them.
19. CHARACTER ARC: Anticipated growth trajectory from beginning to climax.
20. ROLE IN THE STORY: Specific thematic contribution and impact on the overarching plot.

Keep the numbered section labels and field names above in English exactly as written.
Write the section content in {language}; do not translate the labels.

CRITICAL WRITING DIRECTIVES:
- Write strictly in {language}.
- Embody the {genre} genre and {tone} tone.
- Make the character unique, deeply flawed, and emotionally resonant.
"""
    rag_context = (params.get("rag_context") or "").strip()
    if rag_context:
        return f"{rag_context}\n\n{prompt.strip()}"

    return prompt.strip()


def build_character_variations_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a prompt to generate multiple distinct character concepts from a premise.
    """
    premise = (
        params.get("premise")
        or params.get("story_context")
        or params.get("description")
        or ""
    ).strip()
    genre = params.get("genre", "Drama")
    role = params.get("character_role", "Characters")
    count = params.get("count", 3)
    language = params.get("language", "English")

    prompt = f"""Generate exactly {count} distinct, diverse character concepts for the following story premise:

PREMISE / CONTEXT: {premise}
GENRE: {genre}
TARGET ROLE: {role}
LANGUAGE: {language}

FORMAT EACH CONCEPT EXACTLY AS FOLLOWS:
CONCEPT 1:
NAME: [Name and title]
ROLE: [Narrative role]
ARCHETYPE: [Archetype]
LOGLINE: [1-2 sentence character hook]
CORE MOTIVATION: [What drives them]
FATAL FLAW: [Their primary weakness or blindspot]
KEY TRAIT: [Distinctive physical or psychological feature]

CONCEPT 2:
...

Ensure each concept offers a radically different perspective, conflict, and dynamic in the story. Write in {language}.
"""
    rag_context = (params.get("rag_context") or "").strip()
    if rag_context:
        return f"{rag_context}\n\n{prompt.strip()}"

    return prompt.strip()


def build_scene_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a prompt for generating a single self-contained scene.
    """
    context = params.get("context", "").strip()
    scene_goal = params.get("scene_goal", "").strip()
    genre = params.get("genre", "Drama")
    language = params.get("language", "English")
    characters = params.get("characters", "").strip()

    prompt = f"""Generate a focused, high-impact narrative scene:

SCENE CONTEXT:
- Surrounding Story Context: {context}
- Goal of this Scene: {scene_goal}
- Characters Present: {characters}
- Genre: {genre}
- Language: {language}

REQUIREMENTS:
- Open with immediate narrative momentum.
- Establish tension between opposing character motivations.
- Escalate to a turning point or decision that shifts the dynamic.
- Write the entire scene in {language}.
"""
    return prompt.strip()


def build_dialogue_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a prompt for realistic, subtext-rich dialogue exchange.
    """
    characters = params.get("characters", "Two characters")
    topic = params.get("topic", "An unresolved disagreement")
    subtext = params.get("subtext", "Hidden jealousy or unspoken affection")
    language = params.get("language", "English")
    tone = params.get("tone", "Tense")

    prompt = f"""Generate a realistic, sharp dialogue exchange:

DIALOGUE PARAMETERS:
- Characters: {characters}
- Discussion Topic: {topic}
- Underlying Subtext / Hidden Emotion: {subtext}
- Tone: {tone}
- Language: {language}

GUIDELINES:
- Avoid on-the-nose exposition; characters should speak with subtext.
- Use natural interruptions, pauses, and distinct conversational rhythms.
- Write entirely in {language}.
"""
    rag_context = (params.get("rag_context") or "").strip()
    if rag_context:
        return f"{rag_context}\n\n{prompt.strip()}"

    return prompt.strip()


def build_rewrite_prompt(content: str, style_instructions: str, language: Optional[str] = None) -> str:
    """
    Builds a prompt for rewriting existing text in a new style, tone, or perspective.
    """
    lang_clause = f"Maintain or adapt the text to {language}." if language else "Maintain the original language."
    return f"""Rewrite and elevate the following text according to the specific directives:

DIRECTIVES:
- Rewrite Instructions: {style_instructions}
- Language: {lang_clause}
- Preserve core narrative events while enhancing vocabulary, pacing, and imagery.

ORIGINAL TEXT:
\"\"\"
{content}
\"\"\"

REWRITTEN TEXT:"""


def build_expand_prompt(content: str, focus_area: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Builds a prompt to enrich and expand existing text with sensory details and depth.
    """
    focus_clause = f"Focus specifically on expanding: {focus_area}." if focus_area else "Deepen character introspection, sensory textures, and environmental atmosphere."
    lang_clause = f"Write in {language}." if language else "Keep the original language."

    return f"""Expand the following passage by approximately 1.5x to 2x its current length without introducing fluff:

EXPANSION GOALS:
- {focus_clause}
- {lang_clause}
- Ground the reader in the immediate physical world (sound, smell, temperature, texture).

EXISTING PASSAGE:
\"\"\"
{content}
\"\"\"

EXPANDED PASSAGE:"""


def build_shorten_prompt(content: str, target_reduction: str = "50%") -> str:
    """
    Builds a prompt to condense and tighten text while preserving key beats.
    """
    return f"""Condense the following passage to approximately {target_reduction} of its original length:

CONDENSATION DIRECTIVES:
- Strip redundant adjectives, filter words, and repetitive beats.
- Maximize punchiness, pace, and dramatic impact.
- Retain all crucial character decisions and plot revelations.

ORIGINAL TEXT:
\"\"\"
{content}
\"\"\"

CONCISE VERSION:"""


def build_continue_prompt(
    content: str,
    direction: Optional[str] = None,
    language: Optional[str] = None,
    rag_context: Optional[str] = None
) -> str:
    """
    Builds a prompt to seamlessly continue a story or script from where it left off.
    """
    dir_clause = f"Advance the plot toward: {direction}" if direction else "Advance naturally to the logical next complication or scene."
    lang_clause = f"Write in {language}." if language else "Maintain the exact language and voice of the original text."

    rag_block = f"{rag_context}\n\n" if rag_context else ""

    return f"""{rag_block}Continue the following passage seamlessly from its concluding sentence:

CONTINUATION DIRECTIVES:
- {dir_clause}
- {lang_clause}
- Match the established authorial voice, cadence, and tense.

CURRENT TEXT:
\"\"\"
{content}
\"\"\"

CONTINUATION:"""


def build_translate_prompt(content: str, target_language: str) -> str:
    """
    Builds a prompt for culturally nuanced literary translation.
    """
    return f"""Translate the following creative writing piece into natural, idiomatic {target_language}:

TRANSLATION DIRECTIVES:
- Target Language: {target_language}
- This is a creative literary translation, NOT a literal machine translation.
- Preserve authorial tone, poetic metaphors, emotional depth, and humor.
- Ensure natural dialogue phrasing appropriate for native speakers of {target_language}.

ORIGINAL CONTENT:
\"\"\"
{content}
\"\"\"

LITERARY TRANSLATION ({target_language.upper()}):"""


def build_summarize_prompt(content: str, summary_format: str = "bullet_points", summary_length: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Builds a prompt to summarize stories, screenplays, or text passages.
    Supports selectable lengths: short, medium, detailed, bullet_points.
    """
    length_req = summary_length or summary_format
    if length_req == "short":
        format_guide = "Provide a punchy 1-2 sentence core elevator summary."
    elif length_req == "detailed":
        format_guide = "Provide a comprehensive, multi-paragraph breakdown covering setup, conflict, turning points, and thematic resolution."
    elif length_req == "bullet_points":
        format_guide = "Provide 4-6 concise bullet points highlighting key plot developments."
    else:  # medium or default
        format_guide = "Provide a single compelling narrative paragraph capturing the essence and stakes."

    lang_clause = f"Write the summary in {language}." if language else "Maintain the language of the source text."

    return f"""Summarize the following creative writing work:

DIRECTIVES:
- Length / Style: {format_guide}
- Language: {lang_clause}

CONTENT TO SUMMARIZE:
\"\"\"
{content}
\"\"\"

SUMMARY:"""


def build_plot_twist_prompt(params: Dict[str, Any]) -> str:
    """
    Builds a prompt for generating shocking yet narratively logical plot twists.
    """
    premise = (
        params.get("premise")
        or params.get("plot")
        or params.get("context")
        or params.get("content")
        or ""
    ).strip()
    genre = params.get("genre", "Drama")
    characters = params.get("characters", "")
    tone = params.get("tone", "Suspenseful")
    language = params.get("language", "English")

    chars_clause = f"- Key Characters: {characters}" if characters else ""

    return f"""Generate 3 shocking, unexpected, yet narratively logical plot twists for the following story:

STORY PREMISE / CURRENT PLOT:
{premise}

PARAMETERS:
- Genre: {genre}
- Tone: {tone}
- Language: {language}
{chars_clause}

PLOT TWIST CRITERIA:
1. Must recontextualize earlier events without violating narrative logic (fair play).
2. Must raise emotional and dramatic stakes for the protagonist.
3. Avoid cliches (e.g. "it was all a dream").
4. Present exactly 3 distinct plot twist possibilities with:
   - Twist Title / Concept
   - The Revelation: What is unveiled.
   - The Foreshadowing: How it was secretly hinted earlier.
   - Dramatic Impact: How it forces characters to make difficult choices.

Write entirely in {language}."""
