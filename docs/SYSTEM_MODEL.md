# PromptLab — System Model

A description of the system as the code actually implements it. Every behavioural claim below is
tied to the file and line it was read from, so it can be checked rather than trusted.

Line references are to the repository state at the time of writing; paths are relative to `backend/`.

> **Status.** Written stage by stage as the exploration proceeds. Section headings follow the module
> brief's own checklist. Still to come: Data flow, Models and relationships, Storage layer, External
> dependencies.

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

## 2. Entry points

Every route the application exposes. All of them are declared in `app/api.py` with plain `@app.<verb>`
decorators — there is no `APIRouter` and no prefix, so the paths below are the complete URLs. Grouping
is by comment banner only: Health (`app/api.py:34`), Prompt Endpoints (`app/api.py:41`), Collection
Endpoints (`app/api.py:127`).

### 2.1 The route table

Ten declared routes. "Behaviour" describes what the code does today, including where that is
defective; §2.3 says which of those are known defects and which task owns each.

| # | Method & path | Success | Input | Response model | Behaviour |
|---|---|---|---|---|---|
| 1 | `GET /health` | 200 | — | `HealthResponse` | Returns `status="healthy"` and the package version (`app/api.py:36-38`). Touches no storage, so it reports that the process is up, not that it is serving data correctly. |
| 2 | `GET /prompts` | 200 | Query: `collection_id`, `search` — both `Optional[str]`, both default `None` (`app/api.py:44-47`) | `PromptList` | Reads all prompts (`:48`), then applies filter → search → sort in that fixed order (`:51-60`). `total` is `len(prompts)` **after** filtering, not the size of the store (`:62`). |
| 3 | `GET /prompts/{prompt_id}` | 200 | Path id | `Prompt` | Fetches, then evaluates `prompt.id` (`:70-73`). On a hit it returns the prompt. On a miss `storage.get_prompt` returns `None` and the attribute access raises `AttributeError`, which leaves the handler as a **500**. No `else` branch, so a falsy `.id` would return `None` against `response_model=Prompt`. |
| 4 | `POST /prompts` | 201 | Body `PromptCreate` | `Prompt` | If `collection_id` is supplied, verifies the collection exists and raises **400** (not 404) when it does not (`:80-83`). Builds `Prompt(**prompt_data.model_dump())` (`:85`), so `id`, `created_at` and `updated_at` all come from the model defaults, never from the client. |
| 5 | `PUT /prompts/{prompt_id}` | 200 | Path id, body `PromptUpdate` | `Prompt` | 404 if the prompt is absent (`:91-93`); the same 400-on-unknown-collection check as route 4 (`:96-99`). Does not mutate the stored object — constructs a new `Prompt` field by field (`:103-111`), carrying `id` and `created_at` across from the existing record and re-using its `updated_at` unchanged. Returns `storage.update_prompt(...)` directly (`:113`). |
| 6 | `DELETE /prompts/{prompt_id}` | 204 | Path id | — | Branches on the boolean from `storage.delete_prompt`; 404 when false, otherwise returns `None` with an empty body (`:120-124`). |
| 7 | `GET /collections` | 200 | — | `CollectionList` | Returns every collection with `total=len(collections)` (`:129-132`). No filtering, no search, no sorting — deliberately thinner than route 2. |
| 8 | `GET /collections/{collection_id}` | 200 | Path id | `Collection` | Fetch, 404 if absent, return (`:135-140`). |
| 9 | `POST /collections` | 201 | Body `CollectionCreate` | `Collection` | Stores the collection (`:143-146`). No validation beyond the declarative `Field` constraints on the model; unlike route 4 there is no cross-entity check to make. |
| 10 | `DELETE /collections/{collection_id}` | 204 | Path id | — | 404 when the collection is absent, otherwise deletes it and returns `None` (`:149-160`). Deletes only the collection: no pass is made over the prompts that reference it. |

There is no `PATCH` on either resource. See §2.3.4.

### 2.2 Routes not declared in the source

Three further endpoints are served without appearing in `app/api.py`, contributed by FastAPI from the
app object created at `app/api.py:18-22`:

| Path | What it serves |
|---|---|
| `/openapi.json` | The generated OpenAPI schema, titled `PromptLab API`, described `AI Prompt Engineering Platform`, versioned from `app.__version__`. |
| `/docs` | Swagger UI over that schema. |
| `/redoc` | ReDoc over the same schema. |

They are part of the exposed surface even though no handler exists for them, and they are the reason
the `title`/`description`/`version` arguments at `app/api.py:19-21` are externally visible rather than
decorative.

**All ten declared routes are reachable cross-origin.** The single middleware permits every origin,
method and header with credentials allowed (`app/api.py:25-31`); there is no authentication anywhere in
the repository, so the surface is entirely unauthenticated.

### 2.3 Notes on the surface

**2.3.1 The listing pipeline is fixed, and `total` follows it.** Filter, then search, then sort
(`app/api.py:51-60`) — the order is hard-coded, and the two query parameters compose: supplying both
narrows to prompts that are in the collection *and* match the search. Because `total` is computed last
(`:62`), it reports the size of the filtered result, so a client cannot use it to page over the whole
store. Sorting is applied unconditionally with `descending=True`, including when the list is empty.

**2.3.2 `PUT` is a full replace, not a merge.** Route 5 rebuilds the prompt from the request body
field by field (`:103-111`). Only `id` and `created_at` are carried over from the stored record; every
other field is taken from `PromptUpdate`, so a field the client omits is overwritten with that field's
default rather than preserved. This is correct HTTP semantics for `PUT`, and it is the reason the
absence of `PATCH` (§2.3.4) is a functional gap and not merely a stylistic one.

**2.3.3 Handling of "not found" is inconsistent across the surface.** Four of the five routes that
look up a single entity guard the result before using it — `if not existing` (`:92`), `if not
collection` (`:138`), and the two deletes branching on a boolean (`:122`, `:155`) — and all four raise
404. Route 3 instead reaches into the result (`if prompt.id`, `:73`) before establishing that there is
a result, which turns a miss into a 500. The distinction is the return type: `get_prompt` and
`get_collection` are `Optional[...]`, where `None` is the miss and must be separated out before use,
whereas `get_all_prompts` and `get_all_collections` return `List[...]` and cannot be `None` — an empty
list there is a valid answer, not a miss, which is why routes 2 and 7 correctly test nothing.

One further unguarded use of an `Optional` return: route 5 returns `storage.update_prompt(...)`
straight to the client (`:113`), and that method is `Optional[Prompt]`. It is safe only because
existence was already established at `:91-93` — safe by surrounding context rather than by the shape
of the call itself.

A second inconsistency in the same area: a **missing** prompt is a 404 (`:93`), but a **missing
referenced collection** on create or update is a 400 (`:83`, `:99`). Both describe an id that does not
resolve; the first is about the addressed resource, the second about the request body, which is the
distinction the two codes are drawing.

**2.3.4 `PATCH /prompts/{id}` is absent by design of the exercise.** A comment marks where it belongs
(`app/api.py:116-117`). With only `PUT` available, there is no way for a client to change one field of
a prompt without resending all of them, per §2.3.2.

**2.3.5 Defects visible at this layer.** Recorded here because a system model must not contradict the
code; the fixes belong to later tasks and no decision about them is taken in this section.

| Where | Observable behaviour today | Owner |
|---|---|---|
| Route 3, `app/api.py:70-73` | 500 instead of 404 for an unknown prompt id | Task 1.3 |
| Route 5, `app/api.py:110` | `updated_at` is carried over unchanged, so a successful update leaves the prompt claiming it was last modified at its previous timestamp | Task 1.4 |
| Route 2, `app/api.py:60` | Sorting is requested as newest-first; whether it delivers that depends on `sort_prompts_by_date`, which is in `app/utils.py` and has not been read at this stage | Task 1.5 |
| Route 10, `app/api.py:155-158` | The collection is removed while prompts referencing it are left untouched, so their `collection_id` points at an id that no longer resolves | Task 1.6 |

---

## Context Strategy

Required by C1.2. One row per exploration stage, recording the context level actually used and the
reason for it. This table matches `docs/prompt-log.md` — the rationale below is the reason given
before the reading was done, not one composed afterwards.

| Stage | Subject | Context level | Reason |
|---|---|---|---|
| 1 | Architecture (§1) | **Whole-repo** — every file under `backend/`, full contents | Size. The entire backend is 587 lines of Python across seven source files and two test files, so loading all of it is cheap and removes the guesswork about which module is central. The alternatives considered were structure-only (file tree and line counts) and imports-only; both were rejected because they would have made the dependency-direction claims in §1.3 inferences from filenames rather than facts read from the source, and C1.1 fails a model whose claims contradict the code. Breadth is correct here *because* the repository is small; the same choice would be wrong at a larger scale. |

| 2 | Entry points (§2) | **File-level** — `app/api.py` only, full contents; no other source file re-read | Coupling, not size. The whole backend would still have fitted in context, so breadth was available and was declined: §1.3 established `api.py` as the single hub that imports `models`, `storage` and `utils` while nothing imports it back, which makes it the one file where every module meets and therefore the one that has to be read line by line rather than skimmed for shape. Loading the leaf modules alongside it would have invited describing what the helpers *do* instead of what the routes *expose*, and the boundary of this section is the exposed surface. The cost is recorded rather than hidden: the sorting claim in §2.3.5 stops at the call site because `app/utils.py` was deliberately not in context, and it is completed at stage 3. |

Stages 3–6 to follow.
