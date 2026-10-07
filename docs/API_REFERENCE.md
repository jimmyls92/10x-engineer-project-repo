# PromptLab API Reference

Reference for every HTTP endpoint the PromptLab backend exposes. Every example on this page was run
with curl against a local server, and each response shown is the one that came back.

## Overview

| | |
|---|---|
| **Base URL** | `http://localhost:8000` (start the server from `backend/` with `uvicorn app.api:app --reload`) |
| **Format** | Request and response bodies are JSON. Send `Content-Type: application/json` with every body. |
| **Interactive docs** | FastAPI serves Swagger UI at `/docs`, ReDoc at `/redoc` and the schema at `/openapi.json`. The schema lists only the 200/201/204/422 responses, not the 400 and 404 described below. It also shows `title`, `content` and `tags` on `PATCH` as nullable, although a `null` there is rejected with 422. |
| **Storage** | In memory (`storage.py:26-27`). Every prompt and collection is lost when the server stops. |
| **Identifiers** | Server-assigned UUID4 strings, e.g. `"a1e56f1b-d59f-4ac7-ba1f-fab0321db73b"`. |
| **Timestamps** | UTC, in ISO 8601 **without a timezone suffix**, e.g. `"2026-09-29T11:40:48.551871"` (`models.py:37`). Read them as UTC. The fraction is left out when the microseconds are 0 (`"2026-09-29T11:40:48"`), so the width is not fixed. |

## Authentication notes

**None.** No endpoint requires a token, key or session, and no request header is checked.

CORS is open: `api.py:38-44` allows every origin, method and header, with credentials allowed. Any web
page can call the API from a browser.

## Error codes and response formats

### Response formats

Errors come back in one of three shapes.

**1. A message:** `detail` is a string. Used for 400, 404 and 405.

```json
{"detail": "Prompt not found"}
```

**2. A list of field errors:** `detail` is a list, one item per failed check. Used for 422. `loc`
says where the problem is (`["body", "<field>"]`, or just `["body"]` when there is no body at all;
`["body", "tags", <i>]` for one bad tag and `["query", "tag", <i>]` for one bad `?tag=` value, where
`<i>` is its position from 0), `msg` says what is wrong, and `ctx` carries the limit when there is
one.

```json
{"detail": [{"type": "string_too_long", "loc": ["body", "title"],
             "msg": "String should have at most 200 characters",
             "input": "aaaa…", "ctx": {"max_length": 200}}]}
```

The custom checks, a `null` `title`, `content` or `tags` on `PATCH` and the two rules on a list of
tags (more than 10, or a tag repeated), have `"type": "value_error"`, a `msg` that starts with
`"Value error, "`, and `"ctx": {"error": {}}`; see [PATCH /prompts/{prompt_id}](#patch-promptsprompt_id)
and [POST /prompts](#post-prompts).

**3. Plain text:** the body is `Internal Server Error` with `Content-Type: text/plain`, not JSON.
This is what an unhandled server error (500) returns; no request documented on this page produces
one. A client that always parses the error body as JSON would fail on it.

### Status codes

| Status | Meaning | `detail` | Returned by |
|---|---|---|---|
| **200** | Success, with a body | | every `GET`, `PUT` and `PATCH` |
| **201** | Created, with the new record as body | | `POST /prompts`, `POST /collections` |
| **204** | Deleted, **empty body** | | both `DELETE` endpoints |
| **400** | `collection_id` names no existing collection | `"Collection not found"` | `POST /prompts`, `PUT` and `PATCH /prompts/{prompt_id}` |
| **404** | No prompt or collection with that id | `"Prompt not found"` / `"Collection not found"` | every endpoint with an id in the path |
| **404** | Unknown path | `"Not Found"` | any undefined URL |
| **405** | Method not allowed on that path | `"Method Not Allowed"` | e.g. `PATCH /collections/{collection_id}` |
| **422** | The request body fails validation: a missing required field, a string too short or too long, a wrong type, a bad tag or tag list, malformed JSON, or no body; on `PATCH`, also an explicit `null` for `title`, `content` or `tags`. Or a `?tag=` value on `GET /prompts` is not a valid tag. | list of field errors | every endpoint that takes a body, and `GET /prompts`. The other query parameters and the path parameters are plain strings, so they never cause a 422. |

### Order of checks

When a request has more than one problem, only the first check that fails is reported:

1. **422**: the body is validated before the endpoint runs. `PUT /prompts/nope` with a body missing
   `title` returns 422, not 404. On `PATCH`, a `null` `title` or `content` is part of this step:
   `PATCH /prompts/nope` with `{"title": null}` returns 422, not 404, and
   `{"title": null, "collection_id": "nope"}` returns 422, not 400. The same holds for tags:
   `PATCH /prompts/nope` with `{"tags": ["Marketing"]}` returns 422, not 404.
2. **404**: the prompt in the path is looked up next (`api.py:208`, `:256`).
3. **400**: the `collection_id` is checked next (`api.py:213`, `:264`). `PUT /prompts/nope` with a
   valid body and an unknown `collection_id` returns 404, not 400.

## Data models

Constraints are enforced on the request body. A body that breaks one is rejected with 422. Length
limits count characters as sent; values are not trimmed, so a title of a single space is accepted.
Keys a model does not declare, such as `id` or `created_at`, are silently dropped: a client cannot
choose them.

### Prompt

| Field | Type | Sent by | Constraint |
|---|---|---|---|
| `title` | string | client, **required** | 1 to 200 characters |
| `content` | string | client, **required** | at least 1 character |
| `description` | string or null | client, optional | at most 500 characters; default `null` |
| `collection_id` | string or null | client, optional | must name an existing collection (checked by the endpoint, not the model); `""` is accepted by `POST` and `PUT` but rejected by `PATCH` (see [Known issues](#known-issues)); default `null` |
| `tags` | list of strings | client, optional | each tag 1 to 32 characters of lowercase letters and digits, with single hyphens between them (`"code-review"`; not `"Python"`, `"-ai"` or `"a--b"`); at most 10 tags, none repeated; kept in the order sent, never sorted or lowercased; default `[]` |
| `id` | string | server | UUID4 |
| `created_at` | timestamp | server | set on create, never changed |
| `updated_at` | timestamp | server | set on create, refreshed by `PUT` and by a `PATCH` that carries at least one field |

Request bodies: `POST` takes the five client fields. `PUT` takes the same five and replaces them all:
an optional field left out is reset to its default, `null`, or `[]` for `tags`. `PATCH` takes any
subset of them; see its endpoint.

### Collection

| Field | Type | Sent by | Constraint |
|---|---|---|---|
| `name` | string | client, **required** | 1 to 100 characters; need not be unique |
| `description` | string or null | client, optional | at most 500 characters; default `null` |
| `id` | string | server | UUID4 |
| `created_at` | timestamp | server | set on create |

A collection has no `updated_at`: no endpoint edits a collection.

### TagSummary

One tag in use. Computed on each request from the stored prompts, never stored or sent by a client.

| Field | Type | Meaning |
|---|---|---|
| `name` | string | the tag |
| `prompt_count` | integer | how many prompts carry it; always at least 1 |

### List wrappers

| Model | Shape | Returned by |
|---|---|---|
| `PromptList` | `{"prompts": [Prompt, …], "total": <int>}` | `GET /prompts` |
| `CollectionList` | `{"collections": [Collection, …], "total": <int>}` | `GET /collections` |
| `TagList` | `{"tags": [TagSummary, …], "total": <int>}` | `GET /tags` |

`total` is the number of items in the list, counted after any filter. In a `TagList` it counts tags,
not prompts.

## Endpoints

Examples use the ids from one recorded run: collection `c7682450-d542-4e56-b228-4bb3d6608a34` and
prompt `a1e56f1b-d59f-4ac7-ba1f-fab0321db73b`. Substitute your own. On Windows, run them in Git Bash,
or call `curl.exe` in PowerShell (`curl` there is an alias for `Invoke-WebRequest`).

| Method | Path | Purpose | Success |
|---|---|---|---|
| `GET` | [`/health`](#get-health) | Service status and version | 200 |
| `GET` | [`/prompts`](#get-prompts) | List prompts, with optional filters | 200 |
| `POST` | [`/prompts`](#post-prompts) | Create a prompt | 201 |
| `GET` | [`/prompts/{prompt_id}`](#get-promptsprompt_id) | Get one prompt | 200 |
| `PUT` | [`/prompts/{prompt_id}`](#put-promptsprompt_id) | Replace a prompt in full | 200 |
| `PATCH` | [`/prompts/{prompt_id}`](#patch-promptsprompt_id) | Update some fields of a prompt | 200 |
| `DELETE` | [`/prompts/{prompt_id}`](#delete-promptsprompt_id) | Delete a prompt | 204 |
| `GET` | [`/collections`](#get-collections) | List collections | 200 |
| `POST` | [`/collections`](#post-collections) | Create a collection | 201 |
| `GET` | [`/collections/{collection_id}`](#get-collectionscollection_id) | Get one collection | 200 |
| `DELETE` | [`/collections/{collection_id}`](#delete-collectionscollection_id) | Delete a collection, unfiling its prompts | 204 |
| `GET` | [`/tags`](#get-tags) | List the tags in use, with their prompt counts | 200 |

### GET /health

Reports that the server is answering. It checks nothing else and does not touch storage.

```bash
curl http://localhost:8000/health
```

**200 OK**

```json
{"status": "healthy", "version": "0.1.0"}
```

`status` is always `"healthy"`. **Errors:** none.

### GET /prompts

Lists prompts, newest `created_at` first.

| Query parameter | Effect |
|---|---|
| `collection_id` | Optional. Keep only prompts filed in this collection. An unknown id is **not** an error: it returns an empty list. |
| `search` | Optional. Keep only prompts whose `title` or `description` contains the text, ignoring case. `content` is **not** searched. |
| `tag` | Optional and **repeatable** (`?tag=marketing&tag=email`). Keep only prompts that carry **every** tag given; the match is exact. A tag no prompt carries is not an error: it returns an empty list. A repeated value counts once. |

An absent or empty parameter is ignored, so `?tag=` alone lists every prompt. All three can be
combined; they run in the order collection, search, tag.

```bash
curl "http://localhost:8000/prompts?collection_id=c7682450-d542-4e56-b228-4bb3d6608a34&search=tagline&tag=marketing"
```

**200 OK**, a [`PromptList`](#list-wrappers)

```json
{
  "prompts": [
    {
      "title": "Product tagline",
      "content": "Write a tagline for {{product}} aimed at {{audience}}.",
      "description": "Short marketing tagline",
      "collection_id": "c7682450-d542-4e56-b228-4bb3d6608a34",
      "tags": ["marketing", "copywriting"],
      "id": "a1e56f1b-d59f-4ac7-ba1f-fab0321db73b",
      "created_at": "2026-10-06T13:39:32.054321",
      "updated_at": "2026-10-06T13:39:32.054321"
    }
  ],
  "total": 1
}
```

With no match: `{"prompts": [], "total": 0}`.

| Status | When |
|---|---|
| 422 | A `tag` value is not a valid tag or is over 32 characters (below). An empty value is not an error. |

```bash
curl "http://localhost:8000/prompts?tag=Marketing"
```

**422 Unprocessable Entity**

```json
{"detail": [{"type": "string_pattern_mismatch", "loc": ["query", "tag", 0],
             "msg": "String should match pattern '^([a-z0-9]+(-[a-z0-9]+)*)?$'",
             "input": "Marketing", "ctx": {"pattern": "^([a-z0-9]+(-[a-z0-9]+)*)?$"}}]}
```

### POST /prompts

Creates a prompt. Body: the five client fields of [Prompt](#prompt); `title` and `content` are
required. The server assigns `id`, `created_at` and `updated_at`.

```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{"title": "Product tagline",
       "content": "Write a tagline for {{product}} aimed at {{audience}}.",
       "description": "Short marketing tagline",
       "collection_id": "c7682450-d542-4e56-b228-4bb3d6608a34",
       "tags": ["marketing", "copywriting"]}'
```

**201 Created**, the stored [Prompt](#prompt)

```json
{
  "title": "Product tagline",
  "content": "Write a tagline for {{product}} aimed at {{audience}}.",
  "description": "Short marketing tagline",
  "collection_id": "c7682450-d542-4e56-b228-4bb3d6608a34",
  "tags": ["marketing", "copywriting"],
  "id": "a1e56f1b-d59f-4ac7-ba1f-fab0321db73b",
  "created_at": "2026-10-06T13:39:32.054321",
  "updated_at": "2026-10-06T13:39:32.054321"
}
```

`created_at` and `updated_at` are set separately on a new prompt, so they may differ by a few
microseconds or be equal, depending on how fine the server's clock is. Do not rely on either.

| Status | When |
|---|---|
| 400 | `collection_id` is non-empty and names no collection: `{"detail": "Collection not found"}` |
| 422 | A constraint in [Prompt](#prompt) fails, e.g. `{"title": "t"}` gives `"loc": ["body", "content"], "msg": "Field required"`. For tags, see below. |

`"collection_id": ""` is **not** checked and is stored as `""` (see [Known issues](#known-issues)).

A bad tag is reported at its own position, with Pydantic's message. With
`"tags": ["ai", "Marketing"]`:

```json
{"detail": [{"type": "string_pattern_mismatch", "loc": ["body", "tags", 1],
             "msg": "String should match pattern '^[a-z0-9]+(-[a-z0-9]+)*$'",
             "input": "Marketing", "ctx": {"pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"}}]}
```

A list that breaks a list rule is reported on the list, `"loc": ["body", "tags"]`:

| `tags` sent | `msg` |
|---|---|
| 11 tags | `"Value error, a prompt can have at most 10 tags; delete a tag before including another"` |
| `["ai", "ai"]` | `"Value error, tags must not repeat a tag"` |

The count is checked first, so 11 tags with one repeated get only the count message. `"tags": null`
gives `"Input should be a valid list"`. The same rules and messages apply on `PUT` and `PATCH`.

### GET /prompts/{prompt_id}

Returns one prompt.

```bash
curl http://localhost:8000/prompts/a1e56f1b-d59f-4ac7-ba1f-fab0321db73b
```

**200 OK**: the same [Prompt](#prompt) object as in the `POST /prompts` response.

| Status | When |
|---|---|
| 404 | No prompt has that id: `{"detail": "Prompt not found"}` |

### PUT /prompts/{prompt_id}

Replaces a prompt in full. Body: the same as `POST /prompts`. **Every client field is taken from the
body**: an optional field left out is reset to its default, so omitting `collection_id` unfiles the
prompt and omitting `tags` clears them. `id` and `created_at` are kept; `updated_at` is set to now.

```bash
curl -X PUT http://localhost:8000/prompts/a1e56f1b-d59f-4ac7-ba1f-fab0321db73b \
  -H "Content-Type: application/json" \
  -d '{"title": "Product tagline v2",
       "content": "Write a punchy tagline for {{product}}.",
       "description": "Shorter version",
       "collection_id": "c7682450-d542-4e56-b228-4bb3d6608a34",
       "tags": ["marketing", "copywriting"]}'
```

**200 OK**, the stored [Prompt](#prompt)

```json
{
  "title": "Product tagline v2",
  "content": "Write a punchy tagline for {{product}}.",
  "description": "Shorter version",
  "collection_id": "c7682450-d542-4e56-b228-4bb3d6608a34",
  "tags": ["marketing", "copywriting"],
  "id": "a1e56f1b-d59f-4ac7-ba1f-fab0321db73b",
  "created_at": "2026-10-06T13:39:32.054321",
  "updated_at": "2026-10-06T13:39:33.858796"
}
```

| Status | When |
|---|---|
| 404 | No prompt has that id: `{"detail": "Prompt not found"}`. Checked before the collection. |
| 400 | `collection_id` is non-empty and names no collection: `{"detail": "Collection not found"}` |
| 422 | A constraint in [Prompt](#prompt) fails, e.g. no `title`. Checked before the 404. |

As with `POST`, `"collection_id": ""` is stored unchecked.

### PATCH /prompts/{prompt_id}

Updates only the fields present in the body; every field is optional. **A key's presence is what
counts, not its value**:

| Body | Effect |
|---|---|
| key left out | field kept as it is |
| `"description": null` | description cleared |
| `"collection_id": null` | prompt unfiled |
| `"title": null` or `"content": null` | **422**, prompt left unchanged: a title or content cannot be cleared; leave the key out to keep it |
| `"tags": [...]` | tags replaced by the list sent, under the same rules as on `POST` |
| `"tags": []` | tags cleared |
| `"tags": null` | **422**, prompt left unchanged, with the same message as a `null` title: `"Value error, tags cannot be null; send a value or omit the field to keep the current one"` |
| `{}` | nothing changes, **`updated_at` included** |

A body with at least one field sets `updated_at` to now; `id` and `created_at` are kept.

```bash
curl -X PATCH http://localhost:8000/prompts/a1e56f1b-d59f-4ac7-ba1f-fab0321db73b \
  -H "Content-Type: application/json" \
  -d '{"description": "Edited with PATCH"}'
```

**200 OK**, the stored [Prompt](#prompt): only `description` and `updated_at` changed

```json
{
  "title": "Product tagline v2",
  "content": "Write a punchy tagline for {{product}}.",
  "description": "Edited with PATCH",
  "collection_id": "c7682450-d542-4e56-b228-4bb3d6608a34",
  "tags": ["marketing", "copywriting"],
  "id": "a1e56f1b-d59f-4ac7-ba1f-fab0321db73b",
  "created_at": "2026-10-06T13:39:32.054321",
  "updated_at": "2026-10-06T13:39:34.165743"
}
```

| Status | When |
|---|---|
| 404 | No prompt has that id: `{"detail": "Prompt not found"}`. Checked before the collection. |
| 400 | `collection_id` is present, not null, and names no collection, **including `""`**: `{"detail": "Collection not found"}` |
| 422 | A field sent breaks its constraint, e.g. `"title": ""` gives `"msg": "String should have at least 1 character"`, or a bad tag (as on [POST](#post-prompts)); or `title`, `content` or `tags` is `null` (below). Checked before the 404 and 400. |

A `null` `title` (the same holds for `content` and `tags`):

```bash
curl -X PATCH http://localhost:8000/prompts/a1e56f1b-d59f-4ac7-ba1f-fab0321db73b \
  -H "Content-Type: application/json" \
  -d '{"title": null}'
```

**422 Unprocessable Entity**; the stored prompt is unchanged

```json
{"detail": [{"type": "value_error", "loc": ["body", "title"],
             "msg": "Value error, title cannot be null; send a value or omit the field to keep the current one",
             "input": null, "ctx": {"error": {}}}]}
```

### DELETE /prompts/{prompt_id}

Deletes a prompt permanently.

```bash
curl -X DELETE http://localhost:8000/prompts/a1e56f1b-d59f-4ac7-ba1f-fab0321db73b
```

**204 No Content**, empty body.

| Status | When |
|---|---|
| 404 | No prompt has that id: `{"detail": "Prompt not found"}` |

### GET /collections

Lists every collection, in the order they were created. Takes no parameters.

```bash
curl http://localhost:8000/collections
```

**200 OK**, a [`CollectionList`](#list-wrappers)

```json
{
  "collections": [
    {
      "name": "Marketing",
      "description": "Prompts for campaign copy",
      "id": "c7682450-d542-4e56-b228-4bb3d6608a34",
      "created_at": "2026-10-06T13:39:30.966330"
    }
  ],
  "total": 1
}
```

**Errors:** none.

### POST /collections

Creates a collection. Body: `name` (required) and `description` (optional), see
[Collection](#collection). Names need not be unique.

```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "Marketing", "description": "Prompts for campaign copy"}'
```

**201 Created**, the stored [Collection](#collection)

```json
{
  "name": "Marketing",
  "description": "Prompts for campaign copy",
  "id": "c7682450-d542-4e56-b228-4bb3d6608a34",
  "created_at": "2026-10-06T13:39:30.966330"
}
```

| Status | When |
|---|---|
| 422 | A constraint in [Collection](#collection) fails, e.g. `{}` gives `"loc": ["body", "name"], "msg": "Field required"` |

### GET /collections/{collection_id}

Returns one collection. Its prompts are not included; list them with
`GET /prompts?collection_id=<id>`.

```bash
curl http://localhost:8000/collections/c7682450-d542-4e56-b228-4bb3d6608a34
```

**200 OK**: the same [Collection](#collection) object as in the `POST /collections` response.

| Status | When |
|---|---|
| 404 | No collection has that id: `{"detail": "Collection not found"}` |

### DELETE /collections/{collection_id}

Deletes a collection. **Its prompts are kept, not deleted**: each one that was filed in it has its
`collection_id` set to `null`. Their `updated_at` is left alone.

```bash
curl -X DELETE http://localhost:8000/collections/c7682450-d542-4e56-b228-4bb3d6608a34
```

**204 No Content**, empty body.

| Status | When |
|---|---|
| 404 | No collection has that id: `{"detail": "Collection not found"}` |

### GET /tags

Lists every tag carried by at least one prompt, with how many prompts carry it, sorted by name
(Python's string order, so `"a-b"` comes before `"a1"`). The list is computed from the stored prompts
on each request: a tag appears when a prompt first carries it, and disappears when the last prompt
carrying it is edited or deleted. Takes no parameters.

```bash
curl http://localhost:8000/tags
```

**200 OK**, a [`TagList`](#list-wrappers). Here two prompts carry `marketing`: the one above, and a
second, `"Launch email"`, tagged `["marketing", "email"]`.

```json
{
  "tags": [
    {"name": "copywriting", "prompt_count": 1},
    {"name": "email", "prompt_count": 1},
    {"name": "marketing", "prompt_count": 2}
  ],
  "total": 3
}
```

With no tagged prompt: `{"tags": [], "total": 0}`. **Errors:** none.

## Known issues

Both are current behaviour, described as the code does it, and are **not fixed**.

| Issue | Where | Effect |
|---|---|---|
| **An empty `collection_id` is handled inconsistently** | `api.py:176`, `:213`, `:264` | `POST` and `PUT` test truthiness, so `""` is stored without a check. `PATCH` tests `is not None`, so `""` is looked up and rejected with 400. |
| **A prompt with `collection_id: ""` cannot be listed by collection** | `api.py:115` | `GET /prompts?collection_id=` treats the empty value as absent and returns every prompt, so there is no way to select only the prompts stored with `""`. |
