# Lahja MVP

A runnable basic version of **Lahja**, a website that transforms written Arabic from one dialect to another and supports Arabic script, Arabizi, and mixed Arabic/English chat text.

## Included

- Dependency-free HTML, CSS, and JavaScript frontend
- FastAPI + Python backend
- OpenAI Responses API with Pydantic structured output
- Arabic, Arabizi, and mixed-input modes
- 17 initial Arabic dialect profiles
- Arabic or Arabizi output
- Tone selection: neutral, casual, friendly, formal
- Confidence, source detection, notes, warnings, and alternatives
- Responsive dark UI with RTL-aware input and output
- Browser-local history
- Input validation, explicit CORS configuration, and MVP rate limiting
- Mock mode for UI testing without an API key
- Docker setup and backend tests

## Architecture

```text
Browser frontend (HTML/CSS/JavaScript)
        |
        | POST /api/transform
        v
FastAPI backend
  - validates input
  - applies rate limiting
  - builds dialect-specific instructions
  - keeps the API key secret
        |
        v
OpenAI Responses API
  - returns a structured Pydantic result
        |
        v
Frontend renders transformed text and metadata
```

The frontend never receives `OPENAI_API_KEY`. All AI calls go through the backend.

---

# Option A — Run locally

## 1. Install prerequisites

Install:

- Python 3.11 or newer
- An OpenAI API key for real transformations

The frontend has no npm dependencies and does not require Node.js.

## 2. Extract and open the project

```bash
cd lahja-mvp
```

## 3. Configure the backend

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS/Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `backend/.env`.

### Test without paid API calls

```env
LAHJA_MOCK_MODE=true
OPENAI_API_KEY=
```

### Test the real API

```env
LAHJA_MOCK_MODE=false
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.6-luna
```

The default model is chosen for cost-sensitive, high-volume use. You can change it later after measuring quality and cost.

## 4. Start the backend

From the `backend` directory with the virtual environment active:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify:

- Health endpoint: `http://localhost:8000/api/health`
- Interactive API docs: `http://localhost:8000/docs`

## 5. Start the frontend

Open a second terminal:

```bash
cd lahja-mvp/frontend
python -m http.server 5173
```

On some systems the command is:

```bash
python3 -m http.server 5173
```

Open `http://localhost:5173`.

## 6. Test the full connection

1. Select **Lebanese Arabic** as the source.
2. Select **Syrian Arabic** as the target.
3. Enter `mar7aba kifak shu l akhbar`.
4. Select Arabic output.
5. Press **Transform dialect**.

With mock mode enabled, the backend returns a predefined demonstration. With mock mode disabled, it calls the OpenAI API.

You can also press `Ctrl + Enter` or `Cmd + Enter` to transform.

---

# Option B — Docker

## 1. Create the backend environment file

### Windows PowerShell

```powershell
Copy-Item backend\.env.example backend\.env
```

### macOS/Linux

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and choose mock or real API mode.

## 2. Build and run

```bash
docker compose up --build
```

Open:

- Website: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

---

# Run automated tests

From `backend`, with the virtual environment active:

```bash
pytest
```

Tests force mock mode and do not use API credits.

# Important files

```text
lahja-mvp/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI routes and provider errors
│   │   ├── config.py               # .env and environment settings
│   │   ├── dialects.py             # Dialect catalog and prompt guidance
│   │   ├── models.py               # Request/response validation
│   │   └── services/
│   │       ├── openai_service.py    # OpenAI Responses API call
│   │       ├── prompt.py            # Transformation instructions
│   │       └── rate_limit.py        # Single-server MVP limiter
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html                  # Main interface
│   ├── styles.css                  # Responsive dark UI
│   ├── app.js                      # UI state and backend communication
│   ├── config.js                   # Backend URL
│   └── Dockerfile
└── docker-compose.yml
```

# API request example

```bash
curl -X POST http://localhost:8000/api/transform \
  -H "Content-Type: application/json" \
  -d '{
    "text": "mar7aba kifak shu l akhbar",
    "source_dialect": "lebanese",
    "target_dialect": "syrian",
    "input_script": "arabizi",
    "output_script": "arabic",
    "tone": "casual",
    "preserve_names": true
  }'
```

Example response shape:

```json
{
  "transformed_text": "مرحبا، كيفك؟ شو الأخبار؟",
  "detected_source_dialect": "Lebanese Arabic",
  "detected_input_script": "arabizi",
  "confidence": 0.92,
  "notes": [],
  "alternatives": [],
  "warnings": [],
  "request_id": "...",
  "model": "gpt-5.6-luna",
  "latency_ms": 850,
  "mock_mode": false
}
```

# How the AI layer works

1. The backend validates source dialect, target dialect, script, tone, and maximum length.
2. It builds controlled instructions for meaning preservation, Arabizi ambiguity, named entities, output script, tone, and target-dialect style.
3. The backend calls `client.responses.parse(...)`.
4. The model must return the `AITransformResult` Pydantic schema.
5. The frontend receives predictable JSON instead of trying to parse free-form AI text.

# Add or change dialects

Edit `backend/app/dialects.py`:

1. Add the dialect to `DIALECTS`.
2. Add guidance to `DIALECT_GUIDANCE`.
3. Restart the backend.
4. The frontend loads the updated list automatically from `/api/dialects`.

Do not add a dialect only because the model recognizes its name. Create native-speaker evaluation examples for it first.

# How to evaluate dialect quality

For each important source-target pair, build a reviewed test set containing:

- greetings and daily chat
- questions and requests
- jokes and idioms
- gender and number agreement
- names, locations, brands, links, and emojis
- Arabizi with multiple spellings
- code-switching with English or French
- formal and casual tones
- ambiguous and sensitive phrases

Have at least two native reviewers score:

- meaning preservation
- target-dialect naturalness
- regional correctness
- tone preservation
- named-entity preservation

# MVP limitations

- Arabic dialects vary by city, age, community, and context; each label represents a broad profile.
- Short text may not contain enough information for reliable source detection.
- Arabizi spelling is inconsistent and context-dependent.
- LLM output can be fluent but linguistically wrong.
- The in-memory rate limiter resets on restart and does not coordinate multiple servers. Replace it with Redis before scaling.
- History is stored only in the browser and is not synchronized across devices.
- The mock transformer is an interface demonstration, not a linguistic engine.
- Authentication, payments, analytics, moderation workflows, and a correction database are not included.
- Native-speaker evaluation is required before publishing strong accuracy claims.

# Recommended next steps

1. Add thumbs-up/down and an optional corrected version.
2. Store only consented evaluation data in PostgreSQL.
3. Add authentication and per-user quotas.
4. Replace the in-memory limiter with Redis.
5. Add an evaluation dashboard grouped by dialect pair.
6. Track latency, cost, correction rate, and repeat usage.
7. Test different prompts and models against the same reviewed dataset.
8. Build the mobile app after the website proves which user group returns regularly.

# Production security checklist

- Never commit `.env` files.
- Restrict CORS to real production domains.
- Use HTTPS.
- Add authentication and server-side quotas.
- Do not log full private messages by default.
- Add retention and deletion controls.
- Store secrets in the hosting provider's secret manager.
- Add provider error monitoring and abuse controls.
- Review privacy and data-processing obligations for launch countries.
