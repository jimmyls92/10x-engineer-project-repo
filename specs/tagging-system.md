# Feature spec: Tagging system

| | |
|---|---|
| **Feature** | Tag prompts for organization |
| **Status** | Specified in Module 2 (Task 2.5); to be implemented in Module 3 or 4 |
| **Decisions** | Worked through one at a time in `docs/prompt-log.md`, entries 138-176 |
| **Code it touches** | `backend/app/models.py`, `backend/app/api.py`, `backend/app/utils.py`, `backend/tests/test_api.py` |

Requirements are numbered: **BR** business, **NG** non-goal, **NFR** non-functional, **AC**
acceptance criterion, **E** edge case. Every behaviour below is stated as the request a client sends and the exact response it
gets, so each AC can be turned into a test without interpretation.

---

## Overview and goals

### Overview

Today a prompt can be grouped in one way only: it is filed in at most one collection, through a
single `collection_id` (`models.py:61`). A prompt about reviewing Python code cannot be found both
as "code review" and as "Python".

This feature lets a prompt carry **tags**: short lowercase labels, stored on the prompt as a list
of strings and set through the existing `POST`, `PUT` and `PATCH /prompts` endpoints. A tag is not
a resource of its own: it has no id, and it exists only while some prompt carries it. Two read
paths use tags: a repeatable `tag` filter on `GET /prompts`, and a new `GET /tags` that lists every
tag in use with how many prompts carry it.

### Business requirements

| ID | Requirement |
|---|---|
| **BR-1** | A user can attach several labels to a prompt, independently of its collection, and change them later (US-1). |
| **BR-2** | Labels stay clean: a malformed label is refused with a message saying what is wrong, never silently corrected (US-2). |
| **BR-3** | A user can list the prompts that carry given labels, combined with the existing filters (US-3). |
| **BR-4** | A user can see which labels exist and how widely each is used (US-4). |
| **BR-5** | A client that never sends `tags` keeps working: requests without the field behave as today, and the provided tests still pass. |

### Goals

- One exact form for every tag, `^[a-z0-9]+(-[a-z0-9]+)*$`, 1 to 32 characters, so that one word is
  always one tag and filtering never needs case rules.
- At most 10 tags per prompt, none repeated, kept in the order the client sent them.
- Filtering by tag that narrows, as the existing filters do: every tag given must be present.
- A list of tags in use that is always derived from the stored prompts, so it can never disagree
  with them.

### Non-goals (out of scope)

| | Not included | Why |
|---|---|---|
| **NG-1** | Renaming a tag across all prompts | It would need a write endpoint on `/tags`; tags are written only through the prompt endpoints (entry 148). |
| **NG-2** | Endpoints that add or remove one tag | `PATCH` with the new list already does it (entry 148). |
| **NG-3** | OR matching in the `tag` filter | The filter narrows by AND, like the other filters (entry 149). |
| **NG-4** | Case-insensitive matching, or normalising tags | A tag must already be in its stored form; the server validates, never rewrites (entries 141, 144). |
| **NG-5** | Filtering `GET /tags` by collection | A client can list a collection's prompts instead, and the filter would carry the `collection_id` quirk into a new endpoint (entry 153). |

### Glossary

| Term | Meaning |
|---|---|
| **Tag** | One string in a prompt's `tags` list, matching `^[a-z0-9]+(-[a-z0-9]+)*$`, 1 to 32 characters. |
| **Tag in use** | A tag carried by at least one stored prompt. Only these appear in `GET /tags`. |
| **Prompt count** | For one tag, the number of stored prompts whose `tags` contains it. |

---

## User stories with acceptance criteria

### US-1: tag a prompt when creating or editing it

> As a prompt author, I want to attach labels to a prompt when I create or edit it, so that I can
> group related prompts across collections.

Every change is re-read with `GET /prompts/{id}` to prove the tags were stored, not only echoed.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-1.1** | Any | `POST /prompts` with a title, content and `"tags": ["code-review", "ai"]` | 201; the response and `GET /prompts/{id}` both show `"tags": ["code-review", "ai"]`, in that order |
| **AC-1.2** | Any | `POST /prompts` with a title and content and no `tags` key | 201; `GET /prompts/{id}` shows `"tags": []` |
| **AC-1.3** | A prompt tagged `["ai"]` | `PATCH /prompts/{id}` with `{"tags": ["python"]}` | 200; `GET /prompts/{id}` shows `"tags": ["python"]`, and its `updated_at`, parsed with `datetime.fromisoformat`, is later than before the PATCH |
| **AC-1.4** | A prompt tagged `["ai"]` | `PATCH /prompts/{id}` with `{"title": "New"}` | 200; `GET /prompts/{id}` still shows `"tags": ["ai"]` |
| **AC-1.5** | A prompt tagged `["ai"]` | `PATCH /prompts/{id}` with `{"tags": []}` | 200; `GET /prompts/{id}` shows `"tags": []` |
| **AC-1.6** | A prompt tagged `["ai"]` | `PUT /prompts/{id}` with a title and content and no `tags` key | 200; `GET /prompts/{id}` shows `"tags": []` |
| **AC-1.7** | A prompt with no tags | `PUT /prompts/{id}` with a title, content and `"tags": ["b-tag", "a-tag"]` | 200; `GET /prompts/{id}` shows `"tags": ["b-tag", "a-tag"]`, in that order |
| **AC-1.8** | Two prompts, tagged `["ai"]` and `["python"]` | `GET /prompts` | 200; each item of `prompts` carries its own `tags` |

### US-2: invalid tags are refused

> As a prompt author, I want a request with a malformed tag refused with a clear message, so that
> the stored tags stay clean.

Each 422 is asserted on its `loc` and `msg` in the `detail` list. The messages in AC-2.3 and AC-2.6
are Pydantic's own (checked with Pydantic 2.13.5), so an upgrade could change them; those in AC-2.4
and AC-2.5 are this spec's, raised as `ValueError` by a validator.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-2.1** | Any | `POST /prompts` with a title, content and one tag of exactly 32 characters (`"a"` × 32) | 201; `GET /prompts/{id}` shows that tag |
| **AC-2.2** | Any | `POST /prompts` with a title, content and 10 distinct tags (`"t0"` to `"t9"`) | 201; `GET /prompts/{id}` shows all 10, in the order sent |
| **AC-2.3** | Any | `POST /prompts` with `"tags": [<bad>]`, parametrised over the values below | 422; one error with `loc` `["body", "tags", 0]` and the `msg` given below |
| **AC-2.4** | Any | `POST /prompts` with `"tags": ["ai", "ai"]` | 422; `loc` `["body", "tags"]`, `msg` "Value error, tags must not repeat a tag" |
| **AC-2.5** | Any | `POST /prompts` with 11 distinct tags (`"t0"` to `"t10"`) | 422; `loc` `["body", "tags"]`, `msg` "Value error, a prompt can have at most 10 tags; delete a tag before including another" |
| **AC-2.6** | Any | `POST /prompts` with `"tags": null` | 422; `loc` `["body", "tags"]`, `msg` "Input should be a valid list" |
| **AC-2.7** | A prompt tagged `["ai"]` | `PUT /prompts/{id}` (with a title and content) or `PATCH /prompts/{id}`, each sending `"tags": ["Python"]` (parametrised over the two methods) | 422; `GET /prompts/{id}` still shows `"tags": ["ai"]` |
| **AC-2.8** | No prompt has id `nope` | `PATCH /prompts/nope` with `{"tags": ["Python"]}` | 422, not 404: the body is validated before the path lookup |
| **AC-2.9** | A prompt tagged `["ai"]` | `PATCH /prompts/{id}` with `{"tags": null}` | 422; `loc` `["body", "tags"]`, `msg` "Value error, tags cannot be null; send a value or omit the field to keep the current one"; `GET /prompts/{id}` still shows `"tags": ["ai"]` |

Values for AC-2.3:

| `<bad>` | `msg` |
|---|---|
| `"Python"`, `"code review"`, `"-ai"`, `"ai-"`, `"a--b"` | "String should match pattern '^[a-z0-9]+(-[a-z0-9]+)*$'" |
| `""` | "String should have at least 1 character" |
| `"a"` × 33 | "String should have at most 32 characters" |

### US-3: find prompts by tag

> As a prompt author, I want to list only the prompts carrying given tags, so that I can find
> related prompts quickly.

Given for every criterion below: three prompts, created in this order, P1 tagged
`["ai", "code-review"]`, P2 tagged `["ai"]` and P3 tagged `["python"]`. Each result is asserted on
the ids in `prompts`, in order, and on `total`.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-3.1** | P1-P3 | `GET /prompts?tag=ai` | 200; `prompts` is P2, P1 (newest first); `total` 2 |
| **AC-3.2** | P1-P3 | `GET /prompts?tag=ai&tag=code-review` | 200; `prompts` is P1 only: a prompt must carry every tag given; `total` 1 |
| **AC-3.3** | P1-P3 | `GET /prompts?tag=rust` (valid, carried by no prompt) | 200; `prompts` is `[]`; `total` 0 |
| **AC-3.4** | P1-P3, with P1 alone filed in collection C | `GET /prompts?tag=ai&collection_id=<C's id>` | 200; `prompts` is P1 only; `total` 1 |
| **AC-3.5** | P1-P3 | `GET /prompts?tag=ai&search=<P2's title>` | 200; `prompts` is P2 only; `total` 1 |
| **AC-3.6** | P1-P3 | `GET /prompts?tag=`, and `GET /prompts?tag=ai&tag=` | 200; the first gives P3, P2, P1 (`total` 3), as if `tag` were absent; the second gives the same result as AC-3.1: an empty value is ignored |
| **AC-3.7** | P1-P3 | `GET /prompts?tag=Python`, and `GET /prompts?tag=ai&tag=Python` | 422; `msg` "String should match pattern '^([a-z0-9]+(-[a-z0-9]+)*)?$'", with `loc` `["query", "tag", 0]` for the first and `["query", "tag", 1]` for the second |
| **AC-3.8** | P1-P3 | `GET /prompts` with no `tag` | 200; P3, P2, P1; `total` 3 |
| **AC-3.9** | P1-P3 | `GET /prompts?tag=ai&tag=ai` | 200; the same result as AC-3.1: a tag repeated in the query counts once |

The pattern in AC-3.7 is the tag pattern made optional, `( … )?`, so that the empty value of
AC-3.6 passes validation and can be ignored; checked with FastAPI 0.141.1.

### US-4: see which tags exist and how often

> As a prompt author, I want to see every tag in use and how many prompts carry it, so that I know
> which tags I can filter by.

Each item of `tags` is `{"name": <tag>, "prompt_count": <n>}`; `total` counts tags, not prompts.
Each result is asserted on the whole body.

| AC | Given | When | Then |
|---|---|---|---|
| **AC-4.1** | No prompt exists | `GET /tags` | 200; `{"tags": [], "total": 0}` |
| **AC-4.2** | Two prompts, created in this order, tagged `["python", "ai"]` and `["code-review", "ai"]` | `GET /tags` | 200; `tags` is `ai` 2, `code-review` 1, `python` 1, in that order: alphabetical, not the order of first use; `total` 3 |
| **AC-4.3** | The prompts of AC-4.2 | `DELETE` the first prompt, then `GET /tags` | 200; `tags` is `ai` 1, `code-review` 1: `python` is gone, since no prompt carries it; `total` 2 |
| **AC-4.4** | The prompts of AC-4.2 | `PATCH` the second prompt with `{"tags": []}`, then `GET /tags` | 200; `tags` is `ai` 1, `python` 1; `total` 2 |
| **AC-4.5** | Two prompts with no tags | `GET /tags` | 200; `{"tags": [], "total": 0}` |
| **AC-4.6** | One prompt tagged `["ab", "a1", "a-b"]` | `GET /tags` | 200; the names in `tags` are `a-b`, `a1`, `ab`, in that order: Python's string order, where `-` sorts before digits and digits before letters |

---

## Data model changes needed

All new types go in `backend/app/models.py` under the existing `# ============== Prompt Models
==============` banner, except `TagSummary` and `TagList`, which get a new `# ============== Tag
Models ==============` banner. `typing.Annotated` is added to the `typing` import. Storage keeps
whole `Prompt` objects, so `storage.py` is unchanged.

### New type: `Tag`

```python
Tag = Annotated[str, Field(min_length=1, max_length=32, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
```

One tag in a request body. Being a Pydantic item type, each tag that breaks a rule is reported at
its own index, `["body", "tags", <i>]`, with Pydantic's message (AC-2.3).

### New type: `TagQuery`

```python
TagQuery = Annotated[str, Field(max_length=32, pattern=r"^([a-z0-9]+(-[a-z0-9]+)*)?$")]
```

One value of the `?tag=` filter. The same rule as `Tag`, except that the empty string passes, so the
endpoint can ignore it (AC-3.6). It lives in `models.py` with `Tag`, so both rules sit together; it
uses Pydantic's `Field`, not FastAPI's, so `models.py` still imports nothing from FastAPI.

### New function: `check_tag_list`

A module-level function in `models.py`, called by the `tags` validator of both `PromptBase` and
`PromptPatch`, so the list rules are written once.

```python
def check_tag_list(tags: List[str]) -> List[str]:
```

| Check, in this order | Raises `ValueError` with |
|---|---|
| More than 10 tags | "a prompt can have at most 10 tags; delete a tag before including another" |
| A tag appears more than once | "tags must not repeat a tag" |

It returns the list unchanged, in the order sent: tags are never sorted, trimmed or lowercased. A list
that breaks both rules is reported with the count message only. FastAPI prefixes each message with
"Value error, " (AC-2.4, AC-2.5). It runs after every item has passed `Tag`, so a list holding a bad
tag is reported on the tag, not the list.

### New field on `PromptBase`: `tags`

```python
tags: List[Tag] = Field(default_factory=list)
```

With a `field_validator("tags")` that returns `check_tag_list(value)`. `PromptCreate`, `PromptUpdate`
and the stored `Prompt` inherit it, so:

- a POST or PUT without `tags` stores `[]` (AC-1.2, AC-1.6), and every prompt in a response carries
  `tags` (AC-1.8);
- `"tags": null` on POST or PUT is a 422, "Input should be a valid list" (AC-2.6).

### New field on `PromptPatch`: `tags`

```python
tags: Optional[List[Tag]] = None
```

`Optional` so the key can be left out, which keeps the stored tags (AC-1.4). `"tags"` is added to the
fields of the existing `reject_null` validator (`models.py:110`), so an explicit `null` is a 422.
A second `field_validator("tags")` calls `check_tag_list` when the value is not `None`.

### New model: `TagSummary`

| Field | Type | Meaning |
|---|---|---|
| `name` | `str` | The tag |
| `prompt_count` | `int` | How many stored prompts carry it; always at least 1 |

Computed on each request from the stored prompts; never stored.

### New model: `TagList`

| Field | Type | Meaning |
|---|---|---|
| `tags` | `List[TagSummary]` | Every tag carried by at least one prompt, sorted by `name` |
| `total` | `int` | The number of items in `tags` |

Follows the `{<resources>, total}` shape of `PromptList` and `CollectionList`.

### New helpers in `backend/app/utils.py`

Both are pure: they never modify their input and return a new list.

| Function | Returns |
|---|---|
| `filter_prompts_by_tags(prompts: List[Prompt], tags: List[str]) -> List[Prompt]` | The prompts that carry every tag in `tags` (AND). A tag repeated in `tags` counts once (AC-3.9). |
| `count_tags(prompts: List[Prompt]) -> List[TagSummary]` | One `TagSummary` per distinct tag across `prompts`, sorted by `name` with Python's string order (AC-4.6) |

### Changes to existing code in `backend/app/api.py`

| Where | Change |
|---|---|
| `create_prompt` (`api.py:145`) | None: `Prompt(**prompt_data.model_dump())` already carries `tags` |
| `update_prompt` (`api.py:183-191`) | Pass `tags=prompt_data.tags` to the new `Prompt` |
| `patch_prompt` (`api.py:234-242`) | Pass `tags=changes.get("tags", existing.tags)`. A PATCH carrying `tags` refreshes `updated_at` like any other field (`api.py:241`; AC-1.3) |
| `list_prompts` (`api.py:62-97`) | New `tag` query parameter and filter step; see *API endpoints* |
| New `list_tags` | `GET /tags`; see *API endpoints* |

---

## API endpoints with request and response shapes

One endpoint is new, `GET /tags`, handled by `list_tags` under a new
`# ============== Tag Endpoints ==============` banner after the collection endpoints. One gains a
query parameter, `GET /prompts`. Four carry the new `tags` field in their body or response.

### `GET /tags` (new)

Lists every tag carried by at least one prompt, with how many prompts carry it. Read-only: it
computes the list from the stored prompts with `count_tags` on each request.

**Parameters:** none. Any query parameter is ignored, as FastAPI ignores undeclared ones.

**Request**

```
curl http://localhost:8000/tags
```

**Response: 200** (`response_model=TagList`)

```json
{
  "tags": [
    {"name": "ai", "prompt_count": 2},
    {"name": "code-review", "prompt_count": 1},
    {"name": "python", "prompt_count": 1}
  ],
  "total": 3
}
```

With no tag in use: `{"tags": [], "total": 0}`.

**Errors:** none; it always returns 200. **Criteria:** AC-4.1 to AC-4.6.

### `GET /prompts` (changed)

**New query parameter**

| Name | Type | Default | Constraint | Meaning |
|---|---|---|---|---|
| `tag` | `List[TagQuery]`, declared `Query(default=[])`; repeatable | `[]` (no filter) | each value matches `^([a-z0-9]+(-[a-z0-9]+)*)?$`, at most 32 characters | Keep only the prompts that carry **every** non-empty value given |

**Order of steps in `list_prompts`:** the existing `collection_id` filter, then the existing
`search`, then the tag filter (empty values dropped first; if none remain, the step is skipped),
then the sort, newest first, as today. The filters combine by AND, so their order does not change
the result.

**Request**

```
curl "http://localhost:8000/prompts?tag=ai&tag=code-review"
```

**Response: 200** (`PromptList`, unchanged shape; each prompt now carries `tags`)

```json
{
  "prompts": [
    {
      "title": "Code Review Prompt",
      "content": "Review the following code and provide feedback:\n\n{{code}}",
      "description": "A prompt for AI code review",
      "collection_id": null,
      "tags": ["ai", "code-review"],
      "id": "3f1c9a2e-6b0d-4c55-9f5e-2a7d8c1e4b90",
      "created_at": "2026-10-01T09:58:11.270045",
      "updated_at": "2026-10-01T09:58:11.270045"
    }
  ],
  "total": 1
}
```

**Errors:** 422 for a `tag` value that breaks `TagQuery`. See *Error conditions*. **Criteria:**
AC-3.1 to AC-3.9.

### Existing endpoints that carry `tags`

| Endpoint | Request body | Response | Criteria |
|---|---|---|---|
| `POST /prompts` | gains optional `tags`: a list of `Tag`, at most 10, no repeats; left out → `[]` | 201, `Prompt` with `tags` | AC-1.1, AC-1.2, AC-2.1 to AC-2.6 |
| `PUT /prompts/{prompt_id}` | gains optional `tags`, same rules; left out → `[]`, clearing the stored tags | 200, `Prompt` with `tags` | AC-1.6, AC-1.7, AC-2.7 |
| `PATCH /prompts/{prompt_id}` | gains optional `tags`, same rules; left out → stored tags kept; `null` → 422 | 200, `Prompt` with `tags` | AC-1.3 to AC-1.5, AC-2.7 to AC-2.9 |
| `GET /prompts/{prompt_id}` | unchanged | `Prompt` with `tags` | AC-1.1 to AC-1.7 (each re-reads with it) |
| `DELETE /prompts/{prompt_id}` | unchanged | unchanged; the prompt's tags leave `GET /tags` with it | AC-4.3 |

**Request** (POST with tags)

```
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{"title": "Code Review Prompt", "content": "Review the following code and provide feedback:\n\n{{code}}", "tags": ["code-review", "ai"]}'
```

**Response: 201**

```json
{
  "title": "Code Review Prompt",
  "content": "Review the following code and provide feedback:\n\n{{code}}",
  "description": null,
  "collection_id": null,
  "tags": ["code-review", "ai"],
  "id": "3f1c9a2e-6b0d-4c55-9f5e-2a7d8c1e4b90",
  "created_at": "2026-10-01T09:58:11.270045",
  "updated_at": "2026-10-01T09:58:11.270045"
}
```

---

## Error conditions and edge cases

### Errors

Checks run in the project's order: body and query validation (422), then the path lookup (404),
then references in the body (400). A 422 body is FastAPI's `{"detail": [{"loc": ..., "msg": ...,
...}]}`; a 404 or 400 body is `{"detail": "<message>"}`. Only errors this feature adds or changes
are listed; the existing ones stay as they are.

| Endpoint | Status | When | `loc` | `msg` or `detail` | AC |
|---|---|---|---|---|---|
| POST, PUT, PATCH `/prompts…` | 422 | A tag breaks the pattern | `["body", "tags", <i>]` | "String should match pattern '^[a-z0-9]+(-[a-z0-9]+)*$'" | AC-2.3, AC-2.7 |
| POST, PUT, PATCH | 422 | A tag is empty | `["body", "tags", <i>]` | "String should have at least 1 character" | AC-2.3 |
| POST, PUT, PATCH | 422 | A tag is over 32 characters | `["body", "tags", <i>]` | "String should have at most 32 characters" | AC-2.3 |
| POST, PUT, PATCH | 422 | More than 10 tags | `["body", "tags"]` | "Value error, a prompt can have at most 10 tags; delete a tag before including another" | AC-2.5 |
| POST, PUT, PATCH | 422 | A tag is repeated | `["body", "tags"]` | "Value error, tags must not repeat a tag" | AC-2.4 |
| POST, PUT | 422 | `"tags": null` | `["body", "tags"]` | "Input should be a valid list" | AC-2.6 |
| PATCH | 422 | `"tags": null` | `["body", "tags"]` | "Value error, tags cannot be null; send a value or omit the field to keep the current one" | AC-2.9 |
| `GET /prompts` | 422 | A `tag` value breaks the pattern | `["query", "tag", <i>]` | "String should match pattern '^([a-z0-9]+(-[a-z0-9]+)*)?$'" | AC-3.7 |
| `GET /prompts` | 422 | A `tag` value is over 32 characters | `["query", "tag", <i>]` | "String should have at most 32 characters" | E-7 |
| `GET /tags` | — | Never fails | — | — | AC-4.1 to AC-4.6 |

The PUT and PATCH 404 (`Prompt not found`) and 400 (`Collection not found`) are unchanged, and are
raised only for a body whose tags are valid.

### Edge cases

| | Case | Behaviour |
|---|---|---|
| **E-1** | `"tags": null` on different methods | POST and PUT give Pydantic's "Input should be a valid list"; PATCH gives the `reject_null` message (`models.py:110`). The same split already exists for `title` (a null title on POST gives "Input should be a valid string"). AC-2.6, AC-2.9. |
| **E-2** | 11 tags, one of them repeated | One error, the count message: `check_tag_list` checks the count first and stops. |
| **E-3** | A malformed tag and a repeat in the same list, e.g. `["Python", "ai", "ai"]` | One error, on the tag, at `["body", "tags", 0]`: the list rules run only once every item has passed `Tag`. |
| **E-4** | Invalid tags together with an unknown path id or an unknown `collection_id` | 422. The body is validated before any lookup, so `PATCH /prompts/nope` with a bad tag is 422, not 404 (AC-2.8), and a bad tag with an unknown `collection_id` is 422, not 400. |
| **E-5** | Valid tags with an unknown `collection_id` on POST, PUT or PATCH | 400 `Collection not found`, and nothing is stored: the stored tags are unchanged (`api.py:140-143`, `:178-181`, `:229-232`). |
| **E-6** | A tag that differs only in case or spacing, e.g. `"AI"` or `" ai"` | 422. The server never lowercases or trims a tag; the client sends it in its stored form. |
| **E-7** | Empty, repeated or over-long `tag` values in the query | An empty value is ignored, alone or among others (AC-3.6); a repeated value counts once (AC-3.9); a value over 32 characters is 422, since it could never match a stored tag. |
| **E-8** | `DELETE /collections/{collection_id}` | Its prompts are unfiled with `model_copy(update={"collection_id": None})` (`api.py:355`), which keeps their tags. `GET /tags` is unchanged. |
| **E-9** | A tag-only edit, once the prompt versions feature (`specs/prompt-versions.md`) exists | Saves no version, since tags are not content; it still refreshes `updated_at` (AC-1.3). Mirrors versions E-15; the test, `test_patch_prompt_tags_saves_no_version`, is written by whichever of the two features is built second. |
| **E-10** | `GET /tags` with any stored data, or none | Always 200; with no tag in use, `{"tags": [], "total": 0}` (AC-4.1, AC-4.5). |

---

## Non-functional requirements

| ID | Requirement | How it is checked |
|---|---|---|
| **NFR-1** | **Backward compatibility** (BR-5). A request without `tags` behaves as today, and every existing endpoint keeps its status codes. Responses gain one key, `tags`. | The provided tests pass unchanged, and AC-1.2 and AC-1.6 pass. |
| **NFR-2** | **In-memory storage.** Tags are kept on the stored `Prompt`, like all data today (`storage.py:26`). They are not persisted and are lost on restart. `GET /tags` is computed on each request, never stored. | Stated as a property; no persistence is promised or tested. |
| **NFR-3** | **Coding standards.** The implementation follows *PromptLab coding standards* in `CLAUDE.md`: layering (nothing in `models.py` or `utils.py` imports FastAPI), `typing` hints, Google-style docstrings, validation in the model, pure helpers in `utils.py`, tests through the HTTP API for every status each endpoint returns. | Review against those sections, and `pytest tests/ -v` passes. |
| **NFR-4** | **Documentation.** `README.md` (Features list and endpoint summary) gains `GET /tags` and the `tag` filter. `docs/API_REFERENCE.md` gains a section for `GET /tags` (curl example, sample response, errors), the `tag` parameter in the `GET /prompts` section, and the `tags` field and its 422 errors in the `POST`, `PUT` and `PATCH` sections. | The endpoint lists in both files match the routes in `api.py`. |

### Tests to write

In `backend/tests/test_api.py`, in a new class `TestTags`, named `test_<verb>_<resource>_<behaviour>`,
one per AC or per parametrised group of ACs:

| Test | Covers |
|---|---|
| `test_create_prompt_with_tags` / `test_create_prompt_without_tags` | AC-1.1, AC-1.2 |
| `test_patch_prompt_tags_replaced` | AC-1.3 |
| `test_patch_prompt_without_tags_keeps_them` / `test_patch_prompt_empty_tags_clears_them` | AC-1.4, AC-1.5 |
| `test_update_prompt_without_tags_clears_them` / `test_update_prompt_tags_keep_order` | AC-1.6, AC-1.7 |
| `test_list_prompts_shows_tags` | AC-1.8 |
| `test_create_prompt_tags_at_limits` (parametrised: one 32-character tag, 10 tags) | AC-2.1, AC-2.2 |
| `test_create_prompt_invalid_tag` (parametrised over the values of AC-2.3) | AC-2.3 |
| `test_create_prompt_repeated_tag` / `test_create_prompt_too_many_tags` / `test_create_prompt_null_tags` | AC-2.4, AC-2.5, AC-2.6 |
| `test_update_prompt_invalid_tag_keeps_tags` (parametrised over `PUT` and `PATCH`) | AC-2.7 |
| `test_patch_prompt_invalid_tag_not_found` | AC-2.8 |
| `test_patch_prompt_null_tags` | AC-2.9 |
| `test_list_prompts_by_tag` (parametrised over AC-3.1, AC-3.2, AC-3.3, AC-3.9) | AC-3.1 to AC-3.3, AC-3.9 |
| `test_list_prompts_by_tag_and_collection` / `test_list_prompts_by_tag_and_search` | AC-3.4, AC-3.5 |
| `test_list_prompts_empty_tag_ignored` | AC-3.6 |
| `test_list_prompts_invalid_tag` (parametrised: `?tag=Python`, `?tag=ai&tag=Python`, a 33-character value) | AC-3.7, E-7 |
| `test_list_prompts_without_tag` | AC-3.8 |
| `test_list_tags_empty` (parametrised: no prompt, two untagged prompts) | AC-4.1, AC-4.5 |
| `test_list_tags_counts_and_order` | AC-4.2 |
| `test_list_tags_after_delete` / `test_list_tags_after_patch` | AC-4.3, AC-4.4 |
| `test_list_tags_string_order` | AC-4.6 |
| `test_update_prompt_unknown_collection_keeps_tags` | E-5 |
| `test_delete_collection_keeps_tags` | E-8 |
| `test_patch_prompt_tags_saves_no_version`: a prompt with 1 version; `PATCH` with `{"tags": ["ai"]}` gives 200; the versions list still has `total` 1, and `updated_at` is later than before. **Written only by whichever of versions and tagging is built second.** | E-9 |
