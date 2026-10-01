# Module 2 submission

| | |
|---|---|
| **Branch** | `Week-2` (`main` holds Module 1 and is left unchanged) |
| **Summary** (as submitted) | `2 specs + docs; fixed PATCH-null 500 bug` |
| **Process evidence** | `docs/prompt-log.md` (every prompt of the module, in order) and the commit history of `Week-2` |

## What is submitted

| Brief item | Where |
|---|---|
| Updated `README.md`, verified on a clean clone | `README.md` |
| Docstrings across `models.py`, `api.py`, `storage.py` and `utils.py` | `backend/app/` |
| `docs/API_REFERENCE.md` | `docs/API_REFERENCE.md` |
| `.github/copilot-instructions.md` or `.continuerules` | **`CLAUDE.md`**, section *PromptLab coding standards* (see below) |
| `docs/agent-effect-note.md` | `docs/agent-effect-note.md`, with raw runs in `docs/agent-effect-runs/` |
| `specs/prompt-versions.md` | `specs/prompt-versions.md` |
| `specs/tagging-system.md` | `specs/tagging-system.md` |

**`CLAUDE.md` stands in for the agent file.** The project was carried out with Claude Code, whose
agent-instructions file is `CLAUDE.md`. The brief's five headings (*Coding standards specific to
this project*, *Preferred patterns and conventions*, *File naming conventions*, *Error handling
approach*, *Testing requirements*) are its section *PromptLab coding standards*. No
`.github/copilot-instructions.md` or `.continuerules` exists, on purpose. The effect note says the
same.

## Verification

Run on a clean clone of `Week-2` (commit `a82301d`; the specs were then corrected in `4a313d2`),
with Python 3.12.13 and the pinned `requirements.txt`:

| Check | Result |
|---|---|
| `pip install -r requirements.txt` | FastAPI 0.109.0, Pydantic 2.5.3, uvicorn 0.27.0 installed |
| `pytest tests/ -v` | 19 passed |
| `python -m pydoc backend.app.models` | Every class and function shown with its docstring |
| API reference against the routes | The same 11 endpoints in `api.py`, `docs/API_REFERENCE.md` and the README table |
| `uvicorn app.api:app` from `backend/` | `/health` returns `{"status":"healthy","version":"0.1.0"}`; `/docs` returns 200 |

## Known issues

None blocks running the app or the provided tests.

| # | Issue | Where it is recorded |
|---|---|---|
| 1 | **An empty `collection_id` is handled inconsistently.** `POST` and `PUT` store `""` without a check; `PATCH` looks it up and returns 400 (`api.py:140`, `:178`, `:229`). | `docs/API_REFERENCE.md`, *Known issues* |
| 2 | **Prompts stored with `collection_id: ""` cannot be listed by collection.** `GET /prompts?collection_id=` treats the empty value as absent (`api.py:87`). | `docs/API_REFERENCE.md`, *Known issues* |
| 3 | **`/openapi.json` still shows `PATCH`'s `title` and `content` as nullable**, although a null for either is now rejected with 422. | `CLAUDE.md`, *Known traps* |
| 4 | **Two deprecation warnings in `models.py`**: the class-based `Config` blocks and `datetime.utcnow()`. No Module 2 task covers them. | `CLAUDE.md`, *Known traps* |
| 5 | **`python main.py` does not start the server**: it passes the app object with `reload=True`, which uvicorn rejects. Start it with `uvicorn app.api:app --reload`. | `README.md` |
| 6 | **Python 3.13 is not supported** with the pinned versions: `pydantic-core` has no 3.13 wheel and its source build needs Rust. | `README.md` |
| 7 | **The development environment ran newer libraries than the pins** (FastAPI 0.141.1, Pydantic 2.13.5). Every error message quoted in the specs was re-checked on the pinned versions and is identical. | `docs/SYSTEM_MODEL.md`; prompt log, entry 189 |
| 8 | **Provided tests with known exceptions**: one accepts either 404 or 500, two use `time.sleep`, and most have no docstring. Left as provided. | `CLAUDE.md`, *Testing requirements* |
| 9 | **Eight minor spec gaps deferred to Module 3**, found by a fresh-context review of both specs (no false claims, nothing blocking). | `CLAUDE.md`, *Open decisions*; prompt log, entry 179 |
| 10 | **`Storage.update_prompt` does not check that `prompt.id` equals `prompt_id`.** Unreachable today, since `PUT` and `PATCH` copy the existing id. | `CLAUDE.md`, *Known traps* |

**Fixed in Module 2:** a `PATCH` sending `"title": null` or `"content": null` returned 500; it now
returns 422 (`reject_null` in `models.py`, commit `158eb0b`, merged into `Week-2`).
