# PromptLab — System Model

A description of the system as the code actually implements it. Every behavioural claim below is
tied to the file and line it was read from, so it can be checked rather than trusted.

Line references are to the repository state at the time of writing; paths are relative to `backend/`.

> **Status.** Written stage by stage as the exploration proceeds. Section headings follow the module
> brief's own checklist. Still to come: Entry points, Data flow, Models and relationships, Storage
> layer, External dependencies.

---

## 1. Architecture

### 1.1 What PromptLab is

PromptLab is a **catalogue for reusable AI prompt templates**. The domain object is a *prompt*: a
named, reusable piece of text intended to be sent to a language model, kept so that it can be found
and reused rather than rewritten. A *collection* is a folder over prompts. The service's job is
store → organise → find → retrieve.

The application names itself as such — `title="PromptLab API"`,
`description="AI Prompt Engineering Platform"` (`app/api.py:19-20`). The `Prompt` entity is shaped
for reuse rather than for conversation: `title` (how it is found), `content` (the template text),
`description` (what it is for) and `collection_id` (where it is filed) — `app/models.py:20-23`.
Organisation is the feature set: filtering by collection and free-text search over title and
description (`app/utils.py:17-27`), both reachable as query parameters on the prompt listing
(`app/api.py:44-56`). Prompt content is intended to carry `{{variable_name}}` placeholders —
`extract_variables` parses exactly that format (`app/utils.py:43-50`), and the test fixture is of that
shape: `"Review the following code and provide feedback:\n\n{{code}}"` (`tests/conftest.py:28`).

Technically it is a **FastAPI JSON REST backend and nothing else**. There is no frontend, no
database, no authentication and no configuration layer anywhere in the repository; all state is held
in process memory. It runs as a single process with a single entrypoint (`main.py:6-10`).

Two negative findings matter as much as the positive ones, because a description that omits them
would overstate the system:

- **PromptLab never calls a language model.** It has no dependency that could — the full dependency
  list is fastapi, uvicorn, pydantic, pytest, pytest-cov and httpx (`requirements.txt:1-6`). It
  stores prompt text; it does not execute it.
- **The templating is declared but not implemented.** `extract_variables` (`app/utils.py:43-50`) and
  `validate_prompt_content` (`app/utils.py:30-40`) are defined and referenced by nothing — no route
  handler, no model validator. The documented domain is therefore richer than the implemented one.

### 1.2 Components

Five runtime units. Test and packaging files are excluded: they are part of the repository, not of
the system being described.

| Unit | Job | Size |
|---|---|---|
| `main.py` | Process entrypoint. Imports the app and hands it to uvicorn on port 8000 (`main.py:7,10`). Holds no logic. | 10 |
| `app/models.py` | Schema and contract layer. Defines the data, its validation rules, and the id/timestamp factories (`generate_id` `app/models.py:9`, `get_current_time` `app/models.py:13`). | 76 |
| `app/storage.py` | Persistence. A `Storage` class wrapping two dictionaries (`app/storage.py:11-14`), exposed as one module-level instance (`app/storage.py:69`). | 69 |
| `app/utils.py` | Stateless helper functions over `List[Prompt]`: sort, filter, search (`app/utils.py:7,17,21`). Two further helpers are defined but unreferenced (`app/utils.py:30,43`). | 50 |
| `app/api.py` | HTTP layer. Creates the FastAPI app (`app/api.py:18-22`), configures CORS (`app/api.py:25-31`), defines every route handler, and orchestrates the other three modules. | 160 |

**The model layer divides into three families**, which is the spine of the API contract:

- **Domain entities** — `Prompt` (`app/models.py:34`), `Collection` (`app/models.py:54`). These carry
  the server-generated fields: `id`, `created_at`, and for prompts `updated_at`
  (`app/models.py:35-37`, `55-56`).
- **Request DTOs** — `PromptCreate` (`app/models.py:26`), `PromptUpdate` (`app/models.py:30`),
  `CollectionCreate` (`app/models.py:50`). Each inherits from a `*Base` class and adds nothing, so the
  client-supplied fields are exactly the base fields.
- **Response envelopes** — `PromptList` (`app/models.py:64`), `CollectionList` (`app/models.py:69`),
  `HealthResponse` (`app/models.py:74`).

**All input validation is declarative and lives only here**, as Pydantic `Field` constraints —
`title` 1–200 characters, `content` non-empty, `description` at most 500 (`app/models.py:20-22`);
collection `name` 1–100 characters (`app/models.py:46-47`). No route handler performs field
validation of its own.

### 1.3 How the components fit together

```
main.py ──► app.api ──┬──► app.storage ──► app.models
                      ├──► app.utils   ──► app.models
                      └──► app.models
```

The direction is taken from the import statements themselves, not inferred from naming:

- `app/api.py:7-15` imports all three internal modules — `models`, `storage`, `utils`.
- `app/storage.py:8` imports only `app.models`.
- `app/utils.py:4` imports only `app.models`.
- `app/models.py:3-6` imports nothing internal — standard library and pydantic only.

`app.models` is therefore the **leaf** that every other module depends on, dependencies point one
way, and there are **no cycles and no back edges**.

**Where the weight is.** `app/api.py` is the largest file at 160 lines and the only module that
imports more than one other internal module, which makes it the single coupling hub: all
orchestration and all business logic pass through it. `models.py` (76), `storage.py` (69) and
`utils.py` (50) are each small and independently readable. This shapes the exploration that follows —
`api.py` warrants deep, file-level attention, while the other three can be confirmed quickly.

### 1.4 Architectural characteristics

The system presents as three tiers — HTTP, storage, models — but it is not a cleanly layered
architecture. Four observations, each verifiable:

1. **There is no service layer.** Business rules live directly in the route handlers. The check that
   a referenced collection exists before a prompt is attached to it is performed inside the HTTP
   handler (`app/api.py:80-83`), not in a domain module.
2. **Storage is a concrete global, not an abstraction.** `app/storage.py:69` instantiates
   `storage = Storage()` at import time, and `app/api.py:13` imports *that instance* rather than the
   class. There is no interface and no dependency injection, so there is no seam at which the
   implementation could be substituted. The consequence is visible in the test setup, which reaches
   around the API to mutate the same global directly (`tests/conftest.py:6,18`).
3. **A single flat route module.** Every route is defined in `app/api.py`, with no `APIRouter` and no
   per-resource modules; grouping is by comment banner only (`app/api.py:34,41,127`).
4. **CORS is fully open.** All origins, methods and headers are permitted, with credentials allowed
   (`app/api.py:25-31`). This is the only middleware configured.

---

## Context Strategy

Required by C1.2. One row per exploration stage, recording the context level actually used and the
reason for it. This table matches `docs/prompt-log.md` — the rationale below is the reason given
before the reading was done, not one composed afterwards.

| Stage | Subject | Context level | Reason |
|---|---|---|---|
| 1 | Architecture (§1) | **Whole-repo** — every file under `backend/`, full contents | Size. The entire backend is 587 lines of Python across seven source files and two test files, so loading all of it is cheap and removes the guesswork about which module is central. The alternatives considered were structure-only (file tree and line counts) and imports-only; both were rejected because they would have made the dependency-direction claims in §1.3 inferences from filenames rather than facts read from the source, and C1.1 fails a model whose claims contradict the code. Breadth is correct here *because* the repository is small; the same choice would be wrong at a larger scale. |

Stages 2–6 to follow.
