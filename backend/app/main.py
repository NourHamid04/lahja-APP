from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.dialects import DIALECTS
from app.models import HealthResponse, TransformRequest, TransformResponse
from app.services.openai_compat import APIConnectionError, APIError, AuthenticationError, RateLimitError
from app.services.openai_service import LahjaAIService
from app.services.rate_limit import InMemoryRateLimiter

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MVP API for Arabic dialect and Arabizi transformation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

rate_limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)
ai_service = LahjaAIService(settings)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"message": "Lahja API is running", "docs": "/docs"}


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        model=settings.openai_model,
        mock_mode=settings.mock_mode,
    )


@app.get("/api/dialects", tags=["dialects"])
def dialects() -> dict[str, list[dict[str, str]]]:
    return {"dialects": DIALECTS}


@app.post("/api/transform", response_model=TransformResponse, tags=["transform"])
def transform(payload: TransformRequest, request: Request) -> TransformResponse:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again in one minute.",
        )

    started = perf_counter()
    request_id = str(uuid4())

    try:
        result = ai_service.transform(payload)
    except AuthenticationError as exc:
        raise HTTPException(status_code=500, detail="The backend API key is invalid.") from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=503, detail="The AI provider rate limit was reached.") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=503, detail="Could not connect to the AI provider.") from exc
    except APIError as exc:
        raise HTTPException(status_code=502, detail="The AI provider returned an error.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    latency_ms = round((perf_counter() - started) * 1000)
    return TransformResponse(
        **result.model_dump(),
        request_id=request_id,
        model="mock" if settings.mock_mode else settings.openai_model,
        latency_ms=latency_ms,
        mock_mode=settings.mock_mode,
    )
