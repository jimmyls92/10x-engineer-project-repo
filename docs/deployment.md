# Deploying PromptLab

PromptLab is deployed as two containers started by one command: the **API** (FastAPI, from
`backend/Dockerfile`) and the **web app** (the built React frontend served by nginx, from
`frontend/Dockerfile`). `docker-compose.deploy.yml`, at the repository root, builds and runs both.

Everything needed is committed. Nothing is configured by hand outside these files.

> `docker-compose.yml` (without `.deploy`) is the **development** setup from Module 3: API only,
> with live code mounting and auto-reload. It is not the deployment. See the README's
> **Docker usage** section.

---

## Prerequisites

- **Git**, to clone the repository.
- **Docker** with **Compose v2** (Docker Desktop on Windows and macOS), **with the engine running**.
  Check with `docker compose version`. Without a running engine every `docker` command fails.
- **Ports 8000 and 8080 free** on the machine. Port 8000 is also used by the development setup and
  by a local `uvicorn`; stop those first.

No Python, Node or npm install is needed on the machine: both are used inside the images only.

---

## Deploy

From the repository root:

```bash
git clone https://github.com/jimmyls92/10x-engineer-project-repo.git promptlab
cd promptlab
git checkout Week-4
docker compose -f docker-compose.deploy.yml up --build
```

The first build downloads the base images and installs the dependencies, which takes a few
minutes; later builds reuse the cached layers.

Once both containers are running:

| What | Address |
|---|---|
| **The app** — open this in a browser | http://localhost:8080 |
| The API (used by the app; also callable directly) | http://localhost:8000 |
| Interactive API docs | http://localhost:8000/docs |

Check that both answer:

```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"0.1.0"}
curl -o /dev/null -w "%{http_code}\n" http://localhost:8080/
# 200
```

To run in the background instead, add `-d` (`... up --build -d`) and follow the logs with
`docker compose -f docker-compose.deploy.yml logs -f`.

---

## Environment variables

Both values are set in `docker-compose.deploy.yml`; the defaults there work as they are on one
machine. **They must agree with each other**, because each one names the other side's address.

| Name | Read by | When | Value in `docker-compose.deploy.yml` | Meaning |
|---|---|---|---|---|
| `CORS_ORIGINS` | API (`backend/app/api.py`, parsed by `utils.py:parse_cors_origins`) | When the container **starts** | `http://localhost:8080` | Comma-separated list of the addresses a browser may open the app from. A page on any other address cannot read the API's answers. Unset or empty, only `http://localhost:5173` (the Vite dev server) is allowed. |
| `VITE_API_BASE_URL` | Web app (`frontend/src/api/client.js`) | When the image is **built** (a build argument) | `http://localhost:8000` | The API's address as the **browser** reaches it, without a trailing slash. Vite writes it into the built files, so changing it needs a rebuild. The build **stops** with "Build argument VITE_API_BASE_URL is required" if it is missing. |
| `PYTHONUNBUFFERED` | API | Start | `1` | Sends log lines to `docker compose logs` as they happen. Not a PromptLab setting. |

**If they do not match**, the app loads but every request fails, and it shows the pop-up
**"Can't reach the server. Check your connection and try again."**

### Running on another host or port

Example: the app at `http://192.168.1.20:8080`, reached from other machines on the network.

1. In `docker-compose.deploy.yml`, set `CORS_ORIGINS=http://192.168.1.20:8080` (the address
   people type in the browser).
2. Set the build argument `VITE_API_BASE_URL: http://192.168.1.20:8000` (the API's address as
   those browsers reach it, **not** `localhost`, which would point at each visitor's own machine).
3. Rebuild: `docker compose -f docker-compose.deploy.yml up --build`.

To change a port, edit the left side of the matching `ports:` entry (`"HOST:CONTAINER"`) and the
address in the other setting. Several app addresses can be allowed at once:
`CORS_ORIGINS=http://localhost:8080,http://192.168.1.20:8080`.

---

## Secrets

**PromptLab has no secrets.** There are no API keys, passwords, tokens or database credentials: the
API has no authentication and keeps its data in memory. The two settings above are addresses, not
secrets, so they are committed in `docker-compose.deploy.yml`.

Safeguards in place in case one is ever added:

- `frontend/.env` is git-ignored (`frontend/.gitignore`), and `frontend/.dockerignore` keeps every
  `.env*` file out of the image; the image gets its one setting as a build argument instead.
- Anything a frontend build argument holds ends up in files every visitor downloads, so **a secret
  must never be passed to the frontend**. A future secret belongs to the API, set as a container
  environment variable, not committed.

---

## Stop and reset

```bash
docker compose -f docker-compose.deploy.yml down
```

**Data is not persisted.** Prompts and collections live in the API's memory
(`backend/app/storage.py`), so stopping, restarting or rebuilding the API container empties them.
There is no volume or database to back up or clear.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| The app shows "Can't reach the server" on every action | The API is not running, or `CORS_ORIGINS` and `VITE_API_BASE_URL` do not match the addresses in use | `docker compose -f docker-compose.deploy.yml ps` should list both services as running; then check both settings against the address in the browser's address bar, and rebuild |
| `Bind for 0.0.0.0:8000 failed: port is already allocated` (or 8080) | Another program, often the development compose or a local `uvicorn`, holds the port | Stop it (`docker compose down` for the dev setup), or change the host port as above |
| Build stops with "Build argument VITE_API_BASE_URL is required" | The frontend was built without its API address, e.g. with `docker build` directly | Build through the compose file, or pass `--build-arg VITE_API_BASE_URL=http://localhost:8000` |
| `error during connect ... dockerDesktopLinuxEngine` (Windows) | Docker Desktop is not running | Start Docker Desktop and wait for the engine |
| Reloading `/collections` shows nginx's "404 Not Found" | `frontend/nginx.conf` was not copied into the image | Rebuild; the file sends every path to the app |
