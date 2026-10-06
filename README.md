# PromptLab

**A REST API for storing and organising AI prompts.**

## Project overview and purpose

PromptLab is an internal tool for AI engineers: a place to keep prompt templates, group them into
collections, and find them again. Think "Postman for prompts". A prompt has a title, a body that may
contain template variables such as `{{code}}`, an optional description, an optional collection it
belongs to, and up to ten tags. Collections are flat named groups; a prompt belongs to at most one.
Tags cut across collections: a prompt about reviewing Python code can be tagged both `code-review`
and `python`. Template variables are stored as plain text: the service does not parse them or fill
them in.

The service is a FastAPI application with **in-memory storage** — everything lives in a dictionary in
the server process and is lost when it stops. That is deliberate for now; swapping in a database is a
later module.

## Features list

- **Prompt storage and retrieval.** Save a prompt as a title, a body and an optional description,
  then fetch it by id or list every prompt. The server assigns each prompt a UUID and its
  `created_at` / `updated_at` timestamps; the client never sets them. Deleting a prompt removes it
  for good.
- **Full and partial prompt updates.** `PUT` replaces a prompt in full: every field comes from the
  body, so an optional field that is left out is reset (leaving out `collection_id` unfiles the
  prompt). `PATCH` changes only the fields the body carries: an explicit `null` clears the
  description or unfiles the prompt, and a missing key leaves a field alone. A title or body cannot
  be cleared, so `PATCH` refuses a `null` for either with `422`. Both keep `created_at` and refresh `updated_at`, except that a
  `PATCH` with an empty body changes nothing, not even the timestamp.
- **Collections for grouping prompts.** Create a named collection with an optional description,
  then file a prompt in it by setting `collection_id` on create, `PUT` or `PATCH`. The id must name
  an existing collection, or the request is refused with `400`. A prompt sits in at most one
  collection, and a collection cannot be renamed after it is created.
- **Non-destructive collection deletion.** Deleting a collection keeps its prompts: each one is
  unfiled (its `collection_id` is cleared) and its `updated_at` is left as it was, since the
  client did not edit it.
- **Tags.** A prompt carries a list of tags, set on create, `PUT` or `PATCH` and kept in the order
  sent. A tag is 1–32 lowercase letters and digits, with single hyphens between them
  (`code-review`, not `Code Review` or `-ai`); a prompt has at most 10, none repeated. `PUT`
  without `tags` clears them, `PATCH` without `tags` keeps them, and `"tags": []` clears them on
  either. `GET /tags` lists every tag in use, sorted by name, with how many prompts carry it; it is
  computed from the stored prompts, so a tag no prompt carries any more disappears.
- **Filtering and search.** `GET /prompts?collection_id=` returns only the prompts in that
  collection; an unknown id gives an empty list, not an error. `?search=` keeps the prompts whose
  title or description contains the text, ignoring case. The prompt body is not searched. `?tag=`
  keeps the prompts that carry the tag; repeat it (`?tag=ai&tag=python`) to keep only the prompts
  that carry **every** tag given. An unknown tag gives an empty list. All three parameters can be
  combined.
- **Newest-first ordering.** Prompt lists are always sorted by creation date, newest first. The
  order is fixed; no parameter changes it.
- **Input validation.** A title must be 1–200 characters, the body must not be empty, a description
  is at most 500 characters, tags follow the rules above and a collection name is 1–100 characters.
  A body that breaks a rule is rejected with `422` and a per-field error before it reaches storage;
  `PATCH` applies the same rules to the fields it carries. A `?tag=` value that is not a valid tag
  is also rejected with `422`.
- **Health check and interactive API docs.** `GET /health` returns `{"status": "healthy"}` and the
  service version. FastAPI generates Swagger UI (`/docs`) and ReDoc (`/redoc`) pages from the code,
  where every endpoint can be tried from the browser.

---

## Prerequisites and installation

### Prerequisites

- **Python 3.10–3.12** (`python --version`). **Not 3.13** — the pinned `pydantic==2.5.3` needs
  `pydantic-core`, which publishes no wheel for 3.13, and its source build needs a Rust toolchain. Tested on **3.12.13**.
- **git**

Nothing else. No database, no message broker, no API keys — the service calls no external system.
The `config.yaml` at the repository root configures an AI coding assistant; the service never reads
it, and it is not needed to install or run PromptLab.

### Installation

```bash
git clone <your-repo-url>
cd 10x-engineer-project-repo/backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

`requirements.txt` lives in `backend/`, so install from there.

---

## Quick start guide

From installation to a stored, tagged, searchable prompt in five steps.

> **The commands below are for a POSIX shell** (bash, zsh, Git Bash). In Windows PowerShell, `curl`
> is an alias for `Invoke-WebRequest`, `\` does not continue a line, and the quotes inside the JSON
> bodies are not passed through as written. On Windows, use Git Bash, or send the same requests from
> the Swagger UI at http://localhost:8000/docs.

### 1. Start the server

From `backend/`, with the virtual environment active:

```bash
uvicorn app.api:app --reload
```

This must be run **from the `backend/` directory** — the application is imported as
`app.api`, which only resolves when `backend/` is the working directory.

> **Do not use `python main.py`.** It is the repository's original entry point and it does not start a
> server: `main.py:10` passes the application object together with `reload=True`, and uvicorn only
> supports reload for an application given as an import string. `uvicorn app.api:app --reload` is
> the working equivalent.

| What | Where |
|---|---|
| API | http://localhost:8000 |
| Interactive docs (Swagger UI) | http://localhost:8000/docs |
| Alternative docs (ReDoc) | http://localhost:8000/redoc |
| OpenAPI schema | http://localhost:8000/openapi.json |

Leave it running and use a second terminal for the next steps. Stop it with `Ctrl+C`.

### 2. Check it is alive

```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"0.1.0"}
```

### 3. Create a collection

```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "Code review", "description": "Prompts for reviewing pull requests"}'
```

The response is `201` with the new collection. Copy its `id`: the next step needs it.

```json
{"name":"Code review","description":"Prompts for reviewing pull requests","id":"39bb6d01-c454-4f7a-9da7-bb1afc88f4e6","created_at":"2026-10-06T13:37:21.739605"}
```

### 4. Save a tagged prompt in it

Replace `<collection-id>` with the id from step 3:

```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{"title": "Review a diff", "content": "Review this diff and list any bugs: {{diff}}", "collection_id": "<collection-id>", "tags": ["code-review", "python"]}'
```

The response is `201` with the stored prompt. The server has added its `id` and both timestamps:

```json
{"title":"Review a diff","content":"Review this diff and list any bugs: {{diff}}","description":null,"collection_id":"39bb6d01-c454-4f7a-9da7-bb1afc88f4e6","tags":["code-review","python"],"id":"6f037c0a-2822-40d3-ba78-a78a88fe72c1","created_at":"2026-10-06T13:37:22.617241","updated_at":"2026-10-06T13:37:22.617241"}
```

### 5. Find it again

Search matches titles and descriptions, ignoring case:

```bash
curl "http://localhost:8000/prompts?search=review"
```

```json
{"prompts":[{"title":"Review a diff","content":"Review this diff and list any bugs: {{diff}}","description":null,"collection_id":"39bb6d01-c454-4f7a-9da7-bb1afc88f4e6","tags":["code-review","python"],"id":"6f037c0a-2822-40d3-ba78-a78a88fe72c1","created_at":"2026-10-06T13:37:22.617241","updated_at":"2026-10-06T13:37:22.617241"}],"total":1}
```

`curl "http://localhost:8000/prompts?tag=code-review"` and
`curl "http://localhost:8000/prompts?collection_id=<collection-id>"` list the same prompt in the same
shape. To see which tags are in use:

```bash
curl http://localhost:8000/tags
```

```json
{"tags":[{"name":"code-review","prompt_count":1},{"name":"python","prompt_count":1}],"total":2}
```

Your ids and timestamps will differ. Storage is in memory, so restarting the server empties it.

---

## API endpoint summary with examples

The examples assume a POSIX shell (see Quick start guide) and this variable:

```bash
API=http://localhost:8000
```

| Method | Endpoint | What it does | Example |
|---|---|---|---|
| `GET` | `/health` | Service status and version | `curl $API/health` |
| `GET` | `/prompts` | List prompts, newest first. Optional `?collection_id=`, `?search=` and repeatable `?tag=` | `curl "$API/prompts?tag=code-review&tag=python"` |
| `GET` | `/prompts/{id}` | Fetch one prompt; 404 if it does not exist | `curl $API/prompts/<id>` |
| `POST` | `/prompts` | Create a prompt; 201 with the created prompt | `curl -X POST $API/prompts -H "Content-Type: application/json" -d '{"title": "Review a diff", "content": "List bugs in: {{diff}}"}'` |
| `PUT` | `/prompts/{id}` | **Full** replacement: an omitted field is reset | `curl -X PUT $API/prompts/<id> -H "Content-Type: application/json" -d '{"title": "Review a diff", "content": "List bugs in: {{diff}}"}'` (no `collection_id`, so the prompt is unfiled) |
| `PATCH` | `/prompts/{id}` | **Partial** update: only the fields sent change | `curl -X PATCH $API/prompts/<id> -H "Content-Type: application/json" -d '{"description": "For small PRs"}'` |
| `DELETE` | `/prompts/{id}` | Delete a prompt; 204 with no body | `curl -X DELETE $API/prompts/<id>` |
| `GET` | `/collections` | List all collections | `curl $API/collections` |
| `GET` | `/collections/{id}` | Fetch one collection; 404 if it does not exist | `curl $API/collections/<id>` |
| `POST` | `/collections` | Create a collection; 201 with the created collection | `curl -X POST $API/collections -H "Content-Type: application/json" -d '{"name": "Code review"}'` |
| `DELETE` | `/collections/{id}` | Delete a collection and **unfile** its prompts | `curl -X DELETE $API/collections/<id>` |
| `GET` | `/tags` | List the tags in use, sorted by name, with each one's prompt count | `curl $API/tags` |

`search` matches case-insensitively against a prompt's title and description. `tag` keeps the prompts
that carry every tag given; an empty `?tag=` is ignored. `GET /prompts` always sorts by creation date,
newest first; it is not a client-controlled parameter.

**Status codes.** A missing addressed resource is `404`. A body that names a collection which does not
exist is `400`. A body that breaks a field constraint — an empty title, a title over 200 characters,
a tag such as `"Python"`, 11 tags or a repeated tag — is `422`, produced by validation before the
handler runs. `PATCH` also answers `422` to an explicit `null` title, content or tags, before it
looks up the prompt. On `GET /prompts`, a `?tag=` value that is not a valid tag is `422` too.

---

## Development setup

Follow **Prerequisites and installation** first. `requirements.txt` holds the development tools
(`pytest`, `pytest-cov`, `httpx`) as well as the runtime packages, so that one install is all a
contributor needs. Every command below runs from `backend/` with the virtual environment active.

### Run the server with auto-reload

```bash
uvicorn app.api:app --reload
```

`--reload` restarts the server whenever a `.py` file under `backend/` changes. Every restart empties the
in-memory storage, so data created before an edit is gone after it.

### Run the tests

```bash
pytest tests/ -v
```

Every test should pass, and **no server needs to be running**. The suite has one file per module:

| File | Covers |
|---|---|
| `tests/test_api.py` | Every endpoint, through FastAPI's `TestClient`: success, error cases (404, 400, 422), edge cases and query parameters |
| `tests/test_models.py` | The Pydantic models and `generate_id` / `get_current_time`: validation, defaults, serialization |
| `tests/test_utils.py` | Each helper in `utils.py`, with its error conditions |
| `tests/test_storage.py` | Each `Storage` method: CRUD operations, persistence within a session, edge cases |

The three unit-test files call their module directly, without HTTP; `test_storage.py` gives each
test its own fresh `Storage`. An autouse fixture in `tests/conftest.py` empties the shared storage
before and after every test, so no test depends on data another test left behind. `conftest.py`
also provides `client`, `sample_prompt_data` and `sample_collection_data` fixtures, and
`ticking_clock`, which makes `get_current_time()` advance 1 µs per call so that tests comparing
timestamps are deterministic.

### Measure test coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

This prints the coverage of each module under `app/`, with the line numbers no test reaches.

---

## Docker usage

Docker runs the API without a local Python install. `backend/Dockerfile` builds the image;
`docker-compose.yml`, at the repository root, runs it for development with hot reload.

### Prerequisites

- **Docker** with **Compose** (Docker Desktop on Windows and macOS), with the engine running.

### Start it

From the repository root:

```bash
docker-compose up --build
```

`docker compose up --build` (Compose v2 syntax) does the same. The API is at
http://localhost:8000, with the same URLs as in **Quick start guide**. Check it:

```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"0.1.0"}
```

### What compose sets up

| Setting | Value | Why |
|---|---|---|
| Port | `8000:8000` | Host port 8000 reaches uvicorn in the container |
| `PYTHONUNBUFFERED=1` | | Logs appear in `docker-compose logs` as each request happens |
| `PYTHONDONTWRITEBYTECODE=1` | | Stops the container writing `__pycache__/` into your `backend/app/` |
| Volume | `./backend/app:/app/app` | The container runs your files, not the copy in the image |
| Command | `uvicorn … --reload` | Restarts the server when a file in `backend/app/` changes |

Only `backend/app/` is mounted. After changing `requirements.txt` or the `Dockerfile`, run
`docker-compose up --build` again.

### Stop it

`Ctrl+C`, or `docker-compose down` from another terminal. Storage is in memory: every
stop or reload empties it.

### Run the image without compose

```bash
docker build -t promptlab backend
docker run --rm -p 8000:8000 promptlab
```

This runs the image's own command: no reload and no mounted code. The image starts uvicorn
directly; see the note on `python main.py` in **Quick start guide**.

### Tests

The image holds only `app/` and `requirements.txt`, not `tests/`. Run the tests locally, as
in **Development setup**.

---

## Contributing guidelines

1. **Report a bug or propose a change** by opening an issue on the GitHub repository. Say what you
   expected, what happened, and the request that shows it.
2. **Branch from `main`** for your change. Never commit to `main` directly.
3. **Keep the docs true to the code.** If your change alters behaviour, update this README, the
   docstrings and the API reference in the same branch.
4. **Run the tests before you push.** `pytest tests/ -v` must pass in full; see *Development setup*.
5. **Write commits the way the history is written:**
   - an imperative subject of **50 characters or fewer**, naming the change;
   - a body of **at most two sentences** saying *why*, not *what*;
   - **one logical change per commit** — if the message needs an "Also…", it is two commits;
   - **never squash** — the history is kept as it happened.
6. **Open a pull request against `main`** on GitHub, describing what changed and how you checked it.
