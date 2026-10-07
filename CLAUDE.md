# CLAUDE.md — PromptLab

Working protocol for this repository, for every module of the course. Read this before doing anything
else in a new session.

**This file holds no module-specific requirements.** Tasks, deliverables and criteria for the module in
progress live in **`brief.txt`** (see *The current module's brief*). Only CURRENT STATE names a module.

---

# ⇒ CURRENT STATE

**Keep this block accurate. Update it whenever a task starts or finishes, in the same commit as the
work.** It is how a new session resumes without reading everything.

| | |
|---|---|
| **Current module** | **Module 3** — branch `Week-3`. Brief: `brief.txt`, from `Module_3_Project_Production_Ready.pdf`. Where the brief and this file conflict, **the brief rules**. |
| **Previous module** | **Module 2: submitted on `Week-2`** (`1c9cc88`); its log, entries 1-198, is on that branch. |
| **Current task** | **Task 3.5 — Documented refactor: not started.** **Task 3.4 is done** (Module 3 log entries 412-446): `backend/Dockerfile` on `python:3.12-slim` with `backend/.dockerignore` (`bb74d4f`), root `docker-compose.yml` with the bind mount and `--reload` (`4c5916f`), README section `## Docker usage` (`3b3a10b`). Checked: `docker-compose up --build` builds and starts, `GET /health` and `GET /prompts` return 200, hot reload fires on a host edit (entry 440), the image runs alone without reload (entry 444). Parts of Task 3.4 were proposed by Claude at the user's request (entries 413, 431, 443). **Task 3.3 is done** (entries 380-410): ruff `E4,E7,E9,F`, `.github/workflows/ci.yml` (`b77e6ea`), gate evidence in `docs/ci-gate-evidence.md` (`b56a3f2`); runs 37490611819 ✓, 37491674238 ✗, 37492120010 ✓. **Task 3.2 is done** (entries 96-376): the Tagging System, not Prompt Versioning (entry 98), built in 17 Red-Green cycles as vertical slices US-1 to US-4 (`1785ecc`, `5dd30dc`, `0a35e72`, `e76bb18`), then refactored (`f24766c`, `095b90a`; spec updated in `219ed83`) and documented (`a531e52`, `fd24d63`, `efbd01d`); suite 360 passed, coverage 100%. The cycle plan `docs/tagging-tdd-plan.md` is a working note, **never committed** (entry 232). The refactor commits came after all 17 cycles, not inside each one (entry 353). Task 3.1 is done (entries 4-95, `baacb4b`). **Next: Task 3.5.** |
| **Log file to append to** | `docs/prompt-log.md` |
| **Next entry number** | 447 |

Entry numbers cited below, unless marked otherwise, are from **Module 2's log** (on `Week-2`).

**Open decisions:**

- **Spec review findings left for Module 4's Prompt Versioning** (fresh-context review, Module 2
  log entry 179; tagging findings 7-9 settled in Module 3, entries 98-101). Before implementing
  versions, decide on each: (3) FR-7/E-6, deleting a prompt removes its history, has no AC or test;
  (4) I-1 suggests testing dict keys HTTP never shows; (5) the test list misses `version` `1.5`,
  `1.0` (E-10) and `limit` `abc`, `2.5`, empty; (6) AC-4.8 cites `api.py:70-71` (docstring), the
  code is `:95`, `:99`; (10) it does not say `order` is a `Literal` or an `Enum`. Finding 7 was
  accepted, not fixed: `PromptVersionList` goes under `Response Models` while `TagList` has its own
  `Tag Models` banner.

**Known traps:**

- **`README.md` and `docs/API_REFERENCE.md` list every endpoint.** Any endpoint added later (Module
  3's feature) must also go into the README's Features list and API endpoint summary, and get its own
  section in the API reference (curl example, sample response, errors), or C2.2 fails at Module 3.
- **Two deprecation warnings in `models.py`** (seen in entry 22): the class-based `Config` blocks
  (`models.py:220`, `:269`) and `datetime.utcnow()` (`models.py:37`). No Module 2 task covers them;
  docstrings describe them as they are.
- **`Storage.update_prompt` does not check that `prompt.id` equals `prompt_id`** (entry 30,
  `storage.py:66`). Unreachable today, since PUT and PATCH copy `existing.id` (`api.py:201`, `:254`);
  any new code that replaces a prompt must do the same.
- **An empty-string `collection_id` is handled inconsistently** (entry 37). POST and PUT store `""`
  unchecked (`api.py:156`, `:195` test truthiness); PATCH looks it up and returns 400 (`api.py:248`,
  `is not None`). The docstrings describe it; any spec or doc touching `collection_id` must too.
  A consequence (entry 50): `GET /prompts?collection_id=` ignores the empty value (`api.py:95`), so
  prompts stored with `""` cannot be listed by collection. Stated in the API reference's Known issues.
- **`PATCH` rejects a null `title` or `content` with 422** (fixed in `158eb0b`, entries 53-71;
  `reject_null` in `models.py`). It runs while the body is validated, **before** the 404 and 400
  lookups, so `PATCH /prompts/nope` with `{"title": null}` is 422, not 404. Any doc that lists PATCH
  errors or the order of checks must say so (README, `API_REFERENCE.md`, the `patch_prompt` and
  `PromptPatch` docstrings do). `/openapi.json` still shows both fields as nullable.
- **Never push to `main`.** The brief's verification says `git push origin main`, but each module
  is delivered on its own branch (`Week-3`), and `main` holds Module 1, not yet assessed. The CI workflow
  (`.github/workflows/ci.yml`) triggers on push to any branch (`on: [push, pull_request]`), so
  **every push of `Week-3` runs it, and a red run is public**. Run the suite and lint before pushing.
- **Run tests and lint in a pinned environment.** The global Python is 3.13 with newer libraries
  (FastAPI 0.141.1, Pydantic 2.13.5); `requirements.txt` pins FastAPI 0.109.0 and Pydantic 2.5.3,
  which need Python 3.10-3.12. CI installs the pins (on Python 3.12), so check coverage and lint in
  a Python 3.12 venv built from `requirements.txt` (`backend/.venv`; `python3.12` and `uv` are
  installed), not the global interpreter. Ruff is pinned there too (`0.16.10`).
- **Ruff enforces only `E4`, `E7`, `E9`, `F`** (`backend/ruff.toml`, Module 3 log entries 383-384).
  Ruff 0.16's wider defaults gave 81 findings, most contradicting conventions in this file (`typing`
  imports, naive UTC timestamps, deletion routes returning `None`). Do not widen the set without a
  task that asks for it. GitHub warned that `ubuntu-latest` moves to Ubuntu 26 from 2026-10-19; the
  workflow does not pin an Ubuntu version.
- **The clock is coarse on Python 3.12 here** (Module 3 log, entries 45-46). `datetime.utcnow()`
  steps about every 0.3-1 ms in the pinned venv on Windows, but per microsecond on the global 3.13.
  So a new `Prompt`'s `created_at` and `updated_at` are equal 9,985 times in 10,000 on 3.12, and two
  back-to-back POSTs share a `created_at` about 5 times in 300. Tests comparing timestamps from
  separate requests can therefore fail rarely on Windows 3.12. Not measured on Linux. Handled by
  the `ticking_clock` fixture (entries 47-48) for every strict timestamp comparison.
- **`python main.py` does not start a server** with the pinned uvicorn 0.27.0 (Module 3 log, entry
  421): `main.py:10` passes the app object with `reload=True`, so uvicorn logs "You must pass the
  application as an import string" and exits with code 1. `backend/Dockerfile` and `docker-compose.yml`
  call `uvicorn app.api:app` directly; never switch them to `main.py`. The README says the same
  (`README.md:111-114`).
- **Docker** (Task 3.4). Compose mounts only `backend/app/`, so a change to `requirements.txt` or the
  `Dockerfile` needs `docker-compose up --build`. Docker Desktop does not start on its own; without the
  engine every `docker` command fails on `dockerDesktopLinuxEngine`. Compose and a local uvicorn both
  use port 8000: stop one before starting the other.

---

## Course context

AIE 500 / PromptLab — five modules, one project, built cumulatively. Course-wide rules, from
`1785592752-AIE500_Course_and_Project_Guide.pdf` (repo root):

- **The work is cumulative.** Specs from Module 2 are implemented in Modules 3 and 4; the code from
  Module 4 is defended in Module 5. Documentation must keep matching the code as it changes.
- **Each criterion is Met or Not Yet on its own.** Nothing is averaged; MUST PASS criteria block the
  whole submission.
- **Process evidence is assessed**: the prompt log, the commit history, and a recorded defense. Logs
  and histories "cannot be convincingly reconstructed afterwards", and trying to is an integrity matter.
- **A submission is returned** if provided tests fail, the app doesn't run, a required deliverable is
  missing, or secrets are committed.

## The current module's brief

`brief.txt` at the repo root is the text of the current module's project PDF. It holds that module's
**tasks**, **what you submit**, **verification steps** and **criteria table** (with the common
mistakes that come back Not Yet). It is the source of truth for scope — read it at the start of each
module, and re-read the relevant task before starting it.

PDFs here have no text layer the `Read` tool can take directly. At the start of a new module,
regenerate `brief.txt` from that module's PDF with PyMuPDF, writing to a file (the Windows console
cannot print some of the characters used):

```
python -c "import pymupdf,pathlib; d=pymupdf.open('<module PDF>'); pathlib.Path('brief.txt').write_text('\n'.join(p.get_text() for p in d),encoding='utf-8')"
```

## Agent instructions live in CLAUDE.md

**This project is carried out with Claude Code, and `CLAUDE.md` is its agent-instructions file** —
whatever a brief names instead (`.github/copilot-instructions.md`, `.continuerules`, or any other
tool's file). Adapt the assignment to this; do not create the file the brief names.

- A task that asks for "the agent file" is answered in `CLAUDE.md`, under the brief's own section
  names.
- Wherever a brief's evidence, checklist or criterion names the other file, `CLAUDE.md` stands in
  for it. Say so in the deliverable (e.g. the README or an effect note), so the assessor is not
  left to infer the substitution.
- Everything else the brief requires of that file — its content, specificity, and proof that it
  changed generated output — still applies in full.

## Section naming

**Use the brief's own words for every section and task heading.** Matching names is how an assessor
confirms a checklist item is covered without having to interpret a synonym.

## Rules

### 0. Answer the current task, and only the current task

Work the task named in CURRENT STATE. Scope is set by what that task asks for and what the brief's
criteria grade it on — nothing else.

Do **not** raise, decide, or ask about anything belonging to a later task, even when the answer seems
obvious now. If something relevant to a later task surfaces, add it to **Open decisions** or
**Known traps** in CURRENT STATE and carry on.

Finishing a task means: deliverable written, its log entry appended, CURRENT STATE updated, committed.
Then stop and report — do not roll straight into the next task.

### 0b. Work step by step, and act only with permission

**This is a learning exercise, and the user wants to understand every step.** They are learning to
work with AI, not commissioning output. A correct deliverable that appeared in one turn is a failed
turn, however good it is.

**The method trains deductive reasoning: guide the user to the answer, never hand it over.** (Agreed
in Module 3, log entries 103-104 and 117; it replaced a method of options plus a recommendation.)

Break every task into small steps — typically 3 to 6. For each step:

1. **Open with one question, in bold, with context — as a teacher would.** Say where we are and what
   the plan says comes next, then ask what to do. A hint at the kind of answer wanted is fine
   ("shall we use the specs as they are, or what do you think?"); a list of options is not.
   - **One question per step.** If a second question comes up, name it as the next step; do not
     attach it.
   - **Size the question to the step.** If answering needs more than one decision, split the
     question into its smallest piece (one item, one case, one choice) and ask about that piece
     first.
     - **Say what shape the answer should take**: what to name, and what reason to give.
     - **When the format of the answer is new, show a worked example** or a partly filled template.
     - **Widen the question only after the user has answered a narrow one well.** If an answer shows
       the question was too open, narrow it at once instead of waiting for three exchanges.
   - **Ask only about what the user is learning: coding and spec-driven development.** A convention
     already written in this file (naming, layers, banners, file names, response models) is applied
     by Claude and stated as settled, never turned into a question (Module 3 log, entry 215).
2. **Stop. Wait for their prompt.** They write it — you do not draft it for them.
3. **Do not ask the user to justify an answer.** When a choice looks weak or wrong, challenge it:
   name the downsides (point 5). (Changed at the user's request, Module 3 log entry 457.)
4. **If the answer is ambiguous, not specific enough or wrong, narrow it** with comments or questions
   that lead towards a good answer. Never state the answer.
5. **There is no right or wrong answer, with two exceptions, which you correct directly:** a choice
   that goes against a grading criterion in `brief.txt` and could fail the assignment, and any
   breach of a rule in this file. Otherwise, **name every downside you see** in their choice and ask
   for, or propose, an alternative.
6. **Only after three exchanges without an explicit next step or plan**, lay out the options with the
   pros and cons of each and **no recommendation**. Give your recommendation only once the user has
   chosen, then ask which of the two to follow.
7. Act on what they actually sent, then log the entry, then open the next step.

Unchanged by the method: Claude still proposes every commit message for approval (Rule 5) and writes
the prompt log (Rule 1).

Hard limits:

- **Nothing is created, edited, run or committed without the user's explicit permission for that
  specific step.** Permission for one step does not carry over to the next.
- **One step per reply.** Never run two steps because the next one seems obvious.
- **Never pre-empt a step's finding.** If you already know the answer, do not state it. Set up the
  step that lets the user find it.
- **Do not write a deliverable until its content has been worked through step by step.** The document
  is a write-up of work already done together, never the first place the analysis appears.
- If the user says to go faster or to just do it, do that — but say once what is being skipped.

### 1. Prompt log is written live, never reconstructed

Every module keeps a prompt log, in **one file per module: `docs/prompt-log.md`**. It is not split by
task; entries are numbered in order from 1 for the whole module.

After **every** user prompt in this repo, append an entry to that file before or alongside doing the
work. An entry contains:

- **Prompt** — the user's message, verbatim.
- **What came back** — summary of the response; paste the relevant part.
- **Why the next prompt changed** — one line. If the output was good enough, say so.

Write entries in the user's first-person voice — they are the one prompting. Never invent a prompt
that was not actually sent. Never backfill a gap by guessing; if an entry is missing, mark it as
missing.

Flag explicitly in the entry whenever an iteration **narrowed context, added a constraint, or
restructured** the prompt.

### 2. Verify every claim against the source

Documentation and specs must describe what the code does, not what the AI said it does. Before
writing any claim about behaviour, confirm it in the source.

### 3. Never hide a bug

Catching an exception and discarding it counts as a bug still present. Fixes must address the cause.

### 4. Keep replies short and scannable

The user asked for this explicitly.

- **Each explanation is 200 words or fewer.** If a topic needs more, stop there, ask whether the user
  has understood so far, and ask whether they want to continue with the next part — the way a
  teacher would.
- **Bullets over paragraphs.** Bold the thing that matters in each bullet.
- **Use tables instead of bullets** when a comparison or the message itself can be enhanced.
- **Cut anything that is not a finding, a decision, or a question.**
- **Cite `file.py:line` instead of quoting code** unless the exact text is the point.
- This constrains **chat replies only**. Deliverables stay as thorough as the criteria need.

Rule 0b still holds: short does not mean skipping the step, the angles, or the stop.

### 5. Commit messages are graded, and the user approves every one before it is written

Meaningful, specific messages; **one logical change per commit**. Commit in small steps and **never
squash** — the history is process evidence.

**Never run `git commit` without showing the message first and getting an explicit yes.** Propose the
full message — subject and body as they will actually be committed — in the chat reply, say which files
are staged, and stop. The user may accept it, edit it, or ask for a different split into commits.

If the user has already said "commit it" in the prompt being acted on, that is approval for the commit
but **not** for the message — still show the message and wait, unless they say to stop asking.

**Length, set by the user and not negotiable:**

- **Subject**: imperative, **≤ 50 characters**, naming the change.
- **Body**: **at most two sentences, about twenty words each.** Why, not what — the diff already shows
  what changed. Cite `file.py:line` inside a sentence rather than adding a line for it.
- Nothing else. No bullet lists, no "Also …" paragraph, no test-count tables.

**Do not bundle.** If the message needs an "Also …", it is two commits. Propose the split and let the
user decide.

**What the body is for.** The reasoning that leaves no trace in the diff — a claim corrected, a section
deliberately not written, an option rejected. If only one sentence can be spent, spend it there.

## PromptLab coding standards

**These sections are the project's agent instructions.** Module 2 asks for them in
`.github/copilot-instructions.md` or `.continuerules`; here `CLAUDE.md` stands in for both. Every
rule describes the code as it is. Where the code breaks a rule, the place is listed under **Known
exceptions**. Do not copy those, and do not "fix" them unless a task asks for it.

### Coding standards specific to this project

- **Four modules, one layer each.** `models.py` declares and validates data, `storage.py` keeps it,
  `api.py` owns HTTP, `utils.py` holds pure helpers. Nothing below `api.py` imports FastAPI or knows
  about status codes.
- **Type hints on every parameter.** Storage methods and helpers in `utils.py` also annotate their
  return type. Endpoints do not, and declare `response_model` in the route decorator instead. Types
  come from `typing` (`Optional`, `List`, `Dict`), not `X | None` or `list[X]`.
- **Timestamps come only from `get_current_time()`**, never from `datetime` directly, so every
  timestamp is naive UTC.
- **Google-style docstrings on every module, class and function**, with `Args`, `Returns` and `Raises`
  where they apply. A docstring states what the code does, quirks included, and never just restates
  the name. Endpoints do not list 422 under `Raises`, because FastAPI rejects the body before the
  function runs.
- **Comments explain why, not what.** A decision that would look wrong without context gets a
  comment above the code.

### Preferred patterns and conventions

- **Model family per resource**: `XBase` holds the client fields and their `Field` constraints;
  `XCreate`, `XUpdate` (PUT) and `XPatch` are request bodies; `X` is the stored record and adds the
  server fields. A patch model repeats the base constraints.
- **The server assigns `id` and timestamps** through `default_factory`. A request body never declares
  them, and undeclared keys are dropped.
- **List responses are `{<resources>, total}`** (`PromptList`, `CollectionList`), with `total`
  counted after filtering. A list of prompts is sorted newest first with `sort_prompts_by_date`.
- **Replacing a stored prompt builds a new `Prompt`** that copies `existing.id` and
  `existing.created_at` and refreshes `updated_at`. A change that is not a client edit uses
  `model_copy(update=...)` and keeps `updated_at`.
- **PATCH reads which fields were sent with `model_dump(exclude_unset=True)`**, never by testing for
  `None`: an explicit `null` and an absent key mean different things.
- **Check an optional id with `is not None`**, not with truthiness.
- **Helpers in `utils.py` never modify their input**; they return a new list.
- **Layout**: each module groups its code under banners of the form
  `# ============== Prompt Endpoints ==============`. A new endpoint goes under its resource's banner.
  Creation routes declare `status_code=201`; deletion routes declare `status_code=204` and return
  `None`.

**Known exceptions:** creating and replacing a prompt, and filtering the prompt list, test
`collection_id` by truthiness, so an empty string is stored unchecked (see Known traps). The stored
models use the deprecated class-based `Config`.

### File naming conventions

- **Source modules** are lowercase single nouns in `backend/app/`: `models.py`, `storage.py`,
  `api.py`, `utils.py`. The entry point is `backend/main.py`. A new layer gets a new module; a new
  resource does not.
- **Tests** live in `backend/tests/test_<module>.py` (`test_api.py`), with shared fixtures in
  `backend/tests/conftest.py`.
- **Names in code**: functions and variables `snake_case`, classes `PascalCase`. Route handlers are
  `<verb>_<resource>`: `list_prompts`, `get_prompt`, `create_prompt`, `update_prompt` (PUT),
  `patch_prompt`, `delete_prompt`. Storage methods follow the same verbs (`get_all_prompts`,
  `get_prompts_by_collection`). Path parameters are `<resource>_id` (`prompt_id`, `collection_id`).
- **Docs**: references are `UPPER_SNAKE.md` in `docs/` (`API_REFERENCE.md`); notes and logs are
  `kebab-case.md` (`docs/prompt-log.md`); feature specs are `specs/<feature>.md` in kebab-case.

### Error handling approach

- **Storage never raises for a missing record.** It returns `None` or `False`, and the endpoint
  decides the status.
- **Endpoints report errors only by raising `HTTPException`**, which FastAPI sends as
  `{"detail": "<message>"}`. The message is `"<Resource> not found"`.
- **Status codes follow what went wrong:**

  | Status | When | Raised by |
  |---|---|---|
  | **422** | The body or a query parameter breaks a model constraint | Pydantic, before the endpoint runs |
  | **404** | The id **in the path** names nothing | The endpoint |
  | **400** | An id **in the body** names nothing, e.g. a `collection_id` | The endpoint |

- **A filter that matches nothing is not an error.** An unknown id in a **query parameter** gives an
  empty list with status 200, unlike an unknown id in the path.
- **Checks run in this order**: body validation (422), then the path lookup (404), then references in
  the body (400).
- **Validation belongs in the model**: a `Field` constraint, or a `field_validator` raising
  `ValueError`, which FastAPI reports as 422. Endpoints do not re-check what the model already
  enforces.
- **Never catch an exception to hide it** (Rule 3), and never let a known bad input reach a 500.

### Testing requirements

- **The suite must pass before any commit**: `cd backend` then `pytest tests/ -v`.
- **Every endpoint, and every bug fix, gets tests for each status it can return**: the success case
  and every error case.
- **Endpoint tests go through the HTTP API** with the `client` fixture, in `test_api.py`; they never
  call storage to set up or check state. **Unit tests call their module directly**:
  `test_storage.py` the `Storage` class, `test_utils.py` the helpers, `test_models.py` the models.
  Storage is cleared before and after every test by the autouse fixture. Payloads come from the
  `sample_prompt_data` and `sample_collection_data` fixtures.
- **Tests are grouped in classes**: by resource in `test_api.py` (`TestHealth`, `TestPrompts`,
  `TestCollections`), and by class or function under test in the unit-test files. They are named
  `test_<verb>_<resource>_<behaviour>` (`test_patch_prompt_not_found`).
- **Assert one exact status code**, never a set of acceptable ones.
- **After a change, re-read the record with GET** to prove it was stored, not just echoed.
- **Compare timestamps as values**, parsed with `datetime.fromisoformat`, never with `time.sleep`.
  The clock's step depends on the platform (see Known traps): two values read in one call are often
  equal, and two from separate requests occasionally are. **A test asserting one timestamp is later
  than another takes the `ticking_clock` fixture** (`conftest.py`), which advances 1 µs per call.
- **Use `pytest.mark.parametrize`** for the same check over several fields.
- **Each new test has a docstring** saying what it verifies, with `Args` for its fixtures.

**Known exceptions**, all in tests provided with the course: one accepts either 404 or 500, two use
`time.sleep`, and most have no docstring or one without `Args`. Leave them as they are unless a task
asks to change them.

## Verification command

The provided tests must pass in every module:

```
cd backend
pytest tests/ -v
```

With coverage, as Module 3's brief measures it (the threshold is 80%):

```
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

CI (`.github/workflows/ci.yml`) runs, in `backend/`, lint first and then the tests with the
threshold enforced:

```
cd backend
ruff check .
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

Each module's brief adds its own verification steps.
