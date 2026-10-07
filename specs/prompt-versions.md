# Feature spec: Prompt versions

| | |
|---|---|
| **Feature** | Track the version history of a prompt's content |
| **Status** | Specified in Module 2 (Task 2.5); **not implemented yet**, planned for Module 4. No route or test exists. Line numbers cited below are from the end of Module 2 (`1c9cc88`); the tagging feature has since moved them |
| **Decisions** | Worked through one at a time in Module 2's `docs/prompt-log.md` (branch `Week-2`), entries 97-128 |
| **Code it touches** | `backend/app/models.py`, `backend/app/api.py`, `backend/app/utils.py`, `backend/tests/test_api.py` |

Requirements are numbered: **BR** business, **FR** functional, **NFR** non-functional, **AC**
acceptance criterion, **E** edge case. Every behaviour below is stated as the request a client sends
and the exact response it gets, so each AC can be turned into a test without interpretation.

---

## Overview and goals

### Overview

Today a prompt keeps only its latest state. `PUT` and `PATCH /prompts/{prompt_id}` build a new
`Prompt` and replace the stored one (`api.py:183-193`, `:234-244`), so the earlier wording is lost
after every edit.

This feature keeps a numbered history of **a prompt's `content`**. Creating a prompt records its
content as version 1. Each later edit that changes the content records the new content as the next
version. The history is stored on the prompt itself and can be read through two new read-only
endpoints: the whole history, or one version.

### Business requirements

| ID | Requirement |
|---|---|
| **BR-1** | A user can see every wording a prompt's content has had, in order, and when each one was introduced. |
| **BR-2** | A user can read one specific earlier wording by its version number. |
| **BR-3** | A user can go back to an earlier wording without losing the history. |
| **BR-4** | Adding history does not change how any existing endpoint behaves or what it returns. |

### Goals

- A complete, gap-free history of `content`: version 1 is the content the prompt was created with,
  and the latest version is always the prompt's current content.
- History that only grows when the text of the prompt actually changes, so it never holds two
  consecutive identical versions.
- A client can ask for the whole history, or a slice of it, in either order.

### Non-goals (out of scope)

| Not included | Why |
|---|---|
| Versioning `title`, `description` or `collection_id` | A version records **what the prompt says**, not how it is labelled or where it is filed (entries 104-106). A rename or a move leaves no history. |
| A restore endpoint | Restoring already works: read the old version, then `PATCH` its content. That saves a new version (BR-3, US-5). |
| Editing or deleting individual versions | History is written only by the server, as a side effect of creating and editing a prompt. |
| Diffs between versions | Not asked for; a client can compare two `content` values itself. |
| Surviving a restart | Storage is in memory (NFR-2). |
| Looking a history up by title | Titles are neither unique nor stable. A client finds the `prompt_id` first (see *How a client finds a `prompt_id`*). |

### Glossary

| Term | Meaning |
|---|---|
| **Version** | One recorded value of a prompt's `content`, with its number and the time it was introduced. |
| **History** | All versions of one prompt, numbered 1 to *n* without gaps. |
| **Current content** | The prompt's `content` field. Always equal to the content of version *n*. |
| **Content change** | An edit whose new `content` is **not equal**, character for character, to the current content. Case and whitespace count: `"Hello"` and `"Hello "` differ. |

---

## User stories with acceptance criteria

### Functional requirements: when a version is saved

| ID | Requirement |
|---|---|
| **FR-1** | `POST /prompts` saves version 1, holding the new prompt's `content`. Its `created_at` equals the prompt's `created_at` exactly. |
| **FR-2** | `PUT` or `PATCH /prompts/{prompt_id}` saves one new version, numbered *n* + 1, **only when the request makes a content change**. Its `content` is the new content, and its `created_at` equals the `updated_at` the same request stores on the prompt. |
| **FR-3** | An edit that is not a content change saves no version, even when it changes other fields. This covers a `PATCH` without `content`, a `PATCH` or `PUT` that resends the current content, and an empty `PATCH` body. |
| **FR-4** | One request saves at most one version, however many fields it changes. |
| **FR-5** | A request that fails (any 4xx) saves no version and leaves the history unchanged. |
| **FR-6** | Nothing else changes the history. Deleting a collection unfiles its prompts (`api.py:353-356`) but leaves their versions and `updated_at` unchanged. |
| **FR-7** | Versions are never modified or removed while their prompt exists. Deleting the prompt removes its history with it. |
| **FR-8** | Existing prompt responses (`GET`, `POST`, `PUT`, `PATCH` on `/prompts/{prompt_id}`, and each item of `GET /prompts`) do not include the history. It is returned only by the endpoints in *API endpoints*. |

Invariants that hold after every request, and that tests may assert at any point:

- **I-1**: the version numbers of a prompt are exactly 1, 2, …, *n*, and each entry's `version`
  field equals its key in `versions`.
- **I-2**: version *n*'s `content` equals the prompt's `content`.
- **I-3**: `total` in the list response equals *n*.

### US-1: see how a prompt's wording evolved

> As a prompt author, I want to see every version of a prompt's content, oldest first, so that I can
> understand how its wording changed and when.

Implements BR-1, FR-1, FR-2, FR-9, FR-10.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-1.1** | No prompt exists | `POST /prompts` with `{"title": "Summary", "content": "Summarise the text."}`, then `GET /prompts/{id}/versions` | 200, `total` is 1, and `versions` holds one item: `version` 1, `content` "Summarise the text.", and `created_at` equal to the `created_at` of the POST response |
| **AC-1.2** | The prompt from AC-1.1 | `PATCH /prompts/{id}` with `{"content": "Summarise the text in 3 bullets."}`, then `GET /prompts/{id}/versions` | 200, `total` is 2, `versions[1]` has `version` 2, the new content, and `created_at` equal to the `updated_at` of the PATCH response |
| **AC-1.3** | The prompt from AC-1.2 | `PUT /prompts/{id}` with `{"title": "Summary", "content": "Summarise in 5 bullets."}`, then list the versions | 200, `total` is 3, and the `version` values in `versions` are `[1, 2, 3]` in that order |
| **AC-1.4** | A prompt with 3 versions | `GET /prompts/{id}` | 200, and the body has no `versions` key (FR-8) |
| **AC-1.5** | A prompt with 3 versions | `GET /prompts` | 200, and no item of `prompts` has a `versions` key |

### US-2: read one version

> As a prompt author, I want to read one specific version by its number, so that I can look at an
> earlier wording without fetching the whole history.

Implements BR-2, FR-11.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-2.1** | A prompt with 3 versions | `GET /prompts/{id}/versions/2` | 200, body is the single object `{"version": 2, "content": <content of v2>, "created_at": <time of v2>}`, equal to `versions[1]` of the list response |
| **AC-2.2** | A prompt with 3 versions | `GET /prompts/{id}/versions/3` | 200, and `content` equals the prompt's current `content` (I-2) |
| **AC-2.3** | A prompt with 3 versions | `GET /prompts/{id}/versions/4` | 404, body `{"detail": "Version not found"}` |
| **AC-2.4** | Any prompt | `GET /prompts/{id}/versions/0` | 422, `detail[0].loc` is `["path", "version"]`, `detail[0].msg` is "Input should be greater than or equal to 1" |
| **AC-2.5** | Any prompt | `GET /prompts/{id}/versions/abc` | 422, `detail[0].loc` is `["path", "version"]`, `detail[0].msg` is "Input should be a valid integer, unable to parse string as an integer" |
| **AC-2.6** | No prompt has id `nope` | `GET /prompts/nope/versions/1` | 404, body `{"detail": "Prompt not found"}` |

### US-3: only real content changes create history

> As a prompt author, I want renames, description edits and moves between collections to leave the
> history alone, so that the history shows only changes to what the prompt says.

Implements FR-2 to FR-6.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-3.1** | A prompt with 1 version | `PATCH /prompts/{id}` with `{"title": "New title"}` | 200, the title changes, `updated_at` is later than before, and the versions list still has `total` 1 |
| **AC-3.2** | A prompt with 1 version, content "Hello" | `PUT /prompts/{id}` with `{"title": "New title", "content": "Hello"}` | 200, and `total` is still 1 |
| **AC-3.3** | A prompt with 1 version, content "Hello" | `PATCH /prompts/{id}` with `{"content": "Hello"}` | 200, and `total` is still 1 |
| **AC-3.4** | A prompt with 1 version | `PATCH /prompts/{id}` with `{"title": "T2", "description": "D2", "content": "C2"}` | 200, and `total` is 2: one version for the request, not three |
| **AC-3.5** | A prompt with 1 version | `PATCH /prompts/{id}` with `{"content": "C2", "collection_id": "missing"}` | 400 `{"detail": "Collection not found"}`, and `total` is still 1 with version 1 unchanged |
| **AC-3.6** | A prompt with 2 versions, filed in a collection | `DELETE /collections/{collection_id}` | 204, and the prompt's versions list is identical, item for item, to the one read before the deletion |
| **AC-3.7** | A prompt with 1 version, content "Hello" | `PATCH /prompts/{id}` with `{"content": "Hello "}` (trailing space) | 200, and `total` is 2: the comparison is exact |
| **AC-3.8** | A prompt with 1 version | `PATCH /prompts/{id}` with `{}` | 200, and `total` is still 1 |

### US-4: choose the order and the amount

> As a prompt author, I want to ask for the history newest first, and for only the last few versions,
> so that I can see recent changes on a prompt with a long history.

Implements FR-9, FR-10.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-4.1** | A prompt with 5 versions | `GET /prompts/{id}/versions?order=desc` | 200, `version` values `[5, 4, 3, 2, 1]`, `total` 5 |
| **AC-4.2** | A prompt with 5 versions | `GET /prompts/{id}/versions?limit=2` | 200, `version` values `[1, 2]`, `total` 5 |
| **AC-4.3** | A prompt with 5 versions | `GET /prompts/{id}/versions?order=desc&limit=2` | 200, `version` values `[5, 4]`, `total` 5 |
| **AC-4.4** | A prompt with 5 versions | `GET /prompts/{id}/versions?limit=10` | 200, all 5 versions, `total` 5 |
| **AC-4.5** | Any prompt | `GET /prompts/{id}/versions?limit=0` | 422, `detail[0].loc` is `["query", "limit"]`, `detail[0].msg` is "Input should be greater than or equal to 1" |
| **AC-4.6** | Any prompt | `GET /prompts/{id}/versions?order=up` | 422, `detail[0].loc` is `["query", "order"]`, `detail[0].msg` is "Input should be 'asc' or 'desc'" |
| **AC-4.7** | No prompt has id `nope` | `GET /prompts/nope/versions` | 404, body `{"detail": "Prompt not found"}` |
| **AC-4.8** | Any prompt | `GET /prompts/{id}/versions?order=` (empty value) | 422, `detail[0].loc` is `["query", "order"]`, `detail[0].msg` is "Input should be 'asc' or 'desc'". Unlike `GET /prompts`, which ignores an empty query value (`api.py:70-71`) |

### US-5: go back to an earlier wording

> As a prompt author, I want to return a prompt to an earlier wording without losing what came after,
> so that I can undo a change safely.

Implements BR-3, using the existing `PATCH` endpoint. No new endpoint.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-5.1** | A prompt with 3 versions | `GET /prompts/{id}/versions/1`, then `PATCH /prompts/{id}` with `{"content": <content of v1>}` | 200, the prompt's `content` equals v1's, `total` is 4, and version 4's `content` equals version 1's. Versions 1-3 are unchanged |

---

## Data model changes needed

All model changes go in `backend/app/models.py`. Storage (`storage.py`) needs **no change**: the
history lives on the `Prompt` object, which `Storage` already keeps whole in `self._prompts`
(`storage.py:26`).

### New model: `PromptVersion`

One entry of the history. Goes under the `Prompt Models` banner.

| Field | Type | Constraint | Set from |
|---|---|---|---|
| `version` | `int` | `ge=1` | The next number: 1 on creation, *n* + 1 on a content change |
| `content` | `str` | `min_length=1`, as in `PromptBase` | The prompt's content at that moment |
| `created_at` | `datetime` | naive UTC | v1: the prompt's `created_at`. Later: the `updated_at` of the edit that saved it. Never a fresh `get_current_time()` call (see FR-1, FR-2) |

`PromptVersion` is also the response body of `GET /prompts/{prompt_id}/versions/{version}`.

**Note:** the entry repeats its own number, although it is also the dict key. This follows the
existing storage pattern: `self._prompts` is keyed by id, and each `Prompt` still carries its `id`
(`storage.py:26`, `models.py:154`). It means an entry can be returned on its own without rebuilding
it.

### New field on `Prompt`: `versions`

| Field | Type | Default | Serialised |
|---|---|---|---|
| `versions` | `Dict[int, PromptVersion]` | empty dict (`default_factory=dict`) | **No** |

- **Keyed by version number** (`int`), each value a `PromptVersion` with the same `version`.
- **Not serialised**, so that FR-8 and NFR-1 hold without changing any response model. Declaring it
  with `Field(default_factory=dict, exclude=True)` does this. Checked with the versions pinned in
  `requirements.txt` (FastAPI 0.109.0, Pydantic 2.5.3) and with FastAPI 0.141.1 and Pydantic 2.13.5: the field is left out of the response body and does not appear
  in the `Prompt` schema in `/openapi.json`. `model_copy` keeps it, so `delete_collection`
  carries the history across unchanged (FR-6).
- **Not in any request body.** `PromptCreate`, `PromptUpdate` and `PromptPatch` do not declare it,
  so a `versions` key sent by a client is dropped (E-9).

### New model: `PromptVersionList`

Response body of `GET /prompts/{prompt_id}/versions`. Goes under the `Response Models` banner, next to
`PromptList` (`models.py:220`).

| Field | Type | Meaning |
|---|---|---|
| `versions` | `List[PromptVersion]` | The selected versions, in the requested order, after `limit` |
| `total` | `int` | Number of versions the prompt has, **before** `limit` is applied, so it equals the latest version number |

`total` differs from `PromptList.total`, which counts the items returned (`api.py:97`). `CLAUDE.md`
says list totals are "counted after filtering". `limit` is a cut of the result, not a filter, so the
rule still holds, and the docstring must say so.

### Changes to existing code

| Where | Change |
|---|---|
| `create_prompt` (`api.py:145`) | After building the `Prompt`, set `versions` to `{1: PromptVersion(version=1, content=prompt.content, created_at=prompt.created_at)}` before storing it. |
| `update_prompt` (`api.py:183-191`) | Pass `versions=add_version(existing.versions, prompt_data.content, <updated_at>)` to the new `Prompt`, where `<updated_at>` is the same value given to its `updated_at`. |
| `patch_prompt` (`api.py:234-242`) | Same, using the merged `content`. |
| `list_prompt_versions` (new) | Builds its `versions` list with `select_versions`. |
| `utils.py` | Two new pure helpers, below. |

**New helpers in `backend/app/utils.py`.** Both leave their input unchanged and return a new object.

| Function | Returns |
|---|---|
| `add_version(versions: Dict[int, PromptVersion], content: str, created_at: datetime) -> Dict[int, PromptVersion]` | A **new dict**. When `content` differs, character for character, from the content of the latest entry (key *n*), it holds the old entries plus entry *n* + 1, `PromptVersion(version=n + 1, content=content, created_at=created_at)` (FR-2). Otherwise it is an unchanged copy of `versions` (FR-3). |
| `select_versions(versions: Dict[int, PromptVersion], descending: bool, limit: Optional[int]) -> List[PromptVersion]` | The entries as a list sorted by `version`, highest first when `descending` is true (FR-9), then cut to the first `limit` items when `limit` is not `None` (FR-10). Mirrors `sort_prompts_by_date(prompts, descending)` (`utils.py:13`). |

`add_version` returns a dict, not a list. It is the one exception to the coding standard "helpers
in `utils.py` never modify their input; they return a new list" (`CLAUDE.md`): the history is a
dict keyed by version number (see *New field on `Prompt`*), and the helper still returns a new
object, never the one it was given.

**Trap:** `update_prompt` and `patch_prompt` build a brand-new `Prompt`. A new `Prompt` that is not
given `versions=` gets an empty history: the list then returns `total` 0 and every version lookup
returns 404, breaking I-1 to I-3. This is the same kind of trap as copying `existing.id` (see *Known traps* in
`CLAUDE.md`).

---

## API endpoints with request and response shapes

Both endpoints are read-only, go under the `Prompt Endpoints` banner in `api.py`, and follow the
project's naming: `list_prompt_versions` and `get_prompt_version`.

### How a client finds a `prompt_id`

No new endpoint is needed. `POST /prompts` returns the new prompt's `id` (201). `GET /prompts` lists
every prompt with its `id`. `GET /prompts?search=<text>` keeps the prompts whose title or
description contains the text, ignoring case (`utils.py:60-64`). Because it matches contained text,
it can return several prompts, and the client picks one.

### `GET /prompts/{prompt_id}/versions`

Returns the history of one prompt.

**Path parameter**

| Name | Type | Meaning |
|---|---|---|
| `prompt_id` | string | The prompt whose history to return |

**Query parameters** (FR-9, FR-10)

| Name | Type | Default | Constraint | Meaning |
|---|---|---|---|---|
| `order` | `"asc"` or `"desc"` | `"asc"` | exactly one of the two values, lowercase | `asc`: version 1 first. `desc`: the latest version first |
| `limit` | integer | none (all versions) | `>= 1` | Keep at most this many items, counted from the start of the ordered list |

- **FR-9**: the list is ordered by `version` as `order` says. Order is applied **before** `limit`.
- **FR-10**: `limit`, when present, keeps the first `limit` items of the ordered list. A `limit`
  larger than the history returns every version. `total` is the full count in every case.

**Request**

```
curl "http://localhost:8000/prompts/3f1c9a2e-6b0d-4c55-9f5e-2a7d8c1e4b90/versions?order=desc&limit=2"
```

**Response: 200**

```json
{
  "versions": [
    {
      "version": 3,
      "content": "Summarise the text in 5 bullets.",
      "created_at": "2026-09-30T10:12:40.513220"
    },
    {
      "version": 2,
      "content": "Summarise the text in 3 bullets.",
      "created_at": "2026-09-30T10:05:02.004871"
    }
  ],
  "total": 3
}
```

**Errors:** 404 `Prompt not found`; 422 for an invalid `order` or `limit`. See *Error conditions*.

### `GET /prompts/{prompt_id}/versions/{version}`

Returns one version of one prompt (FR-11: the body equals the item with the same `version` in the
list response).

**Path parameters**

| Name | Type | Constraint | Meaning |
|---|---|---|---|
| `prompt_id` | string | | The prompt |
| `version` | integer | `>= 1` | The version number |

**Request**

```
curl http://localhost:8000/prompts/3f1c9a2e-6b0d-4c55-9f5e-2a7d8c1e4b90/versions/1
```

**Response: 200**

```json
{
  "version": 1,
  "content": "Summarise the text.",
  "created_at": "2026-09-30T09:58:11.270045"
}
```

**Errors:** 404 `Prompt not found`; 404 `Version not found`; 422 for a `version` that is not an
integer or is below 1. See *Error conditions*.

### Existing endpoints

| Endpoint | Request | Response | Behaviour added |
|---|---|---|---|
| `POST /prompts` | unchanged | unchanged | Saves version 1 (FR-1) |
| `PUT /prompts/{prompt_id}` | unchanged | unchanged | Saves a version on a content change (FR-2, FR-3) |
| `PATCH /prompts/{prompt_id}` | unchanged | unchanged | Same as PUT |
| `DELETE /prompts/{prompt_id}` | unchanged | unchanged | Removes the history with the prompt (FR-7) |
| `DELETE /collections/{collection_id}` | unchanged | unchanged | None: versions untouched (FR-6) |
| All `GET` on prompts | unchanged | unchanged, no `versions` key | None (FR-8) |

---

## Error conditions and edge cases

### Errors

All errors follow the project's status table (`CLAUDE.md`, *Error handling approach*). 404 bodies
are `{"detail": "<message>"}`. 422 bodies are FastAPI's validation list, where `detail[0].loc` names
the parameter and `detail[0].msg` says what is wrong. The messages below are FastAPI's own, checked
with the versions pinned in `requirements.txt` (FastAPI 0.109.0, Pydantic 2.5.3) and with FastAPI
0.141.1 and Pydantic 2.13.5, which give the same text.

| Status | Endpoint | Condition | Body |
|---|---|---|---|
| **422** | list | `order` is anything but `asc` or `desc`, including `DESC`, `up` and an empty `?order=` | `loc` `["query", "order"]`, `msg` "Input should be 'asc' or 'desc'" |
| **422** | list | `limit` is below 1 | `loc` `["query", "limit"]`, `msg` "Input should be greater than or equal to 1" |
| **422** | list | `limit` is not an integer, including `2.5`, `abc` and an empty `?limit=` | `loc` `["query", "limit"]`, `msg` "Input should be a valid integer, unable to parse string as an integer" |
| **422** | one | `version` is below 1 (`0`, `-1`) | `loc` `["path", "version"]`, `msg` "Input should be greater than or equal to 1" |
| **422** | one | `version` is not an integer (`abc`, `1.5`) | `loc` `["path", "version"]`, `msg` "Input should be a valid integer, unable to parse string as an integer" |
| **404** | both | No prompt has `prompt_id` | `{"detail": "Prompt not found"}` |
| **404** | one | The prompt exists, but `version` is greater than its latest version | `{"detail": "Version not found"}` |

**FR-12, order of checks**, as in every existing endpoint: parameter validation (422), then the
prompt lookup (404 `Prompt not found`), then the version lookup (404 `Version not found`).

| Request | Result | Why |
|---|---|---|
| `GET /prompts/nope/versions/0` | **422**, not 404 | Validation runs before any lookup |
| `GET /prompts/nope/versions?limit=0` | **422**, not 404 | Same |
| `GET /prompts/nope/versions/99` | 404 `Prompt not found` | The prompt is looked up before the version |

No new endpoint returns 400: neither takes a body.

### Edge cases

| ID | Case | Specified behaviour |
|---|---|---|
| **E-1** | A prompt that was never edited | Its history has exactly one version. A prompt never has an empty history. |
| **E-2** | `PUT` resends the current content with other fields changed | No version (FR-3). `updated_at` is still refreshed, as today (`api.py:190`), so the prompt's `updated_at` is later than version *n*'s `created_at`. |
| **E-3** | `PATCH` without `content`, or with the current content | No version (FR-3). `updated_at` is refreshed whenever the body carries a field (`api.py:241`). |
| **E-4** | Content that differs only in case or whitespace | A content change: a new version is saved (AC-3.7). |
| **E-5** | An edit rejected with 404, 400 or 422 | No version, history unchanged (FR-5). The existing endpoints raise before storing (`api.py:175`, `:181`, `:223`, `:232`). |
| **E-6** | Deleting the prompt | Its history goes with it. Afterwards, both endpoints return 404 `Prompt not found`. |
| **E-7** | Deleting the collection a prompt is filed in | Versions and `updated_at` unchanged (FR-6, AC-3.6). |
| **E-8** | Restoring an old wording with `PATCH` | Saves a new version whose content equals the old one. History is never rewound (AC-5.1). |
| **E-9** | A client sends `"versions"` in a `POST`, `PUT` or `PATCH` body | The key is dropped, as for any undeclared key. The history is built only by the server. |
| **E-10** | `version` sent as `1.0` | Accepted as version 1: FastAPI parses an integer-valued decimal string as an integer. `1.5` gives 422. |
| **E-11** | `limit` larger than the history | Every version is returned; not an error (AC-4.4). |
| **E-12** | The version's timestamps | Naive UTC, serialised like every other timestamp in the API, for example `"2026-09-30T09:58:11.270045"`. Tests compare them with `datetime.fromisoformat`, or as strings, since they are copies of values already returned (FR-1, FR-2). |
| **E-13** | The server restarts | All prompts and their histories are lost (NFR-2). |
| **E-14** | Prompts stored with an empty-string `collection_id` | No effect on versions. `collection_id` is not versioned (see *Known traps* in `CLAUDE.md` for the existing behaviour). |
| **E-15** | A tag-only edit (tagging, `specs/tagging-system.md`, exists since Module 3) | No version (FR-3): tags are not content. `updated_at` is still refreshed. Mirrors tagging E-9; the test is written by whichever of the two features is built second, which is this one. |

---

## Non-functional requirements

| ID | Requirement | How it is checked |
|---|---|---|
| **NFR-1** | **Backward compatibility.** Every existing endpoint keeps its request shape, response shape and status codes. | The provided tests pass unchanged, and AC-1.4 and AC-1.5 pass. |
| **NFR-2** | **In-memory storage.** The history is kept in memory with its prompt, like all data today (`storage.py:26`). It is not persisted, and is lost on restart. | Stated as a property; no persistence is promised or tested. |
| **NFR-3** | **Coding standards.** The implementation follows *PromptLab coding standards* in `CLAUDE.md`: layering, `typing` hints, Google-style docstrings, timestamps copied from values made by `get_current_time()`, tests through the HTTP API for every status each endpoint returns. | Review against those sections, and `pytest tests/ -v` passes. |
| **NFR-4** | **Documentation.** `README.md` (Features list and endpoint summary) and `docs/API_REFERENCE.md` (a section per endpoint, with curl example, sample response and errors) gain both endpoints. The `POST`, `PUT` and `PATCH` sections mention that they save versions. | The endpoint lists in both files match the routes in `api.py`. |

### Tests to write

In `backend/tests/test_api.py`, in a new class `TestPromptVersions`, named
`test_<verb>_<resource>_<behaviour>`, one per AC or per parametrised group of ACs:

| Test | Covers |
|---|---|
| `test_create_prompt_saves_version_one` | AC-1.1 |
| `test_patch_prompt_content_saves_version` / `test_update_prompt_content_saves_version` | AC-1.2, AC-1.3 |
| `test_get_prompt_hides_versions` / `test_list_prompts_hides_versions` | AC-1.4, AC-1.5 |
| `test_get_prompt_version_success` / `test_get_prompt_version_latest_is_current` | AC-2.1, AC-2.2 |
| `test_get_prompt_version_not_found` | AC-2.3 |
| `test_get_prompt_version_invalid` (parametrised: `0`, `-1`, `abc`) | AC-2.4, AC-2.5 |
| `test_get_prompt_version_prompt_not_found` / `test_list_prompt_versions_prompt_not_found` | AC-2.6, AC-4.7 |
| `test_patch_prompt_without_content_change_saves_nothing` (parametrised over the bodies of AC-3.1, AC-3.3, AC-3.8) | AC-3.1, AC-3.3, AC-3.8 |
| `test_update_prompt_same_content_saves_nothing` | AC-3.2 |
| `test_patch_prompt_many_fields_saves_one_version` | AC-3.4 |
| `test_patch_prompt_rejected_saves_nothing` | AC-3.5 |
| `test_delete_collection_keeps_versions` | AC-3.6 |
| `test_patch_prompt_whitespace_is_content_change` | AC-3.7 |
| `test_list_prompt_versions_order_and_limit` (parametrised over AC-4.1 to AC-4.4) | AC-4.1 to AC-4.4 |
| `test_list_prompt_versions_invalid_query` (parametrised: `limit=0`, `order=up`, `order=`) | AC-4.5, AC-4.6, AC-4.8 |
| `test_patch_prompt_restore_saves_new_version` | AC-5.1 |
| `test_patch_prompt_tags_saves_no_version`: a prompt with 1 version; `PATCH` with `{"tags": ["ai"]}` gives 200; the versions list still has `total` 1, and `updated_at` is later than before. **Written only by whichever of versions and tagging is built second.** | E-15 |
