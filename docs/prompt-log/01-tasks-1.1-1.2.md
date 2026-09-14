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

## Entry 14 — Stage 2 walkthrough: every route in `api.py`

**Stage:** 2 — Entry points. **Context level:** file-level, `backend/app/api.py` only (161 lines). No
other source file re-read; `storage.py` and `models.py` are referenced only from what stage 1 already
established.

**Prompt sent:**

> I want to continue with the Entry points task (inside task 1.1), for that I just want to read the
> api.py as context. Can you guide me throught route the application exposes and breifly explain what
> they do and their state?

**What came back:**

A route-by-route walkthrough of `api.py`, nine routes in three blocks — health (`36`), prompts
(`43`–`124`), collections (`129`–`160`) — each with its method, path, status code, response model and
what it actually does line by line. No `SYSTEM_MODEL.md` text written yet; this step was the reading,
the write-up is the next step.

What the file itself shows beyond the route list:

- The app object and its metadata come from `app/__version__` (`18-22`), and CORS is wide open —
  `allow_origins=["*"]` together with `allow_credentials=True` (`25-31`).
- `GET /prompts` (`43`) is the only route taking query parameters: `collection_id` and `search`, both
  optional, applied as filter → search → sort (`48-62`).
- Route handlers are thin: every one of them is storage calls plus `HTTPException`. There is no
  service layer between route and storage, matching the stage 1 finding that `storage` is a concrete
  global imported directly (`api.py:13`).
- Four routes raise `404` explicitly by checking a falsy return from storage (`93`, `123`, `139`,
  `156`); `GET /prompts/{prompt_id}` (`65-74`) is the one that does not.
- `PATCH /prompts/{prompt_id}` does not exist — there is a comment where it would be (`116-117`).
- The source carries the brief's own planted-bug comments at `59`, `67-69`, `101`, `110`, `116`,
  `151-153` and `158`. Their *existence* is a fact about the entry points; deciding anything about
  them belongs to Tasks 1.3–1.7 and was not raised here (Rule 0).

**The context decision, and why file-level this time.**

Stage 1 recorded `api.py` as the sole coupling hub of the repo, 160 lines, importing from `models`,
`storage` and `utils` while nothing imports it back. That is precisely the file where whole-repo
context dilutes attention: the routes are the one place where every module meets, so the reading has
to be line-by-line rather than shape-level. The whole `backend/` tree is 587 lines and would still
have fit in context — the reason for narrowing is coupling, not size.

**Why this is an iteration (C1.3): narrowed context.**

Stage 1 was deliberately whole-repo. This prompt names a single file and says so up front, and the
level was chosen before the reading rather than justified after it.

**Why my next prompt changed:**

The routes are now read and understood. The next prompt is the write-up — turning the walkthrough into
the § Entry points section of `SYSTEM_MODEL.md`, which means choosing a shape for it (table vs prose
per route) and deciding how much per-route behaviour belongs in a section headed "every route the
application exposes".

## Entry 15 — What "test the storage result for falsiness" actually means

**Stage:** 2 — Entry points. **Context level:** unchanged, `backend/app/api.py` already in context. No
new file read.

**Prompt sent:**

> you say that it is the only route that doesnt test the storage result for falsiness before using
> it... what do you exactly mean by that?

**What came back:**

The contrast between guarding *on the object* and guarding *on something reached through the object*.

`if not collection:` (`api.py:138`) asks the question of the variable itself. Every Python object
answers truthy/falsy, `None` included, so the test is safe no matter what storage returned — and only
after the `None` case is thrown out does `:140` use the object.

`if prompt.id:` (`api.py:73`) asks the question of an attribute. The attribute lookup has to be
evaluated *before* `if` has anything to test, so it runs unconditionally on whatever `prompt` is. On a
miss `prompt` is `None`, `None` has no `.id`, and the `AttributeError` escapes the handler as a 500 —
a server fault rather than "not found". Noted as a second defect in the same guard: there is no
`else`, so a falsy `.id` would fall off the end of the function and return `None`, which
`response_model=Prompt` cannot serialise.

Rule 0 held — the mechanism was explained, the fix was not proposed. That is Bug #1 / Task 1.3.

**Why my next prompt changed:**

The explanation was clear, but it invited checking the claim against the other routes — which is what
the next prompt did.

---

## Entry 16 — Catching an over-broad claim: `list_prompts` doesn't have that pattern either

**Stage:** 2 — Entry points. **Context level:** unchanged.

**Prompt sent:**

> ok, but list_prompts also does not have this pattern

**What came back:**

**A concession — the claim was wrong as stated.** I had said `GET /prompts/{prompt_id}` was "the only
route that doesn't test the storage result for falsiness before using it". `list_prompts` takes
`storage.get_all_prompts()` at `api.py:48` and uses it at `:52`, `:56` and `:60` with no test at all,
so the word "only" was false.

The corrected claim is scoped by **return type, not by route**:

- `get_all_prompts()` / `get_all_collections()` return `List[...]`, never `None`. There is nothing to
  guard, and an empty list is a valid answer meaning "nothing matched" — a falsiness check there would
  actively be a bug, firing on the normal empty case.
- `get_prompt()` / `get_collection()` return `Optional[...]`, where `None` *is* the miss and the caller
  must separate the two cases before use.

Defensible version: *among the routes that call an `Optional`-returning getter and then use the
result, `GET /prompts/{prompt_id}` is the only one that reaches inside the result before guarding it.*

Re-checking under the corrected framing turned up something the original framing would have missed:
`PUT /prompts/{prompt_id}` returns `storage.update_prompt(...)` at `:113` unchecked, and that getter is
also `Optional[Prompt]`. It is safe only because existence was established upstream at `:91-93` — safe
by context, not by its own shape.

**C1.5 candidate (Rule 4), organically occurring.** Wrong output: the "only route" claim. Why it was
wrong: stated as a property of routes when it is a property of return types, with "only" asserted
without checking the list endpoints. How it was caught: by the user reading `api.py` and naming the
counter-example — nothing in the tooling flagged it. What was done instead: the claim was re-scoped to
`Optional`-returning getters and re-verified across all nine routes, which also surfaced the `:113`
case. Weaker than an outright behavioural falsehood, so whether it goes into
`docs/ai-verification-note.md` is deferred to Task 1.8; the exact wording is preserved here either way.

**Why this is a genuine iteration (C1.3): it added a constraint the model had skipped.** The prompt did
not reword a question, it asserted a counter-example and forced the claim to be re-derived against the
whole route list rather than the two routes it had been generalised from.

**Why my next prompt changed:**

Correction absorbed, so the outstanding question — the shape of the § Entry points write-up — could
finally be answered.

---

## Entry 17 — Write § Entry points as a table plus a notes subsection

**Stage:** 2 — Entry points, write-up. **Context level:** unchanged — `api.py` only, plus
`docs/SYSTEM_MODEL.md` to match the existing house style.

**Prompt sent:**

> the third one

**What came back:**

Of the three shapes offered — a nine-row table, prose grouped by resource, or a table plus a short
notes subsection — the third was chosen: the table carries coverage (the brief grades *every* route),
the notes carry what the table's cells would flatten.

`docs/SYSTEM_MODEL.md` § 2 written accordingly: a routes table with method, path, status, input,
response model and behaviour, a note on the three routes FastAPI contributes that are not declared in
the source, and four notes on the surface as a whole — the fixed filter→search→sort order, PUT as a
full replace, the inconsistent 404 discipline, and the absent PATCH. The § Context Strategy table
gained its stage 2 row.

One judgement call, stated rather than asked, because it did not change the work: **the planted defects
are described as observable behaviour and pointed forward by task number, never fixed or argued
about.** C1.1 requires that nothing in the model contradict the code, so a route that currently returns
500 on a miss has to be recorded as doing that; Rule 0 requires that no decision about it be taken
here.

**Also corrected in this turn:** entries 15 and 16 had been announced as written when no write had
actually happened. Both were appended for real before this one.

**Why my next prompt changed:**

Stage 2 is closed. Stage 3 is Data flow, and it needs its own context decision — the first stage where
`api.py` alone is demonstrably not enough, since the path from route to storage and back runs through
`utils.py`, `storage.py` and `models.py`.
