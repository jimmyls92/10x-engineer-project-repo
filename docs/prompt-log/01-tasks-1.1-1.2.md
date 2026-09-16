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

## Entry 18 — Constrain the reply format: bullets, bold, brevity

**Stage:** 3 — Data flow, before exploration. **Context level:** none; no source file read.

**Prompt sent:**

> I need you to be less verbose and focus more into comments and answers that give value. Please use
> bullets, bold letters and shorten messages in order to make our conversations easier to follow and
> understand. Write this on CLAUDE.md

**What came back:**

Rule 5b added to `CLAUDE.md`: bullets over paragraphs, bold the operative words, cut anything that is
not a finding, a decision or a question, cite `file.py:line` rather than quoting code.

Two boundaries drawn while writing it, because the instruction as given could have been over-applied:

- **It binds chat replies only.** The deliverables are graded on completeness — shortening
  `SYSTEM_MODEL.md` or the log entries to match a chat preference would trade marks for readability.
- **It does not override Rule 0b.** A step still has to name its purpose, offer the angles and stop;
  brevity is about how that is written, not about collapsing steps.

**Why this is a genuine iteration (C1.3): added a standing constraint, not a reworded question.**

The prompt does not ask anything about the codebase. It changes how every future answer is produced
and persists the change in `CLAUDE.md` so it survives a session restart — the same move as entry 13's
naming constraint, applied to form rather than vocabulary.

**Why my next prompt changed:**

Format is settled. The next prompt is the stage 3 context decision, which is still outstanding.

## Entry 19 — Stage 3 context decision, and the walkthrough of the request path

**Stage:** 3 — Data flow. **Context level:** file-level, three files — `app/api.py` (already in
context), `app/storage.py` (69 lines), `app/utils.py` (50 lines). `app/models.py` deliberately excluded.

**Prompt sent:**

> The way I see we just need api.py and storage.py... utils should not be needed as long as utils just
> transfrom the data... what do you think?

**What came back:**

Partial disagreement, with reasons, and a recommendation to add `utils.py` back:

- `utils.py` is **on** the path, not beside it — for `GET /prompts` the return leg *is* filter →
  search → sort (`api.py:48-62`), so excluding it would describe the only non-trivial route's return
  journey as "three helpers happen".
- "as long as utils just transforms the data" was the assumption under test, not an established fact.
  Only the signatures were known, from stage 1.
- Stage 2 had left an explicit IOU: the sorting claim in §2.3.5 stops at the call site and the Context
  Strategy row promises stage 3 closes it. Dropping `utils.py` would leave no stage owning it.
- `models.py` was argued **out** on the same principle: it is the shape of what travels, which is
  stage 4's section, and reading it now would pull stage 4's content into stage 3.

**Follow-up prompt sent:**

> ok lets go with the three files then

**What the reading found** (recorded here; the write-up is the next step):

- **Storage hands out live references, never copies.** `get_prompt` returns the stored object
  (`storage.py:23`); `get_all_prompts` returns `list(self._prompts.values())` (`:26`) — a new list
  containing the same objects. Writes are symmetrical: `create_prompt` stores the very object the
  handler constructed (`:19`). Nothing is cloned in either direction.
- **The utils helpers are non-mutating** — two list comprehensions and a `sorted()` call, each
  returning a new list (`utils.py:18,23,14`). So the premise behind the original two-file proposal was
  correct about *mutation*; it was the *behaviour* inside one of those transforms that made the file
  worth reading.
- **The stage 2 IOU is closed, and the bug is not where the route suggested.** `sort_prompts_by_date`
  accepts `descending: bool = True` and never reads it — `sorted(prompts, key=lambda p: p.created_at)`
  is ascending, oldest first (`utils.py:7-14`). `api.py:60` passes `descending=True` in good faith. The
  call site is correct; the helper ignores its own parameter.
- **The same filter is implemented twice.** `storage.get_prompts_by_collection` (`storage.py:58`) and
  `utils.filter_prompts_by_collection` (`utils.py:17`) are the same predicate. `api.py` uses the utils
  one; the storage one is called by nothing in the application.
- **`search_prompts` guards `description` for `None` but not `title`** (`utils.py:25-26`), which is
  consistent with the schema — `title` is required, `description` optional.
- **`storage.clear()`** (`storage.py:63`) exists only for the tests, which is the seam noted in
  stage 1 at `tests/conftest.py`.

**Why this is a genuine iteration (C1.3): the user narrowed the context, and the narrowing was pushed
back on with evidence rather than accepted.** The two-file proposal came with an explicit premise
("as long as utils just transforms the data"); the reply tested the premise instead of the file list,
and the agreed scope of three files is narrower than stage 1's whole-repo and wider than the proposal.

**Why my next prompt changed:**

The path is traced. What remains is choosing how to present it — by route, by leg, or as one worked
example — which is a shape decision, not a reading one.

## Entry 20 — Why "by leg" risks abstraction, and the shape that was settled

**Stage:** 3 — Data flow, write-up shape. **Context level:** unchanged — the same three files.

**Prompt sent:**

> On the leg one, why you think risk will be too abstrack and why is that difference with the other
> options?

**What came back:**

The risk named concretely rather than as a general warning: a leg description — JSON → Pydantic
validation → handler → storage → `response_model` → JSON — is **true of every FastAPI application**,
so it can be entirely accurate and still say nothing specific about PromptLab. That is expensive under
C1.1, which grades claims that can be checked against the source: leg prose tends to produce sentences
with no line to cite.

Demonstrated with the stage 3 findings, which resist the leg shape because they are conditional:

- "storage hands out live references" (`storage.py:23,26`) only matters **because** `PUT` rebuilds
  rather than mutates (`api.py:103-111`) — one claim spanning two legs;
- the sort defect (`utils.py:14`) belongs to the outbound leg of **one route out of ten**.

Written purely by leg, both degrade into "…except for" footnotes.

How the alternatives differ: **by route class**, the unit of organisation is the thing that actually
varies, so claims attach to lines structurally; **worked trace plus deltas** is concrete by
construction but pays in length and has to argue its chosen route is representative.

**Follow-up prompt sent:**

> ok, lets go with that, but show me the data flow one by one so I can review and accept

**Settled shape:** legs as the spine, with a per-route deltas table beneath them, so the narrative stays
clean and the exceptions have somewhere honest to live. Presented one leg at a time for review before
anything is written to `SYSTEM_MODEL.md`.

**Why this is a genuine iteration (C1.3): the user interrogated the trade-off instead of accepting the
recommendation, and then restructured the delivery.** The prompt did not pick an option — it asked the
reasoning to be justified, and the result was a hybrid neither of us had proposed, plus a review
protocol (leg by leg, accepted one at a time) that did not exist in any of the three original angles.

**Why my next prompt changed:**

Nothing further to decide about shape. The next prompts are acceptances or corrections of one leg at
a time.

## Entry 21 — Shape corrected again: § Data flow becomes a per-route matrix

**Stage:** 3 — Data flow, write-up shape. **Context level:** unchanged — the same three files.

**Prompts sent:**

> I want to correct and go for the delta table, as I see it more fit for this purpose

then, after the ambiguity was put back as two options:

> Lets go for A and if then we see we need to change it we go for it. Regarding "correct" it was aimed
> at the shape

**What came back:**

The instruction had two readings that produced different documents, so it was not guessed at: **A** —
the section *is* a matrix, one row per route, columns for bind/validate → handler guards → storage call
→ transform → response, no leg prose at all; **B** — matrix first, with legs demoted to a short
exceptions section. A was chosen, with the cost stated up front: the cross-cutting facts (storage
handing out live references, `PUT` rebuilding rather than mutating) have no natural cell and will need
somewhere to go.

Leg 1 had already been drafted and reviewed in chat when the shape changed. Nothing was lost — by the
protocol agreed in entry 20, no leg is written to `SYSTEM_MODEL.md` until it is accepted, so the
correction cost a draft in conversation and nothing in the deliverable.

**Why this is a genuine iteration (C1.3): the user restructured the output after seeing a sample of
it.** Entry 20 settled "legs as the spine, table beneath". Reviewing the first leg is what showed that
the prose spine was not earning its place for this section, and the structure was inverted then
discarded. This is the restructuring C1.3 asks for, and it was driven by the review protocol the user
himself introduced — the sample existed to be judged, and it was judged.

**Why my next prompt changed:**

Shape is settled for real. The next prompts review the matrix rows themselves.

## Entry 22 — "How do you know?" — an inferred claim challenged and then executed

**Stage:** 3 — Data flow, matrix review. **Context level:** unchanged, plus one execution against the
running app.

**Prompt sent:**

> Number 3 (get_prompt) says it returns a 200 on hit, but 500 on miss, how you knwo this?

**What came back:**

**A concession that the claim was inference, not observation.** The chain was split into what had been
read and what had not:

- read from source — `get_prompt` returns `self._prompts.get(id)`, so `None` on a miss
  (`storage.py:23`); `:73` evaluates `prompt.id` before the `if` can test anything;
- **asserted from general FastAPI knowledge, not from this repository** — that an unhandled exception
  in a handler becomes a 500.

The third step was then executed rather than argued, through `fastapi.testclient.TestClient` against
`app.api:app` with storage cleared:

```
status: 500
body: Internal Server Error
raised: AttributeError - 'NoneType' object has no attribute 'id'
```

The cell survived unchanged, but **the kind of evidence behind it changed**, and that is what is
recorded in §3.3 of `SYSTEM_MODEL.md` — an observed result with the command behind it, not a claim
assembled from three line citations.

Two further things the question forced out:

- The same weakness had been **flagged on leg 1 and then allowed to ride into the matrix**: the "422
  from the framework" cells were unverified too. They were run in the next turn — empty `title` 422,
  empty body 422, over-long collection `name` 422, unknown `collection_id` **400** from the handler's
  own check, valid body 201.
- `TestClient`'s default `raise_server_exceptions=True` **re-raises** the `AttributeError` instead of
  returning a response. Recorded now because it dictates how the miss case can be asserted when
  Task 1.3 gets a test.

**C1.5-adjacent, and worth noting alongside entry 16.** No false statement was produced — the claim was
correct — but it was presented with the same confidence as the cited claims around it while resting on
an unverified step. The failure mode is *unmarked inference*, and it was caught by the user asking for
provenance rather than for a fact.

**Why this is a genuine iteration (C1.3): it added a standing evidential constraint.** The prompt did
not challenge the conclusion, it challenged the warrant. The result is a rule the section now follows —
claims that rest on framework behaviour are executed and recorded in §3.3 — and it retroactively
repaired three other cells that would have shipped unverified.

**Why my next prompt changed:**

Nothing left to challenge in the matrix; the remaining step was to write it.

---

## Entry 23 — Write § Data flow

**Stage:** 3 — Data flow, write-up. **Context level:** unchanged.

**Prompt sent:**

> ok, lets write this

**What came back:**

The 422 cells were verified first, unprompted, since they were the one loose end left by entry 22 and
leaving them would have put an unmarked inference into the deliverable immediately after agreeing not
to.

`docs/SYSTEM_MODEL.md` § 3 written: an opening paragraph saying why the section is a matrix rather than
a stage narrative (the stages are FastAPI's and identical in any FastAPI app; only the cells are
PromptLab's), §3.1 the prompt and health routes, §3.2 the collection routes, §3.3 the claims verified
by execution, and §3.4 the five facts that span routes and therefore have no cell — no copying in
either direction, the non-mutating but incorrect sort, validation being entirely pre-handler, the
collection filter existing twice with the flow using the outer one, and the two empty Transform columns
being an omission in `utils.py` rather than a decision in the handlers.

The § Context Strategy stage 3 row records the three-file decision including the rejected two-file
proposal and the reason `models.py` was kept out.

**Why my next prompt changed:**

Stage 3 is closed. Stage 4 is Models and relationships, and `models.py` — held out of the last two
stages precisely so it would land here — is its obvious context.

## Entry 24 — Stage 4 context: back to whole-repo, and a reflection on what narrowing was for

**Stage:** 4 — Models and relationships. **Context level:** whole-repo — every file under `backend/`,
including `tests/`.

**Prompt sent:**

> Now I realize that since the size of the code its that small I could have given full context to every
> section exploration. I want to underline this for the Context strategy section. Following this idea,
> I would like to use the whole context of the repository (the backend) for knowing more about how
> propmts and collections relate, due the high coupling of the code.

**What came back:**

Agreement, plus one refinement, because the table would otherwise read as contradicting itself —
coupling was the stated reason for **narrowing** at stage 2 and is now the stated reason for
**widening** at stage 4. The distinction that makes both honest:

- **stage 2** — the coupling was *concentrated*: one hub file held every route, so attention belonged
  there;
- **stage 4** — the relationship is *distributed*: `collection_id` is declared in `models.py`, enforced
  in `api.py:80-83` and `:96-99`, and not enforced at all in `storage.py`. Any single file would show
  the declaration and miss whether anything upholds it.

The reflection itself was sharpened before being recorded: **breadth was always affordable, so the
narrowing bought attention rather than feasibility.** That is a stronger claim under C1.2 than "the
repository is small" — it says the level was chosen deliberately at each stage instead of being forced
by a limit, which is what the criterion actually asks for.

**What the reading found** (the write-up is the next step):

- **The relationship is declared on one side only.** `Prompt.collection_id: Optional[str] = None`
  (`models.py:23`); `Collection` has no field pointing back (`models.py:54-59`). A collection cannot
  name its own members.
- **`collection_id` is the only field in the entire schema with no `Field(...)` constraint** — a bare
  `Optional[str]`. It is not a foreign key, and the model layer knows nothing about collections.
- **Enforcement exists in exactly two places, both HTTP handlers** (`api.py:80-83`, `:96-99`), and in
  both only when the value is truthy — `None` means unfiled and correctly skips the check.
- **Nothing maintains it afterwards.** `storage.create_prompt` and `update_prompt` file whatever they
  are handed (`storage.py:19,31`), and `delete_collection` touches the collections dict alone
  (`storage.py:52-56`).
- **`PUT` silently unfiles a prompt.** `collection_id` is taken from the request body (`api.py:108`),
  so omitting it replaces it with the default `None` — and `tests/test_api.py:92-101` sends exactly
  such a body.
- **Navigation is asymmetric.** prompt → collection is a dict lookup; collection → prompts requires a
  full scan (`storage.py:58-59`, or `utils.py:17-18`).
- **The API never resolves the relation in either direction** — no nesting in any response envelope
  (`models.py:64-71`), so a client wanting a collection and its prompts makes two calls.
- **Collections carry `created_at` but no `updated_at`** (`models.py:55-56`), consistent with there
  being no update route for them at all.
- **Ids and timestamps are server-assigned** through `default_factory` (`models.py:35-37,55-56`) and
  are absent from the `*Create` DTOs, so a client cannot set or spoof them.
- `get_current_time` is `datetime.utcnow()` (`models.py:13-14`) — naive, no timezone.
- `Config.from_attributes = True` (`models.py:39-40,58-59`) is ORM mode; there is no ORM, so it is
  vestigial.

**Trap recorded, not acted on (Rule 0):** `tests/test_api.py:154-179` asserts the *current* orphaning
behaviour at line 178, guarded by `if prompts:`. That constrains Task 1.6 and is now noted in
`CLAUDE.md` under Known traps. No strategy was chosen here.

**Why my next prompt changed:**

The relationship is understood. What remains is the shape of §4 and how much of the schema detail
belongs in a section titled "how prompts and collections relate".

## Entry 25 — A second unverified "only", caught the same way as entry 16

**Stage:** 4 — Models and relationships. **Context level:** unchanged, whole-repo.

**Prompt sent:**

> It is the only field in the whole schema with no Field(...) constraint — a bare Optional[str]. Not a
> foreign key; the model layer knows nothing about collections. what do you mean by this?

**What came back:**

**A concession before the explanation: the sentence was false.** `PromptList`, `CollectionList` and
`HealthResponse` declare their fields with no `Field(...)` either (`models.py:64-76`). The defensible
claim is narrower — of the **six fields a client can supply**, `collection_id` is the only one carrying
no constraint.

**This is the second time the same failure mode has produced a wrong sentence in this session**, the
first being entry 16, and both were caught by the user rather than by me: an "only ..." quantifier
asserted over a set I had not actually enumerated. Entry 16 was about routes, this one about fields.
Two instances of one mechanism is a stronger candidate for `docs/ai-verification-note.md` than either
alone, and it is now on the record as such for Task 1.8.

The explanation itself, once corrected:

- **No `Field(...)`** — every other client-supplied field declares limits (`models.py:20-22,46-47`);
  `collection_id: Optional[str] = None` declares only a type, so any string passes. It is not typed
  `UUID` either, although every id is generated as one (`models.py:9-10`).
- **Not a foreign key** — a database engine enforces a foreign key *continuously* and also constrains
  the parent's deletion. Pydantic validates one object in isolation and has no access to stored
  collections, so it cannot know whether the string names anything. The check therefore has to live in
  a handler, which makes validity a property of a moment rather than of the data.

**Why my next prompt changed:**

The mechanism was clear, so the next prompt could settle the shape of section 4 and start reviewing it.

---

## Entry 26 — Section 4 built unit by unit under review

**Stage:** 4 — Models and relationships, write-up. **Context level:** unchanged.

**Prompts sent, in order:**

> The difference betwwen 1 and 3 is that 3 is more complete, right? In that case lets go for 3. But
> show me row by row, si I can accept it before moving to the next one.

> accept

> number 2 sais at write time, but shouldnt it be at read time? or you are refering that is on write
> time where we can make an impact on the relationship?

> strage.create_prompt and updat_prompt dont even have mention the collecton attribute, why do we even
> mention them?

> several questions here: 1 - self.prompts[prompt.id+] = prompt is just assigning a value to a key of
> the dict, in that dict it is true that we have the collection_id, that is what you mean?

> nevermind, lets go for DELETE / collections, you say it does not upholds this, but if we delete a
> collection, we delete all the prompts inside I guess... you say No becasue this will not break the
> link as both elements (collections and prompts) will be delted at the same time? Because otherwise
> the prompts will no longuer know how to refer to tha collection

> show me first exactly what you plan to add

> accept (three times, for 4.2, 4.3 and 4.4)

**What came back, and what each challenge changed:**

- **"at write time" was ambiguous and the wording changed.** The phrase meant *when the check runs*,
  not *when it matters*; no read path checks anything (`api.py:74`, `utils.py:18`). The cells now read
  "Yes — once, as the prompt is written", which also makes the closing sentence land: the two
  operations that can falsify the link later are in the same table, both marked No.
- **The storage row was challenged as padding, and survived with a stated rule.** The objection was
  fair — `main.py` does not mention `collection_id` either and nobody would list it. The table now
  declares its inclusion rule (sites that *write* the field or *hold the data to check it*), and the
  row earns its place on a point that only emerged under the challenge: **storage already contains
  `get_prompts_by_collection` (`storage.py:58-59`), which returns exactly the prompts a collection
  deletion would strand, and nothing in the application calls it.** The absence is not ignorance of
  collections; it is an unused capability.
- **The cascade premise was wrong, and was checked rather than argued.** The assumption was that
  deleting a collection deletes its prompts. Run through `TestClient`: collection gives 404, the prompt
  is still present with `collection_id` unchanged, and `GET /prompts?collection_id=<deleted id>` still
  returns it. **The link outlives its target and stays queryable by an id that resolves to nothing.**
  Recorded in 4.2 as an observation, with the method named.
- **Bug #4 was not decided** (Rule 0). What *should* happen stays in Open decisions for Task 1.6, and
  the constraint that `test_api.py:154-179` asserts the current behaviour is in Known traps.

`SYSTEM_MODEL.md` section 4 written in four parts, each accepted before the next was drafted: 4.1 the
shape of the link, 4.2 the audit table, 4.3 the consequences for a client, 4.4 the schema facts.

**Why this is a genuine iteration (C1.3): the review protocol changed the content, not just the pace.**
Three of the four challenges altered the deliverable — a reworded claim, a table that had to justify
its own membership rule, and a premise replaced by an executed observation. Reviewing unit by unit is
what made the challenges possible; a single finished section would have been accepted or rejected
whole.

**Why my next prompt changed:**

Section 4 is closed. Stage 5 is the Storage layer, which 4.2 has already partly characterised — the
next context decision has to take account of how much of it is now established.

---

## Entry 27 — Stage 5 opened: Storage layer, with the context level stated up front

**Prompt:**

> lets go for the stora layer explanation. Guide me through how it works and what are the limitations.
> I will load the whole context as the repo is small, but I guess I would only need the storage.py
> file. After investigation, tell me what is the pna on what you want to write, and lets confirm each
> part bit by bit to avoid cognitive overhead.

**What came back:**

`storage.py` read in full (69 lines). No section drafted yet — the reply was a **plan of four sub-parts**
(5.1 what the store is · 5.2 the operation surface · 5.3 how objects enter and leave · 5.4 the
limitations) to be confirmed one at a time, plus a challenge to the context rationale I gave.

**The challenge:** "the repo is small" is the **stage-1** rationale and I have already spent it
(§ Context Strategy row 1). C1.2 asks for a reason grounded in the size or coupling *of this stage's
code*, and reusing a size argument five stages in says nothing about the storage layer. Three angles
were offered — `storage.py` alone (it imports only `models`, so "how it works" is fully contained),
`storage.py` + the `api.py` call sites (a *limitation* is only a limitation relative to what a caller
needs, so the second half of the brief's question may not be answerable from the file alone), or
whole-repo again.

**Why this matters for the next prompt:**

The plan is deliberately split so that "how it works" and "what its limitations are" — the brief's two
halves — can take *different* context levels if that is the honest answer. Noted also that §4.2 already
established part of the storage picture (`get_prompts_by_collection` exists and is called by nothing),
so stage 5 must cite it rather than re-derive it.

---

## Entry 28 — Context level chosen for stage 5: two files, on a coupling argument

**Prompt:**

> I will go for B in tearms on context as I think is needed to understand the limitations

**What came back:**

`api.py` read alongside `storage.py`; the twelve call sites are `api.py:48,70,81,86,91,97,113,122,131,
137,146,155`. My reason was accepted but **sharpened so it names the coupling**, which is what C1.2
grades: `storage.py` calls nothing and is called from exactly one file, so the coupling is **total but
one-directional** — `storage.py` defines the whole supply, `api.py` the whole demand, and a limitation
is a gap between the two that neither file shows alone. The cost of B was stated: `tests/` is out of
scope this stage, so any constraint visible only from test usage will not surface. Nothing else was
pulled in — the duplicated collection filter in `utils.py` is already established in stage 3 and is
cited rather than re-read.

**Why the next prompt changed:**

Context settled; the four-part carve was left standing. Before drafting 5.1 I wanted the *purpose* of
each part rather than its content, so the structure could be judged before any prose existed.

---

## Entry 29 — The purpose of each sub-part, before any of it is written

**Prompt:**

> Explain the point of each process (5.1, 5.2, 5.3 and 5.4) and what do we intend to get from every of
> them.

**What came back:**

A table giving, for each part, the single question it answers, what it produces, and **what breaks in
the section if it is skipped** — deliberately no findings, so the structure is judged on its own. The
load-bearing point: the brief's two halves ("how it works" / "what its limitations are") map to
**5.1–5.3 and 5.4**, and 5.4 is only defensible because 5.2 has already tabulated the supply side —
without it, limitations degrade into generic "in-memory is not a database" observations that would not
be grounded in this code.

**Why the next prompt changed:**

Structure confirmed as purposeful rather than arbitrary, so drafting can start at 5.1.

---

## Entry 30 — 5.1 drafted, and one phrase challenged out of it

**Prompt:**

> go ahead with 5.1

then, on the draft:

> and the only join that exists is a scan (§5.2)... what do you mean by this? Regarding your 3 points:
> 1-Ok for this, but maybe specifiy it on "The container" paragraph, as it belongs there. 2- It is a
> property for sure, if its a limitation or not we will decide it in 5.4, but my guess is that is not a
> limitation, although a lot of times it would be unconvenient

**What came back, and what changed:**

- **A phrase was challenged as jargon and had to be replaced by the fact underneath it.** The draft
  said "the only join that exists is a scan (§5.2)", deferring the explanation to a later part. Asked
  what it meant, the answer is a property of the data structure, not of the method surface: there is no
  dictionary keyed by `collection_id` and no list of prompt ids on the collection, so
  `get_prompts_by_collection` (`storage.py:58-59`) **consults no index — it iterates every prompt and
  compares the field**. The relationship is recomputed per call and never stored.
- **The forward reference was therefore deleted.** The explanation moved *into* "The container", where
  the structural claim already lived — my instruction, and the right call: the fact is about the shape
  of the store, so it belongs in the paragraph about the shape of the store, not parked in a later
  sub-part.
- **The `str`-not-`UUID` key stays in 5.1 as a property, with the judgement explicitly deferred** to
  §5.4 ("Whether that counts as a limitation is left to §5.4"). My reasoning: a property and a
  limitation are different claims, and 5.1 is not the place to decide which it is.
- **`clear()` scoping settled.** The draft said "called by no route in `api.py`", the most context level
  B could honestly support. My ruling: the test suite is not part of the application code, so the
  stronger statement is legitimate. Verified by grep across `app/` — no caller — and written as "called
  by nothing in `app/` — it is a test-support affordance, not part of any request path."

§5.1 written to `docs/SYSTEM_MODEL.md`.

**Why the next prompt changed:**

5.1 fixed the shape of the store. 5.2 can now tabulate what that shape is asked to do.

---

## Entry 31 — 5.2 cut by return type, and stripped of everything that was really a limitation

**Prompt:**

> lets go for B

(from three offered cuts for the operation surface: A one flat ten-row table, B grouped by return type,
C a table with a symmetry column). Then, on the draft:

> I dont really understand the first pushing back point. The second one, both 2 facts are limitations
> but lets save them for 5.4. The third one I would say it is a limitation of the storage system as
> there is no duplicate id check or even prompt duplicate check with different id

then:

> go ahead

**What came back, and what changed:**

- **Cut B was chosen for a reason that connects to work already on the page.** Grouping the eleven
  methods by return type makes the contract visible: `Optional` getters force the caller to decide what
  absence means, `List` getters cannot signal absence at all, and the two `bool` deletes *are* their own
  existence check. That is precisely the split that produced the 404 discipline recorded in §2.3, so the
  storage section joins up with the entry-points section instead of restating it.
- **A pushback of mine was rejected as unclear and had to be re-explained without hedging.** I had
  asked whether "there is no duplicate-key check" belonged in a description of the surface at all, since
  ids are server-generated (§4.4) and no route can reach the overwrite. Restated plainly:
  `self._prompts[prompt.id] = prompt` (`storage.py:19`) silently replaces any existing entry. My ruling
  is that it is a property of the store whether or not a caller can reach it today — so it is a
  limitation, and it moves to §5.4 with the reachability caveat stated honestly.
- **My addition:** there is no duplicate-**content** check either — two prompts with identical title and
  content under different ids are both stored, and nothing looks for it.
- **Two passages were deleted from 5.2 on my instruction so that 5.4 discovers them.** The closing
  paragraph naming the missing collection-update method and `update_prompt`'s whole-object signature was
  removed entirely, not merely deferred by a cross-reference. Same for the duplicate-key sentence. §5.2
  is now purely descriptive — what the store offers and who calls it, nothing judged.

**Why this is a genuine iteration (C1.3): a constraint was added, and it removed content.** The
constraint is that a sub-part may only make claims of its own kind — 5.2 describes, 5.4 judges — and
applying it took three items *out* of a finished draft and onto a parked list carried in `CLAUDE.md`.
The usual direction of an iteration is to add; this one shrank the deliverable on purpose, so that the
limitations section is reached rather than pre-announced.

§5.2 written to `docs/SYSTEM_MODEL.md`.

**Why the next prompt changed:**

Supply side is on the page. 5.3 is the last descriptive part — whether the objects handed across that
surface are the stored ones — and it is the fact 5.4 needs before it can judge any of the four parked
items.
