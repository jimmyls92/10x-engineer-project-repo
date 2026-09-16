# PromptLab — System Model

A description of the system as the code actually implements it. Every behavioural claim below is
tied to the file and line it was read from, so it can be checked rather than trusted.

Line references are to the repository state at the time of writing; paths are relative to `backend/`.

> **Status.** Written stage by stage as the exploration proceeds. Section headings follow the module
> brief's own checklist. Still to come: Storage layer, External dependencies.

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

## 3. Data flow

How a request travels from route to storage and back. The section is organised as a matrix rather
than as a narrative of pipeline stages: the stages themselves — JSON → validation → handler → storage
→ serialisation — are FastAPI's and are the same in any FastAPI application, so describing them would
say little about PromptLab. What differs per route is what the cells hold.

Cells cite `app/api.py` unless another file is named. Read left to right, each row is one request's
journey out and back.

### 3.1 Prompt routes and health

| Route | Bind & validate | Handler guards | Storage | Transform | Response |
|---|---|---|---|---|---|
| `GET /health` | — | — | **none** | — | `HealthResponse` 200 (`:38`) |
| `GET /prompts` | Two optional query params, `collection_id` and `search` (`:44-47`) | — | `get_all_prompts` → a new list holding the **stored objects themselves** (`storage.py:26`) | filter, if `collection_id` (`utils.py:18`) → search, if `search` (`utils.py:23-27`) → sort, **unconditionally** (`utils.py:14`) | `PromptList` with `total` = count **after** filtering (`:62`) 200 |
| `GET /prompts/{prompt_id}` | Path `str`, no constraint | **None before use** — `prompt.id` is evaluated first (`:73`) | `get_prompt` → `Optional[Prompt]`, the stored object (`storage.py:23`) | — | `Prompt` 200 on a hit; **500 on a miss** (observed, §3.3) |
| `POST /prompts` | Body `PromptCreate`; a field violation is a **422 from the framework** (observed, §3.3) | If `collection_id` given, collection must exist, else **400** (`:80-83`) | `create_prompt` stores the object the handler built, uncopied (`storage.py:19`) | — | `Prompt` 201, with `id` and both timestamps from the model defaults (`:85`) |
| `PUT /prompts/{prompt_id}` | Path `str` + body `PromptUpdate`; **422** on a field violation | Prompt must exist, else **404** (`:91-93`); collection, if given, must exist, else **400** (`:96-99`) | `update_prompt` replaces the dict entry (`storage.py:28-32`); its `Optional` return is passed on **unchecked** (`:113`) | — | `Prompt` 200, rebuilt field by field rather than mutated (`:103-111`) |
| `DELETE /prompts/{prompt_id}` | Path `str` | Branches on the returned `bool`; **404** if false (`:122`) | `delete_prompt` (`storage.py:34-38`) | — | 204, empty body (`:124`) |

### 3.2 Collection routes

| Route | Bind & validate | Handler guards | Storage | Transform | Response |
|---|---|---|---|---|---|
| `GET /collections` | — | — | `get_all_collections` (`storage.py:49-50`) | **none** — no filter, search or sort exists for collections | `CollectionList` 200 (`:132`) |
| `GET /collections/{collection_id}` | Path `str` | `if not collection` → **404** (`:138-139`) | `get_collection` → `Optional[Collection]` (`storage.py:46-47`) | — | `Collection` 200 |
| `POST /collections` | Body `CollectionCreate`; **422** on a field violation (observed, §3.3) | **None** — there is no second entity to cross-check | `create_collection` (`storage.py:42-44`) | — | `Collection` 201 (`:145-146`) |
| `DELETE /collections/{collection_id}` | Path `str` | Branches on the returned `bool`; **404** if false (`:155-156`) | `delete_collection` touches the collections dict **only** (`storage.py:52-56`) | — | 204, empty body |

### 3.3 Claims verified by execution, not by reading

Two cells above assert framework behaviour rather than behaviour visible in a line of this repository.
Both were run rather than assumed, against `app.api:app` through `fastapi.testclient.TestClient` with
storage cleared first:

| What was checked | Result |
|---|---|
| `GET /prompts/does-not-exist` | **500**, body `Internal Server Error`. With `raise_server_exceptions=True` (the `TestClient` default) the request instead propagates `AttributeError: 'NoneType' object has no attribute 'id'`. |
| `POST /prompts` with `title=""` | **422** |
| `POST /prompts` with an empty body | **422** |
| `POST /prompts` with an unknown `collection_id` | **400** — the handler's own check (`:80-83`), not the framework's |
| `POST /prompts` with a valid body | **201** |
| `POST /collections` with a 101-character `name` | **422** |

The `raise_server_exceptions` detail is recorded because it changes how the miss case can be asserted
in a test: under the default client the exception escapes instead of becoming a response.

### 3.4 What the matrix cannot hold

**3.4.1 Nothing is copied in either direction.** `get_prompt` returns the stored object
(`storage.py:23`), and `get_all_prompts` returns `list(self._prompts.values())` (`storage.py:26`) — a
new list containing the same objects, not clones. Writes are symmetrical: `create_prompt` files the
very object the handler constructed (`storage.py:19`). A handler that mutated a fetched prompt would
therefore mutate the store directly. No handler does: `PUT` is the only route that could, and it
builds a new `Prompt` instead (`:103-111`). The absence of copying is a property of the storage layer
that the routes currently happen not to exercise, not a guarantee the design enforces.

**3.4.2 The transform column is non-mutating but not correct.** All three helpers return new lists —
two comprehensions and a `sorted()` call (`utils.py:18,23-27,14`) — so the outbound leg never writes
back. But `sort_prompts_by_date` declares `descending: bool = True` and never reads it; the body is
`sorted(prompts, key=lambda p: p.created_at)` with no `reverse` argument, which is ascending, oldest
first (`utils.py:7-14`). `GET /prompts` passes `descending=True` (`:60`). **The call site is correct
and the helper ignores its own parameter** — the defect is one file further down the flow than the
route reads as suggesting.

**3.4.3 Validation is entirely pre-handler.** Every field rule is declarative on the models (cited
from the stage 1 reading; `models.py` was deliberately not in this stage's context), and a violation
becomes a 422 without any handler line executing — confirmed in §3.3. The consequence for reading the
matrix: every check in the *Handler guards* column is an existence or cross-entity check, never a
field check, because field checks can no longer fail by the time the handler starts.

**3.4.4 The collection filter exists twice, and the flow uses the outer one.**
`storage.get_prompts_by_collection` (`storage.py:58-59`) and `utils.filter_prompts_by_collection`
(`utils.py:17-18`) are the same predicate over the same data. `GET /prompts` calls the utils version
(`:52`), so the filtering happens *after* the whole store has been copied into a list rather than
during the scan. The storage version is called by nothing in the application.

**3.4.5 Two routes have an empty Transform column by omission rather than by design.**
`GET /collections` (`:129-132`) offers no filtering, searching or sorting, and no helper exists to
provide any — `utils.py` is typed `List[Prompt]` throughout (`utils.py:7,17,21`). The asymmetry
between the two listing routes is in the helpers, not in the handlers.

---

## 4. Models and relationships

How prompts and collections relate. §4.1 states the shape of the link, §4.2 audits every site that
could uphold it, §4.3 draws out what that means for a client, and §4.4 records the schema detail the
first three depend on.

### 4.1 The shape of the relationship

**Prompts and collections form a many-to-one relationship that only one side declares.**

A prompt carries `collection_id: Optional[str] = None` (`models.py:23`). `Collection` declares `name`,
`description`, `id` and `created_at`, and nothing else (`models.py:45-59`) — **there is no field
pointing back to prompts.** The link therefore exists in exactly one place in the schema, on the child.

`Optional` is load-bearing: `None` is a valid, expected state meaning *filed nowhere*, not a missing
value. The default makes it the state a prompt is created in unless a client says otherwise
(`models.py:23`), and `POST /prompts` skips its collection check entirely when the field is falsy
(`api.py:80`).

The declaration is a type and nothing more. Alone among the six fields a client can supply,
`collection_id` carries no `Field(...)` constraint — compare `title` (1–200), `content` (non-empty),
`description` (≤500), collection `name` (1–100) at `models.py:20-22,46-47`. It is not typed `UUID`
either, though every id is generated as one (`models.py:9-10`), so `collection_id: "banana"` is a
schema-valid prompt.

**Consequence: the relationship is a convention, not a constraint.** Pydantic validates one object in
isolation and has no access to stored collections, so nothing at the model layer can know whether the
string names something real. Whatever integrity exists must be imposed elsewhere — §4.2.

### 4.2 Where the link is upheld, and where it is not

Listed below is every site that **writes `collection_id`, or holds the data needed to check it**. That
is the inclusion rule: a module that merely never mentions the field (`main.py`, the health route) is
not a missing safeguard and is not listed.

| Site | Upholds the link? |
|---|---|
| `models.py:23` | **No** — declares the field and validates nothing beyond its type (§4.1). |
| `POST /prompts` (`api.py:80-83`) | **Yes — once, as the prompt is written.** If `collection_id` is truthy the collection must exist, else **400**. Nothing re-checks afterwards. |
| `PUT /prompts/{id}` (`api.py:96-99`) | **Yes — once, as the prompt is rewritten.** The same check, the same 400. |
| `PUT` body assembly (`api.py:108`) | **No — it can break the link.** `collection_id` is taken from the request body, so an omitted field silently replaces an existing link with `None`. |
| `storage.create_prompt` / `update_prompt` (`storage.py:19,31`) | **No.** The dict value is the whole `Prompt` object (`storage.py:13`), so `collection_id` is persisted without any line naming it — an invalid link passes through unexamined. This is the only layer holding both dicts (`storage.py:13-14`), and therefore the only place a continuous constraint could live. It even has the required query already written: `get_prompts_by_collection` (`storage.py:58-59`) returns exactly the prompts a collection deletion would strand, and nothing in the application calls it. |
| `DELETE /collections/{id}` (`api.py:149-160`, `storage.py:52-56`) | **No — it breaks the link and leaves it broken.** Only the collections dict is mutated; the prompts dict is never read. |
| `GET /prompts?collection_id=…` (`api.py:52`, `utils.py:18`) | **No.** Filtering is raw string equality with no existence check, so a deleted collection's id still returns its former prompts. |

**Observed** (same method as §3.3 — `TestClient`, storage cleared): create a collection, file a prompt
in it, delete the collection. The collection returns 404; the prompt remains, its `collection_id`
unchanged; and `GET /prompts?collection_id=<deleted id>` still returns it. The link outlives its
target, and remains queryable by an id that resolves to nothing.

Integrity is therefore imposed in **exactly two places, both HTTP handlers, both only at the moment a
prompt is written**. There is no check on the collection side, none in storage, and none on any read
path. The guarantee the system actually offers is *this link was valid when it was written* — and the
two operations that can falsify it afterwards, deleting the collection and a `PUT` that omits the
field, are both in the table above, both marked No.

### 4.3 What follows for a client

**A non-null `collection_id` is not a promise.** Given a prompt, a client cannot tell from the response
whether its collection still exists — the field is returned exactly as stored (`api.py:74`). Resolving
it means a second request to `GET /collections/{id}`, which may legitimately return 404 for a prompt
that was filed correctly at the time. Distinguishing *unfiled* (`None`) from *filed in something
deleted* (a non-null id that no longer resolves) requires that extra call.

**The relationship is never resolved in a response.** No envelope nests the other side: `PromptList`
holds prompts, `CollectionList` holds collections (`models.py:64-71`), and `Collection` carries no
member list or count (`models.py:54-59`). A client rendering "a collection and its prompts" makes two
calls — `GET /collections/{id}` and `GET /prompts?collection_id={id}` — and the second is the only way
to traverse the link at all.

**Traversal is asymmetric in cost as well as in direction.** prompt → collection is a dict lookup
(`storage.py:47`). collection → prompts is a full scan of every prompt, and as routed it is worse than
that: `GET /prompts` copies the entire store into a list (`storage.py:26`) and *then* filters it in
`utils.py:18`, rather than using `storage.get_prompts_by_collection` (`storage.py:58-59`), which scans
once and is called by nothing.

**`PUT` can unfile a prompt without the client intending it.** Because the handler rebuilds the prompt
from the request body (`api.py:103-111`), a body that omits `collection_id` writes the default `None`
and the prompt silently leaves its collection. This is not hypothetical: `test_api.py:92-101` updates a
prompt with a body containing only `title`, `content` and `description`. It is correct `PUT`
semantics — the client asked to replace the resource — and it is the concrete cost of there being no
`PATCH` (§2.3.4).

**Counts follow the filter, not the collection.** `PromptList.total` is computed after filtering
(`api.py:62`), so `GET /prompts?collection_id={id}` yields the collection's size as a side effect.
There is no other way to obtain it, and the figure counts prompts pointing at the id — including
orphans, if the collection has since been deleted.

### 4.4 Schema facts that bear on the above

The three model families — entities, request DTOs, response envelopes — are set out in §1.2. What
matters here is the detail behind them.

**The DTOs add nothing to their bases.** `PromptCreate` and `PromptUpdate` are both `pass`
(`models.py:26-31`), so they are field-for-field identical to `PromptBase` and to each other. Create
and update therefore accept exactly the same shape, and **`PromptUpdate` has no way to express "leave
this field alone"** — an absent field is indistinguishable from one set to its default. That is the
schema-level reason `PUT` unfiles prompts (§4.3) and the reason a `PATCH` cannot simply reuse this
model.

**Identity and timestamps are server-assigned and cannot be supplied by a client.** `id`, `created_at`
and `updated_at` are declared with `default_factory` on the entity classes only
(`models.py:35-37,55-56`) and are absent from the `*Create` DTOs, so a request body carrying them is
ignored rather than honoured. Ids come from `generate_id` — `str(uuid4())` (`models.py:9-10`) — but
every id field is typed `str`, not `UUID`, so the format is a convention of the generator, not a
constraint on the data (§4.1).

**`Collection` has `created_at` and no `updated_at`** (`models.py:55-56`), which matches the route
surface exactly: there is no `PUT` or `PATCH` for collections (§2.1), so a collection is immutable once
created and has no second timestamp to maintain.

**Timestamps are naive UTC.** `get_current_time` returns `datetime.utcnow()` (`models.py:13-14`), which
carries no `tzinfo`. Values are therefore comparable with each other — which is all the sort in
`utils.py:14` requires — but nothing in a serialised response marks them as UTC. `datetime.utcnow()` is
also deprecated from Python 3.12 onward in favour of `datetime.now(timezone.utc)`.

**`Config.from_attributes = True`** is set on both entity classes (`models.py:39-40,58-59`). It tells
Pydantic to accept objects with matching attributes rather than only dicts — the setting used when
populating models from ORM rows. There is no ORM and no database in the project
(`requirements.txt:1-6`), and every model in the flow is built from keyword arguments
(`api.py:85,103,145`), so the setting is inert: a trace of a shape the service does not have.

---

## 5. Storage layer

### 5.1 What the store is

The module states its own intent: in-memory storage for prompts and collections, "in a production
environment, this would be replaced with a database" (`storage.py:1-5`). The rest of this section takes
that at face value and asks what the implementation actually commits to.

**The container.** A single class, `Storage` (`storage.py:11`), holding **two plain Python
dictionaries** — `self._prompts` and `self._collections` (`storage.py:13-14`) — each typed
`Dict[str, ...]` and keyed by the entity's own `id`. The underscore prefix marks both as private by
convention; no method returns either dictionary itself.

The two dictionaries are **structurally independent**. Neither holds a reference to the other's
entries, and neither is indexed by anything but its own key, so the prompt→collection link described in
§4 exists only as a field value inside each prompt — never as part of the store's shape. The one method
that relates the two, `get_prompts_by_collection` (`storage.py:58-59`), is not an exception: it consults
no index, it **iterates every prompt and compares `collection_id`**. The relationship is recomputed on
each call and is never stored. A lookup by id is a direct dictionary hit; a lookup by collection is a
full pass over the prompts.

**The key type is `str`, not `UUID`.** Ids are server-assigned strings (established in §4.4), so a
lookup key is any string a caller supplies — the dictionary cannot reject a malformed one, only miss on
it. Whether that counts as a limitation is left to §5.4.

**The instance.** Exactly one, constructed at import time as a module-level global — `storage =
Storage()` (`storage.py:69`) — and bound into the routes by direct import, `from app.storage import
storage` (`api.py:13`). There is no factory, no constructor argument and no injection seam (established
in §1.4). Every route in the application therefore reads and writes **the same object**, and no route
can be handed a different one.

**Lifetime.** The dictionaries live for the lifetime of the Python process and no longer. There is no
file, no serialisation, no load on startup and no flush on shutdown; a restart begins with two empty
dictionaries. The single reset path is `clear()` (`storage.py:63-65`), filed under "Utility" and called
by nothing in `app/` — it is a test-support affordance, not part of any request path.

---

## Context Strategy

Required by C1.2. One row per exploration stage, recording the context level actually used and the
reason for it. This table matches `docs/prompt-log.md` — the rationale below is the reason given
before the reading was done, not one composed afterwards.

| Stage | Subject | Context level | Reason |
|---|---|---|---|
| 1 | Architecture (§1) | **Whole-repo** — every file under `backend/`, full contents | Size. The entire backend is 587 lines of Python across seven source files and two test files, so loading all of it is cheap and removes the guesswork about which module is central. The alternatives considered were structure-only (file tree and line counts) and imports-only; both were rejected because they would have made the dependency-direction claims in §1.3 inferences from filenames rather than facts read from the source, and C1.1 fails a model whose claims contradict the code. Breadth is correct here *because* the repository is small; the same choice would be wrong at a larger scale. |

| 2 | Entry points (§2) | **File-level** — `app/api.py` only, full contents; no other source file re-read | Coupling, not size. The whole backend would still have fitted in context, so breadth was available and was declined: §1.3 established `api.py` as the single hub that imports `models`, `storage` and `utils` while nothing imports it back, which makes it the one file where every module meets and therefore the one that has to be read line by line rather than skimmed for shape. Loading the leaf modules alongside it would have invited describing what the helpers *do* instead of what the routes *expose*, and the boundary of this section is the exposed surface. The cost is recorded rather than hidden: the sorting claim in §2.3.5 stops at the call site because `app/utils.py` was deliberately not in context, and it is completed at stage 3. |

| 3 | Data flow (§3) | **File-level, three files** — `app/api.py`, `app/storage.py`, `app/utils.py`. `app/models.py` deliberately excluded | Coupling. A data flow claim spans every module a request touches, so the two files the request passes through after the route had to be added; `api.py` alone would have described the return leg of the listing route as "three helpers happen". The initial proposal was two files, excluding `utils.py` on the premise that it only transforms data — the premise was the thing under test, and reading the file is what showed `sort_prompts_by_date` ignores its own `descending` argument (§3.4.2), closing the gap stage 2 left open. `models.py` was argued out on the same principle that brought `utils.py` in: it is the shape of what travels rather than a hop on the path, and it is stage 4's subject, so reading it here would have pulled stage 4's content forward. Its field constraints are cited in §3.4.3 from the stage 1 reading and marked as such. |

| 4 | Models and relationships (§4) | **Whole-repo** — every file under `backend/`, `tests/` included | Coupling, of the opposite kind to stage 2. There the coupling was *concentrated*: one hub file held every route, so attention belonged in it. Here it is *distributed*: the link is declared in `models.py:23`, enforced in `api.py:80-83` and `:96-99`, ignored in `storage.py:19,31`, and broken without repair in `storage.py:52-56`. Any single file shows the declaration and hides whether anything upholds it, and §4.2 is an audit that only exists if every site can be seen at once. `tests/` was included deliberately rather than as a side effect of breadth, and earned it: `test_api.py:154-179` asserts the current orphaning behaviour, and `test_api.py:92-101` is a live example of the `PUT` unfiling described in §4.3. |

Stages 5–6 to follow.

### A note on what the narrowing was for

Recorded because it is the honest summary of the four rows above, and because it changes what they
mean. **The whole backend is 587 lines. Breadth was affordable at every stage, so no narrowing in this
table was forced by a limit** — stage 2 could have been run whole-repo and would have produced a
correct §2.

What narrowing bought was **attention, not feasibility**. Stage 2 excluded the leaf modules so that the
account of the exposed surface would be an account of the surface, and not drift into what the helpers
do. Stage 3 admitted exactly the two files a request passes through, and refused `models.py` so that
stage 4's subject would not be consumed early.

The clearest evidence that the levels were chosen rather than defaulted is that **the narrowing has a
recorded cost**: stage 2's decision to leave `utils.py` out left the sorting claim in §2.3.5 explicitly
incomplete, and stage 3 closed it — and the reason it could be closed is that `utils.py` was read there
for its behaviour rather than skimmed as part of a repository-wide pass. Where the argument has run the
other way, as at stage 4, breadth was taken for a reason that is stated in the row and not simply
because the repository is small.
