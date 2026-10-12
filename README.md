# PromptLab

**A web app and REST API for storing and organising AI prompts.**

## Project overview and purpose

PromptLab is an internal tool for AI engineers: a place to keep prompt templates, group them into
collections, and find them again. Think "Postman for prompts". A prompt has a title, a body that may
contain template variables such as `{{code}}`, an optional description, an optional collection it
belongs to, and up to ten tags. Collections are flat named groups; a prompt belongs to at most one.
Tags cut across collections: a prompt about reviewing Python code can be tagged both `code-review`
and `python`. Template variables are stored as plain text: the service does not parse them or fill
them in.

PromptLab has two parts. The **web app** (`frontend/`, React with Vite) is what a user opens in a
browser: a Prompts screen to list, search, filter, read, create, edit and delete prompts, and a
Collections screen to list, create and delete collections. It holds no data of its own and calls
the **API** (`backend/`) for everything. The API can also be used directly, with curl or from its
interactive docs.

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
- **Prompt versions.** Every prompt keeps the history of its `content`. Creating a prompt saves
  version 1; a `PUT` or `PATCH` whose content differs from the latest version, even by one space,
  saves the next one. Edits to the title, description, collection or tags save nothing, nor does a
  request that fails. `GET /prompts/{id}/versions` lists the history, oldest first by default
  (`?order=desc` for the latest first, `?limit=` to keep the first few); `GET
  /prompts/{id}/versions/{version}` returns one version. To go back to an earlier wording, send it
  as the new content with `PATCH`: that saves a new version, so nothing is lost. The history is
  never shown in the prompt itself, and it is deleted with its prompt.
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
- **Web app.** Two screens. **Prompts** lists every prompt, newest first; a search box and a
  collection filter take effect when **Apply** is pressed, and a status line says what is shown.
  Selecting a prompt opens its detail under its row; prompts are created and edited in a form
  window and deleted after a confirmation. **Collections** lists, creates and deletes collections.
  Each screen shows a loading state, an error message when the API fails or cannot be reached, and
  an empty state; forms check their fields before sending. Tags and versions are not shown in the
  web app, and editing a prompt there keeps its tags. The scope is set by `specs/frontend.md`.
- **Health check and interactive API docs.** `GET /health` returns `{"status": "healthy"}` and the
  service version. FastAPI generates Swagger UI (`/docs`) and ReDoc (`/redoc`) pages from the code,
  where every endpoint can be tried from the browser.

---

## Prerequisites and installation

### Prerequisites

- **Python 3.10–3.12** (`python --version`). **Not 3.13** — the pinned `pydantic==2.5.3` needs
  `pydantic-core`, which publishes no wheel for 3.13, and its source build needs a Rust toolchain. Tested on **3.12.13**.
- **git**
- **Node.js `^20.19.0` or `>=22.12.0`, with npm**, for the web app only (`node --version`). Vite 8
  requires one of those. Tested on Node 24.

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

Then the web app, from the repository root in a second terminal:

```bash
cd frontend
npm install
```

`frontend/.env.example` documents the one setting, `VITE_API_BASE_URL`, the address of the API. In
development it can be left unset: the dev server then calls `http://localhost:8000`. To set it,
copy the file to `frontend/.env` and edit it.

---

## Quick start guide

Start the API and the web app, as the course's verification does, then optionally use the API
directly: from installation to a stored, tagged, searchable prompt.

> **The commands below are for a POSIX shell** (bash, zsh, Git Bash). In Windows PowerShell, `curl`
> is an alias for `Invoke-WebRequest`, `\` does not continue a line, and the quotes inside the JSON
> bodies are not passed through as written. On Windows, use Git Bash, or send the same requests from
> the Swagger UI at http://localhost:8000/docs.

### 1. Start the API

Terminal 1, from `backend/`, with the virtual environment active:

```bash
cd backend && python main.py
```

This must be run **from the `backend/` directory**: the application is imported as `app.api`, which
only resolves when `backend/` is the working directory. It starts the server with auto-reload,
listening on every network interface (`0.0.0.0`). `uvicorn app.api:app --reload` is equivalent,
but listens on `localhost` only.

| What | Where |
|---|---|
| API | http://localhost:8000 |
| Interactive docs (Swagger UI) | http://localhost:8000/docs |
| Alternative docs (ReDoc) | http://localhost:8000/redoc |
| OpenAPI schema | http://localhost:8000/openapi.json |

Leave it running. Stop it with `Ctrl+C`.

### 2. Start the web app

Terminal 2, from the repository root:

```bash
cd frontend && npm run dev
```

Then open **http://localhost:5173**. The Prompts screen loads the prompts from the API, and the
header switches to Collections. Stop it with `Ctrl+C`.

The API allows browser requests only from `http://localhost:5173` unless `CORS_ORIGINS` says
otherwise, so if Vite picks another port because 5173 is taken, every request fails with "Can't
reach the server". Free the port, or start the API with that address in `CORS_ORIGINS` (see
**Development setup**).

### 3. Use the API directly: check it is alive

The remaining steps are optional and use a third terminal.

```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"0.1.0"}
```

### 4. Create a collection

```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "Code review", "description": "Prompts for reviewing pull requests"}'
```

The response is `201` with the new collection. Copy its `id`: the next step needs it.

```json
{"name":"Code review","description":"Prompts for reviewing pull requests","id":"39bb6d01-c454-4f7a-9da7-bb1afc88f4e6","created_at":"2026-10-06T13:37:21.739605"}
```

### 5. Save a tagged prompt in it

Replace `<collection-id>` with the id from step 4:

```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{"title": "Review a diff", "content": "Review this diff and list any bugs: {{diff}}", "collection_id": "<collection-id>", "tags": ["code-review", "python"]}'
```

The response is `201` with the stored prompt. The server has added its `id` and both timestamps:

```json
{"title":"Review a diff","content":"Review this diff and list any bugs: {{diff}}","description":null,"collection_id":"39bb6d01-c454-4f7a-9da7-bb1afc88f4e6","tags":["code-review","python"],"id":"6f037c0a-2822-40d3-ba78-a78a88fe72c1","created_at":"2026-10-06T13:37:22.617241","updated_at":"2026-10-06T13:37:22.617241"}
```

### 6. Find it again

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
| `DELETE` | `/prompts/{id}` | Delete a prompt and its version history; 204 with no body | `curl -X DELETE $API/prompts/<id>` |
| `GET` | `/prompts/{id}/versions` | List a prompt's content versions, oldest first. Optional `?order=asc\|desc` and `?limit=` | `curl "$API/prompts/<id>/versions?order=desc&limit=2"` |
| `GET` | `/prompts/{id}/versions/{version}` | Fetch one version; 404 if the prompt or the version does not exist | `curl $API/prompts/<id>/versions/1` |
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
On the version endpoints, an `order` other than `asc` or `desc` (an empty `?order=` included), a
`limit` below 1 and a `version` below 1 or not an integer are `422`; a version number above the
latest is `404`.

---

## Development setup

Follow **Prerequisites and installation** first. `requirements.txt` holds the development tools
(`pytest`, `pytest-cov`, `httpx`, `ruff`) as well as the runtime packages, so that one install is all a
contributor needs. Every command below runs from `backend/` with the virtual environment active.

### Run the server with auto-reload

```bash
uvicorn app.api:app --reload
```

`--reload` restarts the server whenever a `.py` file under `backend/` changes. Every restart empties the
in-memory storage, so data created before an edit is gone after it.

### Run the web app in development

From `frontend/`, after `npm install`:

| Command | What it does |
|---|---|
| `npm run dev` | Serves the app at http://localhost:5173 and reloads it on every change |
| `npm run lint` | Checks the code with oxlint |
| `npm run build` | Builds the static app into `frontend/dist/` |
| `npm run preview` | Serves the built `dist/` locally |

`VITE_API_BASE_URL` is read when the app is built. `npm run dev` falls back to
`http://localhost:8000` without it; a build made without it still completes, but the app stops on
load with "VITE_API_BASE_URL is not set". Set it for every build, for example
`VITE_API_BASE_URL=http://localhost:8000 npm run build`.

The API accepts browser requests only from the addresses in `CORS_ORIGINS`, a comma-separated list
read when the API starts. Unset, it is `http://localhost:5173`, the dev server. To serve the app from
anywhere else, start the API with that address, for example
`CORS_ORIGINS=http://localhost:4173 python main.py` for `npm run preview`.

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

### Run the linter

```bash
ruff check .
```

Ruff checks only the rule groups `E4`, `E7`, `E9` and `F` (pycodestyle's import, statement and
syntax-error checks, plus pyflakes), as set in `backend/ruff.toml`.

### Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request, on Python 3.12. From `backend/` it
installs `requirements.txt`, runs `ruff check .`, then runs the suite with
`--cov=app --cov-fail-under=80`, so a lint error, a failing test or coverage under 80% fails the
build. Run the same two commands locally before pushing.

---

## Docker usage

Docker runs the API without a local Python install. `backend/Dockerfile` builds the image;
`docker-compose.yml`, at the repository root, runs it for development with hot reload.

**To deploy the whole app** (API and web frontend), use `docker-compose.deploy.yml` instead, as
described in [`docs/deployment.md`](docs/deployment.md): one command, then open
http://localhost:8080.

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
directly rather than through `python main.py`, which turns reload on.

### Tests

The image holds only `app/` and `requirements.txt`, not `tests/`. Run the tests locally, as
in **Development setup**, or inside the deployed API service, with the deployment's own Python,
libraries and environment, by mounting `tests/` read-only: see
[Run the tests against the deployed configuration](docs/deployment.md#run-the-tests-against-the-deployed-configuration).

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
