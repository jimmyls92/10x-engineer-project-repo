# Prompt log — Tasks 1.1 and 1.2

Task 1.1: explore the codebase and write up `docs/SYSTEM_MODEL.md`.
Task 1.2: record the context strategy used at each exploration stage.

Written live, in my own voice. Entries continue from `00-setup.md` (entries 1–6).

---

## Entry 7 — Restart Task 1.1 after clearing the context

**Stage:** Task 1.1, before any exploration. **Context level:** none — no source file read yet.

**Prompt sent:**

> I want to retake the project

**What came back:**

Context had been cleared deliberately at the end of entry 6, to test whether `CLAUDE.md` alone could
resume the work. It could. Without me restating anything, the CURRENT STATE block was read, the log
state was verified against the filesystem (`01-tasks-1.1-1.2.md` empty, next entry 7, no source file
read), and work resumed at Task 1.1 step 1 — no source file was opened, because choosing the context
level for the first pass is part of Task 1.2 and is mine to decide.

What came back was a step, not an answer: the goal of step 1 (decide and justify the context level for
the first exploration pass) plus three angles — whole-repo orientation from the file tree only,
straight to a file-level deep read of the core module, or a manifest/entrypoint-first pass. Then it
stopped and waited for me to write the prompt.

**Why my next prompt changed:**

Nothing to change yet — this is the restart. The test of `CLAUDE.md` passed: no one-shot deliverable,
no premature file reads, no questions belonging to later tasks.

---

## Entry 8 — Reject one context decision for the whole task; stage it per section instead

**Stage:** Task 1.1, still before any exploration. **Context level:** none — no source file read yet.

**Prompt sent:**

> but we have to decide for every subsection for 1.1? I mean the context needed will change from
> architeture to entry points to storage layer, right? If you agree then lets start with architecture
> as it is the first one, lets explain what is required there and then jump to the next one

**What came back:**

Agreement, and the plan changed because of it. Step 1 had been framed as a single context choice
covering the whole of Task 1.1; I pushed back that the context requirement is not constant across the
write-up — architecture needs breadth with no depth, the storage layer needs depth with almost no
breadth — so one decision cannot honestly justify both.

The exploration was restructured into six stages, one per section required by C1.1, each carrying its
own recorded context level and reason: architecture, routes, data flow, prompt/collection
relationship, storage layer and limitations, external dependencies. Stage 1 is architecture. What
C1.1 requires of that section was spelled out, followed by three context options for it.

**Why this is a genuine iteration (C1.3): restructured the prompt, and the plan behind it.**

Not a rewording. The unit of decision changed — from one context choice per *task* to one per
*section of the deliverable*. The trigger was noticing that the proposed step would have produced a
C1.2 rationale that was true of at most one section and stretched over five others, which is exactly
the mismatch between stated rationale and actual practice that C1.2 fails work for. The rest of Task
1.1 now runs on this structure.

**Why my next prompt changed:**

Next prompt is scoped to architecture alone, and has to carry its own context decision rather than
inherit a global one.

---

## Entry 9 — Stage 1 (Architecture): whole-`backend/` read, answers tied to line numbers

**Stage:** 1 of 6 — Architecture.
**Context level chosen: whole-repo (everything under `backend/`), full file contents.**
**Reason (C1.2):** size. The entire backend is 587 lines of Python across seven source files plus two
test files; loading all of it costs little and removes the guesswork about which file is central.
Structure-only or import-only context would have made the dependency-direction claims inferences from
filenames rather than facts from the source, and C1.1 fails work whose claims contradict the code.
Breadth is the right trade here precisely *because* the repo is small — the same choice would be wrong
at 50k lines, which is what makes it a real decision rather than a default.

**Prompt sent:**

> I think I will need to read all the files to clearly understand the architecture, furthermore it is
> not that much to load in context, so for this case I think is the right choice. With this context I
> need you to answer at "What the project is and how its put together". I need to know the main
> components of this codebase and how they relate with each other. Give me an answer by reading the
> accorded context (basically everything inside backend), and ralate your affirmations with the code
> (mentioning lines or files), so I can double check your answer and accept it or challengue it.

**What came back:**

A component table and a dependency map, every claim carrying a `file:line`. The substance:

- The project is a FastAPI JSON REST backend and nothing else — no frontend, no database, no auth, no
  config layer. Two resources, prompts and collections, held in process memory.
  `requirements.txt:1-6` lists only fastapi, uvicorn, pydantic, pytest, pytest-cov, httpx.
- Seven units: `main.py` (entrypoint, 10 lines, `main.py:7,10`), `app/__init__.py` (`__version__`,
  consumed at `api.py:15,21,38`), `models.py` (schemas + `generate_id:9` / `get_current_time:13`),
  `storage.py` (two dicts behind a `Storage` class, `storage.py:11-14`), `utils.py` (stateless list
  helpers, two of them uncalled — `utils.py:30,43`), `api.py` (app, CORS, all routes), `tests/`.
- `models.py` splits into domain entities (`Prompt:34`, `Collection:54`), request DTOs
  (`PromptCreate:26`, `PromptUpdate:30`, `CollectionCreate:50`) and response envelopes
  (`PromptList:64`, `CollectionList:69`, `HealthResponse:74`). All input validation is declarative and
  lives here as `Field` constraints (`models.py:20-22,46-47`), not in the handlers.
- Dependency direction taken from import statements, not inferred: `api.py:7-15` imports all three
  internal modules; `storage.py:8` and `utils.py:4` import only `app.models`; `models.py:3-6` imports
  nothing internal. `models` is the leaf, no cycles, no back edges.
- The honest shape: it *looks* three-tiered but is not cleanly layered. No service layer — a domain
  rule (does the referenced collection exist?) sits in the HTTP handler at `api.py:80-83`. Storage is
  a concrete global instantiated at import time (`storage.py:69`) and imported *as an instance* by
  `api.py:13`, so there is no interface and no injection seam; `conftest.py:6,18` proves the
  consequence by reaching around the API to reset the singleton directly. One flat route module, no
  `APIRouter`, only comment banners for grouping (`api.py:34,41,127`), and a wide-open CORS policy
  (`api.py:25-31`).
- Weight sits in `api.py` — 160 lines, the largest file and the only one importing more than one
  internal module, so it is the coupling hub. `models.py` 76, `storage.py` 69, `utils.py` 50.

The seeded `BUG #n` comments were noticed but deliberately not discussed, as Tasks 1.3–1.6 own them.

**Why my next prompt changed:**

The "where the weight is" finding is the one that carries forward: `api.py` being the sole coupling
hub is the concrete, size-and-coupling justification for the later stages going file-level on it
rather than repeating this whole-repo load. Stage 1 needed breadth; stage 2 onward should not inherit
it by default.

---

## Entry 10 — The answer described the machinery but never said what the product is for

**Stage:** 1 — Architecture. **Context level:** unchanged (whole `backend/`, already loaded).

**Prompt sent:**

> ok, to respond to the architecture - what the service is and how its put together, I will just answer
> with everything inside "What the project is" and The "components". But before writting anything, you
> did noy say what the project is about. Once we include this we can write our findings. Tell me what
> the project is about, and propose what to write on the architecture section so I can confirm.

**What came back:**

The gap was real and was conceded. Entry 9 had described modules, imports and dependency direction —
the *machinery* — without ever stating the *domain*. A reader could have followed all of it and still
not known what a "prompt" is here or why anyone would run the service.

The purpose, with evidence: PromptLab is a catalogue for reusable AI prompt templates — store,
organise, find, retrieve. `api.py:19-20` names it ("PromptLab API" / "AI Prompt Engineering
Platform"); the `Prompt` entity is shaped for reuse rather than for conversation — `title`, `content`,
`description`, `collection_id` (`models.py:20-23`); organisation is the feature set, with
collection-filter and free-text search wired to query parameters (`utils.py:17-27`, `api.py:44-56`);
the templates are meant to carry `{{variable}}` placeholders (`utils.py:43-50`, and the fixture at
`conftest.py:28`).

Two negative findings that matter more than the positive ones:

- The service **never calls an LLM** and has no dependency that could — `requirements.txt:1-6`. It
  stores prompt text; it does not run it.
- The templating is **aspirational, not implemented**: `extract_variables` and
  `validate_prompt_content` are defined and referenced by nothing — no route, no validator. A write-up
  calling templating a feature would contradict the code and fail C1.1.

Then a proposed three-subsection structure for § Architecture (What PromptLab is / Components / How
they fit together), plus an explicit open question — whether a fourth "Architectural characteristics"
subsection should carry the no-service-layer, storage-global, flat-route-module and open-CORS
observations, or whether those defer to their own later stages. Three options offered, nothing written
to disk pending my confirmation.

**Why my next prompt changed:**

Reviewing the proposed component list against what "architecture" actually means, two of the seven
units did not belong. That is the next correction.

---

## Entry 11 — Cut test and packaging files from the component list

**Stage:** 1 — Architecture. **Context level:** unchanged (whole `backend/`, already loaded).

**Prompt sent:**

> One thing, delete tests/ and app/__init__.py as they are not part of the architecture

**What came back:**

Applied, with one flag raised before doing it: `app/__init__.py` holds `__version__`, which is not
merely packaging metadata — it is surfaced to clients in the `/health` response body
(`api.py:15,21,38`). It leaves § Architecture as instructed and is picked up in the routes stage,
where that dependency is actually load-bearing. `conftest.py` likewise stops being listed as a
component but remains available as *evidence* for the storage-singleton claim in the § Storage Layer
stage.

The component table drops from seven units to five: `main.py`, `models.py`, `storage.py`, `utils.py`,
`api.py`.

**Why this is a genuine iteration (C1.3): narrowed the scope of the deliverable.**

Not a rewording, and not a correction of a factual error — the seven-unit table was accurate. The
constraint added was about *what belongs in an architecture description at all*: runtime components,
not test scaffolding or packaging metadata. Including test files would have padded the section with
units that are not part of the system being described. The AI proposed the wider list and did not
question it; the narrowing was mine.

**Why my next prompt changed:**

Structure of § Architecture is now settled apart from one open choice — whether the "architectural
characteristics" observations live in this section or defer to later stages. That is what the next
prompt has to answer before anything is written.

---

## Entry 12 — Confirm the structure and write § Architecture

**Stage:** 1 — Architecture, write-up. **Context level:** unchanged (whole `backend/`, already
loaded); no new file read for the write-up, since it documents analysis already done.

**Prompt sent:**

> (a), confirmed, write it

**What came back:**

`docs/SYSTEM_MODEL.md` created with § Architecture in four subsections, plus the § Context Strategy
table opened with its stage 1 row:

- **1.1 What PromptLab is** — the domain paragraph, plus the two negative findings: it never calls a
  language model (`requirements.txt:1-6`), and the `{{variable}}` templating is declared but
  unimplemented (`app/utils.py:30-40,43-50` referenced by nothing).
- **1.2 Components** — five runtime units with sizes; test and packaging files excluded per entry 11.
  The three model families, and the note that all validation is declarative `Field` constraints in
  `models.py` (`app/models.py:20-22,46-47`).
- **1.3 How they fit together** — dependency diagram, the four import lines proving direction, the
  leaf/no-cycles conclusion, and `api.py` as the sole coupling hub.
- **1.4 Architectural characteristics** — option (a): no service layer (`app/api.py:80-83`); storage
  as a concrete global with no injection seam (`app/storage.py:69` + `app/api.py:13`, consequence
  visible at `tests/conftest.py:6,18`); one flat route module (`app/api.py:34,41,127`); fully open
  CORS (`app/api.py:25-31`).

The § Context Strategy row was written now rather than at the end of Task 1.1, so the recorded reason
is the one given before the reading happened — which is the whole point of C1.2.

**Why my next prompt changed:**

Stage 1 is closed. Stage 2 is the routes, and it needs its own context decision. The stage 1 finding
that `api.py` is the sole coupling hub is what that decision now has to be argued against — the whole
repo is no longer the obvious level.

---

## Entry 13 — Align every section name with the brief, and load the brief itself

**Stage:** 2 — Entry points, before exploration. **Context level:** the brief PDF only; no source file
re-read.

**Prompt sent:**

> lets go with stage 2, but please use the same naming as the assigment, which is "Entry points". Save
> this in Claude.md so we use the same naming as the assigment (
> @1785592803-Module_1_Project_Brownfield_Challenge.pdf )

**What came back:**

The brief had been sitting untracked in the repo root the whole time and had never actually been read
— `CLAUDE.md` cited it as the source of truth while the section names in use were paraphrases invented
in this session. Reading it needed two attempts: the `Read` tool failed for want of `pdftoppm`, and a
direct text dump crashed on the Windows console encoding (`UnicodeEncodeError` on the `→` character).
PyMuPDF writing to a UTF-8 file worked; the working command is now recorded in `CLAUDE.md` so the next
session does not repeat the flailing.

Checking my correction against the source turned up **more drift than I had flagged**: I asked for one
rename, and two were needed. "Routes" → **Entry points**, and also "Prompt/collection relationship" →
**Models and relationships**. The brief's checklist is: Architecture · Entry points · Data flow ·
Models and relationships · Storage layer · External dependencies · Context strategy.

A third error surfaced that neither of us had raised: **`CLAUDE.md` had Task 1.2 as "context
strategy"**. In the brief, Task 1.2 is *Keep a prompt log*, and the context strategy section is part of
Task 1.1. The confusion came from criterion **C1.2** being the criterion that grades the context
strategy — task numbers and criterion numbers do not line up. Corrected in `CLAUDE.md`, in the work
order, and in the shard table in `docs/prompt-log/README.md`.

**Why this is a genuine iteration (C1.3): added a constraint, and grounded it in a source.**

The constraint is "use the assignment's vocabulary, not your own paraphrase", and it is now a standing
rule in `CLAUDE.md` rather than a one-off correction. What makes it more than cosmetic: the rubric is a
checklist an assessor works through, and a section titled with a synonym forces them to interpret
rather than tick. Applying the constraint properly also required loading the authoritative source
instead of trusting the summary in `CLAUDE.md` — which is what exposed two further errors that a
straight rename would have left in place.

**Why my next prompt changed:**

Naming is settled, so the next prompt can be about Entry points itself — and it has to carry the
stage 2 context decision.

---
