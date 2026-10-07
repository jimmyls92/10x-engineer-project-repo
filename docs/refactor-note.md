# Refactor note — Task 3.5

One refactor of `backend/app/api.py`, made with the test suite unchanged and green on both sides.

## The smell named

**Duplication.** The check "a `collection_id` sent in the request body must name an existing
collection, otherwise 400" was written out in full three times, in the three endpoints that accept a
`collection_id` in the body (line numbers at the "before" commit, `d962229`):

| Endpoint | Handler | Lines |
|---|---|---|
| `POST /prompts` | `create_prompt` | `api.py:156-159` |
| `PUT /prompts/{prompt_id}` | `update_prompt` | `api.py:195-198` |
| `PATCH /prompts/{prompt_id}` | `patch_prompt` | `api.py:248-251` |

Each copy was the same three lines:

```python
collection = storage.get_collection(<id>)
if not collection:
    raise HTTPException(status_code=400, detail="Collection not found")
```

**Why it is a smell:** any change to the rule (the lookup, the status code, the message) meant
editing three places, and missing one would leave the three endpoints disagreeing about the same
error.

## The two commit hashes

| | Commit | Message | CI run |
|---|---|---|---|
| **Before** | `d962229` | Log baseline before collection-check refactor | 37638799826 ✓ |
| **After** | `6a183ec` | Extract collection check into a helper | 37641437421 ✓ |

`d962229` only adds to the prompt log; its code is identical to the previous commit, `e83b9b8`.

## The refactor

- A new helper, `ensure_collection_exists(collection_id: str) -> None` (`api.py:49-64` at
  `6a183ec`), holds the lookup and the 400 once. It is placed under a new `Helpers` banner.
- The three copies are replaced by a call to it (`api.py:177`, `:214`, `:265` at `6a183ec`).
- **The helper lives in `api.py`, not `utils.py`.** It raises `HTTPException`, and the project's
  layering keeps every module below `api.py` free of HTTP.
- **The guard deciding whether to check stays at each call site, unchanged.** The three endpoints do
  not agree on it, and that disagreement is documented behaviour
  (`docs/API_REFERENCE.md`, *Known issues*):

  | Endpoint | Guard (unchanged) | Effect on `"collection_id": ""` |
  |---|---|---|
  | POST, PUT | `if prompt_data.collection_id:` | skipped, stored as is |
  | PATCH | `if changes.get("collection_id") is not None:` | looked up, rejected with 400 |

  Moving the guard into the helper would have unified the three and changed what an empty string
  does, which is a change in behaviour, not a refactor. Fixing that inconsistency is a separate
  decision and is not part of this change.

## Confirmation that the public interface and observable behaviour are unchanged

| Evidence | Result | What it shows |
|---|---|---|
| Suite on both commits (`pytest tests/ -v --cov=app`, Python 3.12 venv from `requirements.txt`, and CI) | **360 passed** on `d962229` and on `6a183ec` | Every behaviour the suite pins is the same before and after |
| `git diff --stat d962229 6a183ec -- backend/tests` | **Empty**; the whole diff is `backend/app/api.py` (25 insertions, 11 deletions) | No test was edited to accommodate the refactor |
| Coverage | **100%** of `app/` on both commits | Every changed line runs under the suite |
| Tests that reach each call site (`backend/tests/test_api.py`) | `:45` POST, `:926` PUT, `:1262` PATCH: unknown `collection_id` gives 400 `{"detail": "Collection not found"}` and stores nothing. `:1262` (parametrized): PATCH rejects `""`. `:304`, `:1122`: POST and PUT store `""` unchecked | The status, message and the different guards are each asserted, so a slip in any of them would fail a test |
| OpenAPI schema, `app.openapi()` dumped with sorted keys and hashed, built from each commit | **Same MD5** (`5afd9586566e2e8a74bef2279f3dd71f`) | Routes, parameters, request and response models are unchanged |
| `ruff check .` | All checks passed on both commits | The code is well formed. This is a side check, not evidence of behaviour |

The OpenAPI check can be repeated from the repository root:

```
git archive d962229 backend/app | tar -x -C /tmp/before
cd /tmp/before/backend && python -c "import json,app.api as a;print(json.dumps(a.app.openapi(),sort_keys=True))" | md5sum
cd -  && cd backend   && python -c "import json,app.api as a;print(json.dumps(a.app.openapi(),sort_keys=True))" | md5sum
```

## What was not changed

- **No route, status code, error message or response model.** The helper is not a route, so it does
  not appear in the API.
- **No test.**
- **Other repetition left as it is**, since only the named smell is in scope: the "get the prompt,
  else 404" lookup (`get_prompt`, `update_prompt`, `patch_prompt`), the field-by-field `Prompt(...)`
  built in PUT and PATCH, and the `"Collection not found"` 404s in the collection endpoints, which
  are a different rule (a path id, not a body id).
- The only other edit in the diff is that two blank lines that carried trailing spaces, after the
  removed blocks in POST and PUT, are now empty.
