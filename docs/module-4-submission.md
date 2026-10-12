# Module 4 submission

| | |
|---|---|
| **Repository** | https://github.com/jimmyls92/10x-engineer-project-repo |
| **Branch** | `Week-4` (`main` holds Module 1 and is left unchanged; Module 3 is on `Week-3`, Module 2 on `Week-2`) |
| **Summary** | `React web app (Prompts, Collections) on the real API; Prompt Versioning built test-first, first passing endpoint 20 min 49 s after the first red commit; suite 418 passed, 100% coverage, locally and inside the deployed API service; one-command container deployment (docs/deployment.md)` |
| **Process evidence** | `docs/prompt-log.md` (every prompt of the module, in order) and the commit history of `Week-4`, never squashed |

## What is submitted

| Brief item | Where |
|---|---|
| `specs/frontend.md` | `specs/frontend.md` (`d35e641`): scope set by C3.3's journeys, two screens, component tree, API mapping, state, loading/error/empty behaviour, folder principle |
| Second spec feature implemented test-first, suite green against deployed config | **Prompt Versioning**, from `specs/prompt-versions.md`: `GET /prompts/{id}/versions` (`order`, `limit`) and `GET /prompts/{id}/versions/{version}`; `POST` saves version 1, `PUT`/`PATCH` save one on each content change. Every group was committed red before its code: `63dc14c` → `d7f764e`, `c24cc36` → `1018d92`, `e57b633` → `034b75d`, `9e731d7` → `52a1764`. The suite passes inside the deployed API service, as `docs/deployment.md` (*Run the tests against the deployed configuration*) shows how to repeat |
| Commit timestamps showing the 4-hour increment | First failing test `63dc14c`, 2026-10-12 12:23:09 +0200; first passing endpoint **complete against its spec** `034b75d`, 12:43:58 +0200: **20 min 49 s**. The clock was counted as stopped only when the list endpoint met its whole spec, not at its first green (`d7f764e`, 12:33:31), to avoid "committing unfinished work to hit the time" |
| React frontend matching the spec, with unused scaffolding removed | `frontend/src/`: the Vite scaffold `30aaac1` was replaced by the spec's skeleton in `85053b6` (template files removed), then `131a3f0` API layer, `ed3d586` shared components, `b5cea5c` Prompts, `58a31bf` Collections |
| All CRUD operations working against the real backend (**MUST PASS**) | Checked by hand in the browser against the local backend (Task 4.6, log entries 67-70) and against the deployed containers (Task 4.8, entries 78-79); the API calls go through `frontend/src/api/` only |
| Loading, error and empty states handled | Built in Task 4.4 and checked in Task 4.7 (entries 71-73), together with form validation, mobile width and keyboard use; "Can't reach the server" checked with the backend stopped |
| Deployed application plus `docs/deployment.md` | `docker-compose.deploy.yml`, `backend/Dockerfile`, `frontend/Dockerfile`; `docs/deployment.md` lists every step, both environment variables (`CORS_ORIGINS`, `VITE_API_BASE_URL`) and how secrets are handled (there are none). Runnable by one documented container command; not hosted publicly |
| Repository link, summary and known issues | This file |

**`CLAUDE.md` is the agent-instructions file.** The project is carried out with Claude Code, so
`CLAUDE.md` stands in for `.github/copilot-instructions.md` or `.continuerules`, as in Modules 2
and 3.

**`python main.py` now starts the server.** The brief's verification runs it; with the pinned
uvicorn it used to exit with code 1. It was fixed test-first in this module (`1c1b521` →
`d5468c7`).

## Verification

Run on a fresh clone of `Week-4`, with Python 3.12.13, the pinned `requirements.txt` (FastAPI
0.109.0, Pydantic 2.5.3, uvicorn 0.27.0) and Node 24, on Windows with Git Bash and Docker Desktop.
The first clone was at `3540325`; `69dc5ba` only adds `main.py` to the image and fixes the docs, so
the backend and deployment checks were repeated on a second fresh clone at `69dc5ba`.

| Check | Result |
|---|---|
| `ruff check .` | All checks passed |
| `pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80` | 418 passed; coverage 100.00% |
| Terminal 1: `cd backend && python main.py` | Server up on port 8000; `GET /health` → `{"status":"healthy","version":"0.1.0"}` |
| Terminal 2: `cd frontend && npm install && npm run dev` | 0 vulnerabilities; the app served on http://localhost:5173 (200). `npm run lint` exit 0 |
| API calls with the web app's `Origin: http://localhost:5173` | A collection and a prompt created; content `PATCH` 200; search 200 with `access-control-allow-origin: http://localhost:5173`; the edit gave 2 versions; both deletes 204 |
| `docker compose -f docker-compose.deploy.yml up --build` | API `/health` healthy; the app on http://localhost:8080 (200); CORS allows `http://localhost:8080` |
| Suite inside the deployed API service, as written in `docs/deployment.md` | 418 passed |
| CI on push | Runs on every push of `Week-4`; last run before this note: [38245027581](https://github.com/jimmyls92/10x-engineer-project-repo/actions/runs/38245027581) on `0abe927` ✓ |

## Known issues

None blocks running the app or the tests.

| # | Issue | Where it is recorded |
|---|---|---|
| 1 | **The app is not hosted publicly.** It runs from one documented container command on any machine with Docker, as the brief allows. | `docs/deployment.md` |
| 2 | **Tags and versions are not shown in the web app.** The spec scopes the frontend to C3.3's journeys; both work through the API, and editing a prompt in the web app keeps its tags. | `specs/frontend.md`, *Out of scope* |
| 3 | **If port 5173 is taken, the dev app cannot reach the API.** Vite picks another port, which `CORS_ORIGINS` does not allow by default; free the port or add the address. | `README.md`, *Quick start guide* |
| 4 | **The deployed-config test command was run on Windows (Git Bash) only.** The plain form for Linux and macOS differs only in the path and was not run there. | `docs/deployment.md` |
| 5 | **An empty `collection_id` is handled inconsistently.** `POST` and `PUT` store `""` without a check; `PATCH` looks it up and returns 400 (`api.py:184`, `:228`, `:283`). | `docs/API_REFERENCE.md`, *Known issues* |
| 6 | **Prompts stored with `collection_id: ""` cannot be listed by collection.** `GET /prompts?collection_id=` treats the empty value as absent (`api.py:121`). | `docs/API_REFERENCE.md`, *Known issues* |
| 7 | **`/openapi.json` still shows `PATCH`'s `title` and `content` as nullable**, although a null for either is rejected with 422. | `CLAUDE.md`, *Known traps* |
| 8 | **Deprecation warnings**: the class-based `Config` blocks and `datetime.utcnow()` in `models.py`. The suite passes but prints 617 warnings, most of them these. | `CLAUDE.md`, *Known traps* |
| 9 | **Python 3.13 is not supported** with the pinned versions: `pydantic-core` has no 3.13 wheel and its source build needs Rust. | `README.md`, *Prerequisites* |
| 10 | **The clock is coarse on Windows with Python 3.12**: two requests can share a timestamp. Every strict comparison uses the `ticking_clock` fixture. Not measured on Linux. | `CLAUDE.md`, *Known traps*; `backend/tests/conftest.py` |
| 11 | **Ruff enforces only `E4`, `E7`, `E9` and `F`.** Ruff's wider defaults contradict the project's conventions. | `backend/ruff.toml`; `README.md`, *Run the linter* |
| 12 | **Provided tests left as provided**: one accepts either 404 or 500 (`test_api.py:836`), two use `time.sleep` (`:948`, `:1260`). | `CLAUDE.md`, *Testing requirements* |
| 13 | **`Storage.update_prompt` does not check that `prompt.id` equals `prompt_id`.** Unreachable today, since `PUT` and `PATCH` copy the existing id. | `CLAUDE.md`, *Known traps* |
| 14 | **`TagList` names two things in `models.py`**: the tag-list annotation (`:90`) and the `GET /tags` response model (`:326`). Request models bind the annotation first, so behaviour is correct. | `check_tag_list` docstring |
