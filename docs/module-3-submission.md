# Module 3 submission

| | |
|---|---|
| **Repository** | https://github.com/jimmyls92/10x-engineer-project-repo |
| **Branch** | `Week-3` (`main` holds Module 1 and is left unchanged; Module 2 is on `Week-2`) |
| **Summary** | `Suite 360 tests, 100% coverage; Tagging built test-first (17 red-green cycles); CI lint+tests gated at 80% (ci-gate-evidence.md); Dockerfile + compose; duplication refactor (refactor-note.md); docs realigned` |
| **Process evidence** | `docs/prompt-log.md` (every prompt of the module, in order) and the commit history of `Week-3`, never squashed |

## What is submitted

| Brief item | Where |
|---|---|
| Coverage ≥ 80%, with meaningful assertions | `backend/tests/` (`test_api.py`, `test_models.py`, `test_utils.py`, `test_storage.py`): 360 tests, 100% of `app/` |
| One spec feature implemented with visible test-first commit history (**MUST PASS**) | **Tagging System**, from `specs/tagging-system.md`. Each cycle is a commit with a failing test followed by the commit that makes it pass, from `b104be3` "Add failing tests for the prompt tags field" to `efbd01d`; the refactor commits `f24766c` and `095b90a` follow the cycles |
| `.github/workflows/ci.yml` passing on a clean clone (**MUST PASS**) | `.github/workflows/ci.yml`; latest run [37660486164](https://github.com/jimmyls92/10x-engineer-project-repo/actions/runs/37660486164) on `d93d28d` ✓ |
| `docs/ci-gate-evidence.md` showing the pipeline failing on a broken test | `docs/ci-gate-evidence.md`: runs 37490611819 ✓, 37491674238 ✗ (deliberately broken test), 37492120010 ✓ |
| `backend/Dockerfile` and `docker-compose.yml` that build and run | `backend/Dockerfile`, `backend/.dockerignore`, `docker-compose.yml`; README section *Docker usage* |
| `docs/refactor-note.md` with named smell and before/after commits | `docs/refactor-note.md`: duplication of the collection check, before `d962229`, after `6a183ec` |
| Documentation and API reference updated to match the code | `README.md` (Tagging in *Features list*, `GET /tags` in the endpoint summary, *Run the linter*, *Continuous integration*, *Docker usage*), `docs/API_REFERENCE.md` (`GET /tags` and the `tag` filter), docstrings in `backend/app/`, status lines in both specs |
| Repository link, summary and known issues | This file |

**`CLAUDE.md` is the agent-instructions file.** The project is carried out with Claude Code, so
`CLAUDE.md` stands in for `.github/copilot-instructions.md` or `.continuerules`, as in Module 2.

**Prompt Versioning is not implemented.** The brief asks for one of the two Module 2 specs; the other
is Module 4 work. `specs/prompt-versions.md` says so in its status line, and no route or test for it
exists yet.

## Verification

Run on a fresh clone of `Week-3` at `d93d28d`, with Python 3.12.13 and the pinned
`requirements.txt`:

| Check | Result |
|---|---|
| `pip install -r requirements.txt` | FastAPI 0.109.0, Pydantic 2.5.3, uvicorn 0.27.0 installed |
| `ruff check .` | All checks passed |
| `pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80` | 360 passed; coverage 100.00% |
| `docker-compose up --build` | Image built from the committed files, container up on port 8000 |
| `GET /health`, `GET /prompts`, `GET /tags` on the container | `{"status":"healthy","version":"0.1.0"}`; 200; 200 |
| CI on push | Run 37660486164 on `d93d28d` ✓ |

## Known issues

None blocks running the app or the tests.

| # | Issue | Where it is recorded |
|---|---|---|
| 1 | **An empty `collection_id` is handled inconsistently.** `POST` and `PUT` store `""` without a check; `PATCH` looks it up and returns 400 (`api.py:176`, `:213`, `:264`). The refactor kept this on purpose. | `docs/API_REFERENCE.md`, *Known issues*; `docs/refactor-note.md` |
| 2 | **Prompts stored with `collection_id: ""` cannot be listed by collection.** `GET /prompts?collection_id=` treats the empty value as absent (`api.py:115`). | `docs/API_REFERENCE.md`, *Known issues* |
| 3 | **`/openapi.json` still shows `PATCH`'s `title` and `content` as nullable**, although a null for either is rejected with 422. | `CLAUDE.md`, *Known traps* |
| 4 | **Deprecation warnings**: the class-based `Config` blocks and `datetime.utcnow()` in `models.py`. The suite passes but prints 506 warnings, most of them these. | `CLAUDE.md`, *Known traps* |
| 5 | **`python main.py` does not start the server** with the pinned uvicorn 0.27.0; it exits with code 1. Start it with `uvicorn app.api:app --reload`; Docker does the same. | `README.md`; `backend/main.py` docstring |
| 6 | **Python 3.13 is not supported** with the pinned versions: `pydantic-core` has no 3.13 wheel and its source build needs Rust. | `README.md`, *Prerequisites* |
| 7 | **The clock is coarse on Windows with Python 3.12**: two requests can share a timestamp, so tests that compare timestamps could fail rarely. Every strict comparison uses the `ticking_clock` fixture. Not measured on Linux. | `CLAUDE.md`, *Known traps*; `backend/tests/conftest.py` |
| 8 | **Ruff enforces only `E4`, `E7`, `E9` and `F`.** Ruff's wider defaults gave 81 findings, most contradicting the project's conventions. | `backend/ruff.toml`; `README.md`, *Run the linter* |
| 9 | **Provided tests left as provided**: one accepts either 404 or 500 (`test_api.py:754`), two use `time.sleep` (`:866`, `:1178`). | `CLAUDE.md`, *Testing requirements* |
| 10 | **`Storage.update_prompt` does not check that `prompt.id` equals `prompt_id`.** Unreachable today, since `PUT` and `PATCH` copy the existing id. | `CLAUDE.md`, *Known traps* |
| 11 | **`TagList` names two things in `models.py`**: the tag-list annotation (`:90`) and the `GET /tags` response model (`:298`), which replaces it at module level. Request models bind the annotation before the redefinition, so behaviour is correct. | `check_tag_list` docstring |
| 12 | **Spec findings left for Prompt Versioning** (Module 4): five gaps from the Module 2 fresh-context review of `specs/prompt-versions.md`. | `CLAUDE.md`, *Open decisions* |
