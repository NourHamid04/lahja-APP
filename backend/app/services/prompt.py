from app.dialects import DIALECT_GUIDANCE, DIALECT_NAMES
from app.models import TransformRequest

SYSTEM_PROMPT = """
You are Lahja, an expert Arabic dialect transformation engine.
Your job is to rewrite text from one Arabic variety into another while preserving meaning, intent, emotion, names, numbers, URLs, emojis, and relevant code-switching.

Important rules:
1. This is dialect transformation, not word-for-word translation.
2. Produce natural text that a real speaker could write in chat.
3. Do not exaggerate accents, stereotypes, or hyper-local vocabulary.
4. Do not silently change facts, names, gender references, politeness, sentiment, or intensity.
5. Arabizi may use inconsistent digit mappings (2, 3, 5, 6, 7, 8, 9). Resolve it from context instead of applying a naive character replacement.
6. For mixed Arabic/Latin text, preserve brand names, URLs, usernames, technical terms, and intentional English words.
7. If the source dialect or phrase is genuinely ambiguous, choose the most likely meaning and add a short warning.
8. Return only the fields required by the structured output schema.
9. Keep notes short and useful. Do not give long linguistic lectures.
10. Never claim perfect certainty for a short or ambiguous sentence.
""".strip()


def build_user_prompt(request: TransformRequest) -> str:
    source_name = DIALECT_NAMES.get(request.source_dialect, request.source_dialect)
    target_name = DIALECT_NAMES[request.target_dialect]
    target_guidance = DIALECT_GUIDANCE.get(request.target_dialect, "Use natural contemporary wording.")

    script_instruction = (
        "Write the final transformed text using Arabic script."
        if request.output_script == "arabic"
        else "Write the final transformed text in readable Arabizi using common Latin-letter conventions."
    )

    tone_instruction = {
        "neutral": "Keep the original level of formality unless a neutral choice is needed.",
        "casual": "Use casual everyday chat wording.",
        "friendly": "Use warm and friendly wording without changing the message.",
        "formal": "Use a polite, formal register that still belongs to the target variety.",
    }[request.tone]

    names_instruction = (
        "Preserve personal names and named entities unless transliteration is required by the selected output script."
        if request.preserve_names
        else "Names may be transliterated naturally when appropriate."
    )

    return f"""
Transform the following message.

Declared source dialect: {source_name}
Declared input script: {request.input_script}
Target dialect: {target_name}
Target-specific guidance: {target_guidance}
Output instruction: {script_instruction}
Tone instruction: {tone_instruction}
Entity instruction: {names_instruction}

User text:
---
{request.text}
---

The transformed_text field must contain only the usable transformed message, with no labels or quotation marks.
Detected source dialect should be a concise English dialect name.
""".strip()
