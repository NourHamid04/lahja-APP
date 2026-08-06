from app.config import Settings
from app.dialects import DIALECT_NAMES
from app.models import AITransformResult, TransformRequest
from app.services.openai_compat import OPENAI_SDK_AVAILABLE, OpenAI
from app.services.prompt import SYSTEM_PROMPT, build_user_prompt


class LahjaAIService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            OpenAI(api_key=settings.openai_api_key)
            if OPENAI_SDK_AVAILABLE and OpenAI is not None and settings.openai_api_key
            else None
        )

    def transform(self, request: TransformRequest) -> AITransformResult:
        if self.settings.mock_mode:
            return self._mock_transform(request)

        if not OPENAI_SDK_AVAILABLE:
            raise RuntimeError("The OpenAI Python SDK is not installed. Run: pip install -r requirements.txt")

        if not self.client:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Add it to backend/.env or enable LAHJA_MOCK_MODE=true."
            )

        response = self.client.responses.parse(
            model=self.settings.openai_model,
            reasoning={"effort": "low"},
            input=[
                {"role": "developer", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(request)},
            ],
            text_format=AITransformResult,
        )

        if response.output_parsed is None:
            raise RuntimeError("The model returned no structured result.")
        return response.output_parsed

    @staticmethod
    def _mock_transform(request: TransformRequest) -> AITransformResult:
        examples = {
            ("lebanese", "syrian", "مرحبا كيفك شو الأخبار؟"): "مرحبا، كيفك؟ شو الأخبار؟",
            ("lebanese", "syrian", "mar7aba kifak shu l akhbar"): "مرحبا، كيفك؟ شو الأخبار؟",
            ("egyptian", "lebanese", "عامل ايه النهارده؟"): "كيفك اليوم؟",
            ("msa", "egyptian", "كيف حالك اليوم؟"): "عامل إيه النهارده؟",
        }
        transformed = examples.get(
            (request.source_dialect, request.target_dialect, request.text),
            f"[Mock {DIALECT_NAMES[request.target_dialect]}] {request.text}",
        )
        return AITransformResult(
            transformed_text=transformed,
            detected_source_dialect=DIALECT_NAMES.get(request.source_dialect, "Unknown Arabic variety"),
            detected_input_script="arabizi" if any(char.isascii() and char.isalpha() for char in request.text) else "arabic",
            confidence=0.55,
            notes=["Mock mode is enabled; this result is for interface testing only."],
            alternatives=[],
            warnings=["Add an OpenAI API key and disable mock mode for AI transformation."],
        )
