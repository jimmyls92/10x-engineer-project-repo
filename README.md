# PromptLab

**A REST API for storing and organising AI prompts.**

PromptLab is an internal tool for AI engineers: a place to keep prompt templates, group them into
collections, and find them again. Think "Postman for prompts". A prompt has a title, a body that may
contain template variables such as `{{code}}`, an optional description, and an optional collection it
belongs to. Collections are flat named groups; a prompt belongs to at most one.

The service is a FastAPI application with **in-memory storage** — everything lives in a dictionary in
the server process and is lost when it stops. That is deliberate for now; swapping in a database is a
later module.

---

## Quick start

### Prerequisites

- **Python 3.10–3.12** (`python --version`). **Not 3.13** — the pinned `pydantic==2.5.3` publishes
  no wheel for it and the source build needs a Rust toolchain. Tested on **3.12.13**.
- **git**

Nothing else. No database, no message broker, no API keys — the service calls no external system.

### Run the API

```bash
git clone <your-repo-url>
cd 10x-engineer-project-repo/backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.api:app --reload
```

The last two commands must be run **from the `backend/` directory** — the application is imported as
`app.api`, which only resolves when `backend/` is the working directory.

> **Do not use `python main.py`.** It is the repository's original entry point and it does not start a
> server; see *Known issues* below. `uvicorn app.api:app --reload` is the working equivalent.

| What | Where |
|---|---|
| API | http://localhost:8000 |
| Interactive docs (Swagger UI) | http://localhost:8000/docs |
| Alternative docs (ReDoc) | http://localhost:8000/redoc |
| OpenAPI schema | http://localhost:8000/openapi.json |

Stop the server with `Ctrl+C`.

### Run the tests

From the same `backend/` directory, with the virtual environment active:

```bash
pytest tests/ -v
```

All tests should pass.

### Check it is alive

```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"0.1.0"}
```

---

## API endpoints

| Method | Endpoint | What it does |
|---|---|---|
| `GET` | `/health` | Service status and version |
| `GET` | `/prompts` | List prompts, newest first. Optional `?collection_id=` and `?search=` |
| `GET` | `/prompts/{id}` | Fetch one prompt; 404 if it does not exist |
| `POST` | `/prompts` | Create a prompt; 201 with the created prompt |
| `PUT` | `/prompts/{id}` | **Full** replacement — every field is taken from the body, so an omitted field is reset |
| `PATCH` | `/prompts/{id}` | **Partial** update — only the fields the body carries are changed |
| `DELETE` | `/prompts/{id}` | Delete a prompt; 204 with no body |
| `GET` | `/collections` | List all collections |
| `GET` | `/collections/{id}` | Fetch one collection; 404 if it does not exist |
| `POST` | `/collections` | Create a collection; 201 with the created collection |
| `DELETE` | `/collections/{id}` | Delete a collection and **unfile** its prompts — the prompts survive with `collection_id` cleared |

`search` matches case-insensitively against a prompt's title and description. `GET /prompts` always
sorts by creation date, newest first; it is not a client-controlled parameter.

**Status codes.** A missing addressed resource is `404`. A body that names a collection which does not
exist is `400`. A body that breaks a field constraint — an empty title, a title over 200 characters —
is `422`, produced by validation before the handler runs.

---

## Project structure

```
.
├── README.md                 # You are here
├── CLAUDE.md                 # Working protocol for this repository
├── config.yaml
│
├── backend/
│   ├── app/
│   │   ├── api.py            # FastAPI routes — every endpoint lives here
│   │   ├── models.py         # Pydantic models and request/response bodies
│   │   ├── storage.py        # In-memory storage, one module-level instance
│   │   └── utils.py          # Sorting, filtering and search helpers
│   ├── tests/
│   │   ├── conftest.py       # Fixtures; storage is cleared around every test
│   │   └── test_api.py
│   ├── main.py               # Original entry point — does not work, see Known issues
│   └── requirements.txt
│
├── docs/
│   ├── SYSTEM_MODEL.md       # How the service works, verified against the code
│   ├── prompt-log.md         # The AI-assisted working log
│   └── ai-verification-note.md
│
├── frontend/                 # Empty — Module 4
└── specs/                    # Empty — Module 2
```

---

## Known issues and limitations

- **`python main.py` does not start the server.** It passes the application object to `uvicorn.run`
  together with `reload=True`, which uvicorn accepts only for an application given as an import string.
  It prints `WARNING: You must pass the application as an import string to enable 'reload' or
  'workers'.` and exits without binding a port — on every version tested, pinned and current. The file
  is left as it stands because changing it was outside this module's scope; use
  `uvicorn app.api:app --reload` instead. The test suite cannot catch this, since it drives the app
  through `TestClient` and never runs `main.py`.
- **The supported Python range is undeclared and has an upper bound.** There is no `pyproject.toml`,
  no `python_requires` and no lock file. `pip install -r requirements.txt` fails on Python 3.13 and
  succeeds on 3.12.
- **Storage is in memory.** Restarting the server empties it. There is no persistence, no migration
  path and no backup.
- **Single process only.** The store is a plain dictionary on one module-level instance, so running
  more than one worker gives each worker its own, silently diverging data.
- **No authentication or authorisation.** Every endpoint is open, and CORS is configured to allow all
  origins.
- **No concurrency primitive.** Storage offers nothing to serialise concurrent writes; two overlapping
  updates to the same prompt can interleave.
- **Timestamps are naive UTC.** `created_at` and `updated_at` carry no timezone, and the underlying
  `datetime.utcnow()` is deprecated in recent Python versions — the test run prints deprecation
  warnings because of it.
- **`test_delete_prompt` asserts a loose status code** (`404` or `500`), so it would still pass if the
  404 behaviour regressed.
- **Dependencies are pinned but unverified.** `requirements.txt` pins six packages; Starlette is used
  directly by the CORS middleware import and is not declared, and there is no lock file.

---

## Roadmap

- **Module 1 — fix the backend.** ✅ Four bugs fixed, `PATCH /prompts/{id}` added, the codebase
  documented in `docs/SYSTEM_MODEL.md`.
- **Module 2 — documentation and specs.** Feature specifications under `specs/`, coding standards.
- **Module 3 — production readiness.** Broader test coverage, CI/CD, Docker.
- **Module 4 — frontend.** A React client under `frontend/`.
