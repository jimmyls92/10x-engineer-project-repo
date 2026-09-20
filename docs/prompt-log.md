# Prompt log

**Criterion C1.3.** Every prompt sent in this repository during Module 1, in order, with what came
back and why the next prompt changed. 89 entries, written live — each one appended before or
alongside the work it describes, never reconstructed afterwards.

The first person throughout is **the engineer prompting**, not the assistant. Prompts are quoted
verbatim, typos included; nothing here was tidied up after the fact.

**Tool:** Claude Code (Opus 5), run from the repository root.

**How the liveness is evidenced.** The log was kept as one shard per task under `docs/prompt-log/`,
and each shard was committed as it was written rather than at the end. The commit history of that
directory, interleaved with the code and document commits it describes, is the evidence that this
file was not written backwards from a finished repository. This file is the concatenation of those
shards in filename order, with the per-shard front matter dropped and nothing else changed.

## What the entries cover

| Entries | Task | Deliverable |
|---|---|---|
| 1-6 | Setup | Working protocol, `CLAUDE.md`, the log itself — and one discarded attempt |
| 7-40 | Task 1.1 / 1.2 | Staged exploration -> `docs/SYSTEM_MODEL.md`, six sections plus the context strategy |
| 41-73 | Tasks 1.3-1.7 | Bugs #1-#4 and `PATCH /prompts/{id}` |
| 74-75 | Task 1.8 | `docs/ai-verification-note.md` |
| 76-89 | Task 1.9 | Docstrings, the README, and the corrections the clean-clone test forced |

## The C1.3 iterations

C1.3 asks for at least two iterations that **narrowed context, added a constraint, or restructured** a
prompt because the output was not good enough — rewording does not count. Those are flagged in place,
inside the entry, with the reason the change was made. They are indexed here so they can be found
without reading 89 entries:

| Entry | Kind | What it did |
|---|---|---|
| **2** | added a constraint | Persist the working protocol instead of holding it in chat |
| **4** | added a constraint | Scope pushback, then verify by executing rather than reading |
| **5** | added a constraint | Shard the log to protect context, and make CLAUDE.md track task state |
| **6** | added a constraint | Discard the one-shot Task 1.1 and require step-by-step work |
| **8** | restructured the prompt | Reject one context decision for the whole task; stage it per section instead |
| **11** | narrowed context | Cut test and packaging files from the component list |
| **13** | added a constraint | Align every section name with the brief, and load the brief itself |
| **14** | narrowed context | Stage 2 walkthrough: every route in `api.py` |
| **16** | added a constraint | Catching an over-broad claim: `list_prompts` doesn't have that pattern either |
| **18** | added a constraint | Constrain the reply format: bullets, bold, brevity |
| **19** | narrowed context | Stage 3 context decision, and the walkthrough of the request path |
| **20** | restructured the prompt | Why "by leg" risks abstraction, and the shape that was settled |
| **21** | restructured the prompt | Shape corrected again: § Data flow becomes a per-route matrix |
| **22** | added a constraint | "How do you know?" — an inferred claim challenged and then executed |
| **26** | iteration | Section 4 built unit by unit under review |
| **31** | added a constraint | 5.2 cut by return type, and stripped of everything that was really a limitation |
| **32** | restructured the prompt | The section was restructured: a whole sub-part dropped as redundant |
| **34** | narrowed context | 5.3 written: shape chosen, two rows defended, one row corrected |
| **44** | added a constraint | The test obligation was checked against the brief, and my version of it was wrong |
| **45** | added a constraint | Commit messages audited against the brief; Rule 6 rewritten to require approval |
| **47** | restructured the prompt | All three angles, in order: read, execute, then write the test |
| **48** | narrowed context | Step 2: the bug observed by execution, in a throwaway probe |
| **49** | added a constraint | Step 3: the owed test written, and failing for the right reason |
| **59** | added a constraint | Task 1.6 step 1: the brief confirms the choice is mine, and adds an obligation |
| **65** | added a constraint | Task 1.6: full verbose run before committing |
| **77** | added a constraint | scope fixed at A, and the style guide is read instead of guessed |
| **80** | added a constraint | option B, plus a constraint the options did not offer |
| **81** | restructured the prompt | the whole repository is swept for comments that the fixes made false |
| **84** | restructured the prompt | a fourth option, from me rather than from the list |
| **86** | narrowed context | whether the defect had ever been documented, and what that exposed |

The flag's wording changed as the module went on — the earliest entries name the move in a sentence,
the later ones in a bracket after "C1.3". Rows reading simply *iteration* are the ones whose flag
names the move in prose; the entry itself says which of the three it was. Nothing was retrofitted to
make the index tidier.

---

## Entry 1 — Orient on the assignment before touching the code

**Stage:** Setup. **Context level:** single document (the brief PDF), no source files.

**Prompt sent:**

> I want yo to read document @1785592803-Module_1_Project_Brownfield_Challenge.pdf and guide me
> throught the presented tasks in order. We should solve them together paying attention to the
> different tips and recommendations. Read first the whole document to clearly understand the grading
> criteria and also because apparently there are some task consisting in "recording" my working
> process. Dont assume anything, ask in case you are not sure how to proceed.

**What came back:**

The PDF would not render through the built-in reader (no `pdftoppm` installed) and I declined the
suggestion to `pip install pypdf`. It fell back to a stdlib-only extraction script
(`zlib.decompress` over the PDF content streams, regex over the `Tj`/`TJ` text operators) and
recovered all six pages.

It then summarised the six criteria as a table, separating the two *process-evidence* criteria (C1.3
prompt log, C1.5 AI-verification note) from the deliverable criteria, and flagged the brief's warning
that the prompt log "cannot be convincingly reconstructed afterwards." It stopped before reading any
source file and asked three setup questions: how the prompt log should be captured, whether
exploration should be staged deliberately, and how to handle the AI-mistake evidence.

**Why my next prompt changed:**

Nothing was wrong with the answer — stopping to ask was right. But the whole protocol was living only
in the chat, which does not survive a new session or a context compaction. My next prompt added a
durability constraint rather than asking for more analysis.

---

## Entry 2 — Persist the working protocol instead of holding it in chat

**Stage:** Setup. **Context level:** none — no source files read yet, deliberately.

**Prompt sent** (answering the three setup questions):

> 1, but maybe we should wirte this reminder in some kind of CLAUDE.md, dont you think?
> 1, but again, should we remind this in a CLAUDE.md file?
> 1, should we include this rule in a CLAUDE.md file?

For all three I chose the first option — log written live after each exchange, exploration staged
deliberately, wait for a genuine AI mistake rather than manufacturing one — and on each one I pushed
for the rule to be written into a `CLAUDE.md` rather than left in conversation.

**What came back:**

Agreement, and `CLAUDE.md` written at the repo root before any source file was opened: the
deliverables table, working rules (log live and never reconstruct; stage exploration honestly; verify
every claim against source; capture AI mistakes when they happen; never hide a bug; meaningful
commits), work order, and verification command. The prompt log was opened at the same time.

**Why this is a genuine iteration (C1.3):**

Not a reword — a **constraint added**: the answer must survive a context reset, which meant writing to
disk instead of answering in chat. Different artefact, different output.

**Why my next prompt changed:**

Protocol durable and machine-read at session start, so setup looked closed. Next prompt moved to
Task 1.1.

---

## Entry 3 — First attempt at Task 1.1, Stage 1: whole-repo orientation

**Stage:** Exploration, stage 1. **Context level:** **whole-repo.**
**Note:** this attempt was later discarded — see entry 6.

**Prompt sent:**

> ok, lets do both of them and we start with tark 1.1

("both" = commit the protocol files, and check the Python environment.)

**What came back:**

Protocol commit `5e081ae`, made before any source file was opened. Environment confirmed without a
venv: fastapi 0.141.1, pydantic 2.13.5, pytest 9.1.1, httpx 0.28.1 — all well ahead of the pins in
`requirements.txt`. Then all nine source files read in one pass, plus a baseline test run:

```
3 failed, 10 passed
FAILED test_get_prompt_not_found  - AttributeError
FAILED test_delete_prompt         - AttributeError
FAILED test_sorting_order         - assert 'First' == 'Second'
```

Findings beyond the four seeded bugs: three functions defined but never called; the storage singleton
handing out live object references; `allow_origins=["*"]` combined with `allow_credentials=True`;
`datetime.utcnow()` deprecated and naive; and PUT nulling `collection_id` when the field is omitted.

**Why my next prompt changed:**

I did not send the next prompt as planned — the reply had ended by asking me to choose a Bug #4
strategy, which belongs to Task 1.6. That prompted a scope objection instead.

---

## Entry 4 — Scope pushback, then verify by executing rather than reading

**Stage:** Exploration, stage 2. **Context level:** **narrowed — one behaviour per probe, answered by
execution rather than by reading.** **Note:** discarded with entry 3 — see entry 6.

**Prompt sent:**

> I am confused, I dont think we need to reply to this for Task 1.1, I think, although we have the
> whole context, we should assume we just want to answer what is written in the task and evaluated in
> the rubric. Or what you are saying is related to this in any manner?

**What came back:**

The scope objection was accepted and the Bug #4 decision parked until Task 1.6. One real link was
noted — `get_prompts_by_collection` is the helper a Bug #4 fix would use, which is probably why the
previous developer wrote it and never wired it up. Rather than assert it was dead code, `grep`
confirmed definitions and no call sites.

A nine-probe script then ran against `TestClient(raise_server_exceptions=False)`:

```
1. missing prompt            -> real HTTP 500 (not just a test-client exception)
2. PUT omitting collection_id-> 200, collection_id silently becomes None
3. PUT omitting content      -> 422; PUT genuinely requires every field
4. storage.get_prompt(...)   -> live reference; mutating it changed the store
5. search=UNIQUEWORD (body)  -> 0 hits; search never looks at content
6. total                     -> counts the filtered set, not the store
7. POST, unknown collection  -> 400 (not 404)
8. /docs /redoc /openapi.json-> all 200; 5 declared paths
9. created_at vs updated_at  -> DIFFER by ~6us on create; both naive, no timezone
```

Probe 9 justified the stage: in source, `created_at` and `updated_at` are two identical
`default_factory=get_current_time` lines and read as the same instant. They are two separate calls and
differ. Writing the system model from reading alone would have produced a claim contradicting the
code. `docs/SYSTEM_MODEL.md` was then written in one pass.

**Why this is a genuine iteration (C1.3):**

Two changes, neither cosmetic. A **scope constraint** — answer only what the current task and rubric
ask. And a **change in the kind of context**: stage 1 supplied source text, stage 2 supplied observed
behaviour, because further reading could not settle the open questions.

**Why my next prompt changed:**

The log was growing fast enough to threaten context on later tasks, so the next prompt addressed
process rather than code.

---

## Entry 5 — Shard the log to protect context, and make CLAUDE.md track task state

**Stage:** Setup. **Context level:** none — no source files involved.

**Prompt sent:**

> CLAUDE.md should trak in which task we are currently working, and when facing a task focus only in
> what is asked in the task and evaluated in the rubric. To avoid getting ahead as you did before.
> Also we need a strategy to keep prompt-log.md below a dangerous token headcount, I propose to create
> one promp-log.md per task and then merge them at the end of the assigment. CLAUDE.md should also
> have this information to know which one he should load in function of the task. This will also allow
> us to retake the work where we left it and stick to the log recording without reaching context rot.
> Ask clarifying questions in case this strategy is not 100% defined for you.

**What came back:**

Three clarifying questions, then implementation of my answers: shard by the brief's task numbers,
splitting further only if a shard grows large; keep the shards committed as we go rather than deleting
them at merge; merge once at the end as its own commit. Two things I had not specified were flagged —
the merged file must land at exactly `docs/prompt-log.md` because the rubric names that path, and
CLAUDE.md needs a resume pointer rather than only a task number, or a fresh session still would not
know what is half-finished.

**Why this is a genuine iteration (C1.3):**

Changed the working method, not a prompt's wording. Two constraints added: **scope** (answer only the
current task) and **context budget** (shard the log so later tasks load one small file). The trigger
was output drifting ahead of the task, and a log on its way to being unloadable.

**Why my next prompt changed:**

Re-reading the Task 1.1 output, I realised the deeper problem was not the log's size. The whole task
had been completed in a single reply. The result was fine and I had learned nothing from it, which
defeats the point of the exercise.

---

## Entry 6 — Discard the one-shot Task 1.1 and require step-by-step work

**Stage:** Setup. **Context level:** none — process only.

**Prompt sent:**

> Another hard rule for CLAUDE.md, follow each task step by step, this is an educational project, so
> propose prompts, or actions on my side for each of these steps to ensure the highest educational
> outcome. You just did Task1.1 on one shot and this is what we want to avoid, I did not learn
> anything out of this. Delete SYSTEM_MODEL.md and copy all the prompt log from task1.1 into the log
> file 00-setup.md. Then erase the log of task 1.1 and 1.2. Once you are done, I will clear the
> context to see if our CLAUDE.md is working as expected and we retake from the beginning of task 1
> and we do it step by step in an educational manner as expected. Let me know if this is 100% clear
> for you and in case not, ask clarifying questions.

**What came back:**

Three clarifying questions before any destructive action, one of which I disagreed with and
overrode — I decided that *everything* in that session counted as setup, so the discarded Task 1.1
work should be preserved here as history rather than deleted, and no separate "we restarted" note was
needed because this entry is that record.

On how prescriptive the coaching should be, I chose goal-plus-options over full draft prompts: at each
step I am told what the step should achieve and two or three angles it could take, and I write the
actual prompt. The reasoning was that choosing the angle is the skill being taught, and that prompts
drafted for me would weaken the C1.3 evidence, which grades iteration I drove.

Then: `docs/SYSTEM_MODEL.md` deleted, `docs/prompt-log/01-tasks-1.1-1.2.md` emptied to a stub, this
file rewritten to hold all six entries, and CLAUDE.md given a step-by-step rule plus a CURRENT STATE
block pointing at the start of Task 1.1.

**Why this is a genuine iteration (C1.3):**

The strongest one so far, and it cost real work — a finished, verified deliverable was deleted on
purpose. The constraint added is about **the shape of the collaboration, not the content of a
prompt**: never complete a task in one reply; break it into steps, hand back at each one. The trigger
was noticing that a correct output had produced no understanding on my side. Everything before this
was about making the AI's output better; this was about making my own involvement real.

**Why my next prompt changed:**

Context deliberately cleared after this entry, to test whether CLAUDE.md alone can resume the work
correctly. Task 1.1 restarts from zero, step by step.

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

## Entry 32 — The section was restructured: a whole sub-part dropped as redundant

**Prompt:**

> the data flow was already stablished before, in that case 5.4 is now 5.3 and avoid repeating again

**What came back:**

Agreed and applied. The planned **5.3 "how objects enter and leave" was deleted, not merged** — §3 (Data
flow) already established that storage hands out and files away uncopied objects (`storage.py:19,23,26`)
and that `PUT` rebuilds rather than mutates (`api.py:103-111`), all verified at the time. The three
angles I had been offered for 5.3 (cite and move on / cite and trace the consequence / re-verify by
execution) were all answers to a question that had already been answered. Limitations moves up to
**§5.3**, and any limitation that rests on object identity cites §3 instead of restating it. The carve
is now 5.1 · 5.2 · 5.3.

**Why this is a genuine iteration (C1.3): the deliverable was restructured, not reworded.** A planned
sub-part was removed from a document in progress because its content already existed elsewhere in the
same document. The proposal to write it came from me; the recognition that §3 had covered it came from
me as the user. Recorded here because the visible result is an *absent* section, which nothing in the
finished `SYSTEM_MODEL.md` would otherwise explain.

**Why the next prompt changed:**

Description is finished. Everything remaining in the section is judgement, including the four items
parked out of 5.2.

---

## Entry 33 — "Unreachable" was challenged and turned out to be the wrong word

**Prompt:**

> why the duplication-id is unreachable? it cant effectivly happen?

**What came back:**

I had flagged, while offering shapes for the limitations section, that the duplicate-id overwrite is
"unreachable today". Challenged, the chain was actually traced instead of asserted: `id` is absent from
`PromptCreate`/`CollectionCreate` (`models.py:26-27,50-51`) and declared only on the entity models
(`models.py:35,55`); Pydantic drops unknown keys by default so a body containing `"id"` never reaches
the handler; `api.py:85,145` build from the DTO so `default_factory=generate_id` always fires
(`models.py:9-10`); and `PUT` reuses `existing.id` (`api.py:104`). A collision would therefore require
two `uuid4` values to collide.

**The correction I forced:** "unreachable" overstated it, and — more importantly — deflating the item
was the wrong move. The accurate framing is that **the store promises nothing and the safety lives
entirely in `models.py`**, a different module under a different concern. `storage.py:19,43` overwrite
whatever is present, silently. A store that is safe only because of how its callers happen to build
their arguments is exactly the supply/demand gap that context level B was chosen to expose, so the
limitation stands — with the masking named rather than omitted.

**A sibling surfaced from tracing it:** `update_prompt` writes `self._prompts[prompt_id] = prompt`
(`storage.py:31`) and never checks that `prompt.id == prompt_id`. Nothing in the store prevents the key
and the stored object's own id from disagreeing; today only `api.py:104` does. Unlike the duplicate-id
overwrite, this one is reachable by any new write path.

**Why the next prompt changed:**

The item had to be written as "no guarantee, currently masked" rather than as "cannot happen", which
means the shape chosen for the section has to leave room for a caveat per row.

---

## Entry 34 — 5.3 written: shape chosen, two rows defended, one row corrected

**Prompt:**

> lets go with C, and add that sibling to the list

then, on the draft:

> one could argue that 2 and 3 are coupled right, as the storage object is created in teh storage
> script both thins are consecuence of this decission. what do you think? 4- concurrency could also be
> managed from the api side, right?

then:

> ok, keep both rows and rewrite 4, go ahead.

**What came back, and what changed:**

- **Shape C chosen: a single thirteen-row table**, each row carrying the limitation, its evidence in
  `storage.py`, and what it costs the caller with the `api.py` line. Chosen over grouping by cause or by
  consequence because the two evidence columns make the supply/demand gap literal — which is the whole
  reason this stage read both files.
- **My first challenge was tested rather than accepted.** I observed that rows 2 (one instance, no seam)
  and 3 (state is per-process) both descend from `storage.py:69`. The test applied was whether each can
  be fixed without the other: a factory or injected dependency removes row 2 and leaves row 3; moving to
  a shared external store removes row 3 and leaves row 2. **Separately fixable, so two limitations with
  one origin** — kept as two rows, with the shared cause now stated explicitly in the document instead
  of left for a reader to notice.
- **My second challenge produced an outright correction.** "No concurrency control" was wrong as
  written: a lock in `api.py` around `91→113` would serialise that sequence, so the absence is not
  unfixable from outside. Row 4 was rewritten to the narrower and truer claim — **the store offers no
  primitive to build it with**: no atomic update, no compare-and-set, no version field, and no method
  combining a read with a conditional write. Any solution must live outside the layer and be applied at
  every call site by convention.
- **That rewrite revealed a shape shared by three rows.** Rows 4, 5 and 6 are all "the guarantee is
  absent from the storage layer, and whatever stands in for it today is somewhere else" — `api.py` for
  4 and 6, `models.py` for 5. Note A now says so, which turns three separate observations into one
  characterisation of the layer.
- **Row 13 deliberately stops short** of saying what *should* happen on collection deletion. It cites
  §4.2 and leaves the decision to Task 1.6 (Rule 0).

**Why this is a genuine iteration (C1.3): a claim was narrowed under challenge.** The prompt did not
ask for a rewording — it asked whether a limitation attributed to the storage layer could be answered
from the API layer. It could, so the claim was too broad, and the replacement is a different and
smaller assertion about what the store *provides* rather than about what the system *lacks*.

§5.3 written to `docs/SYSTEM_MODEL.md`. Rows 10, 11 and 13 stood as drafted; I was asked about them and
raised no objection.

**Why the next prompt changed:**

All three sub-parts are written. What remains for stage 5 is the § Context Strategy row, which by
standing convention is written last so it records what the stage actually did.

---

## Entry 35 — What C1.2 actually requires, and the stage-5 row

**Prompt:**

> sorry Im getting lost, those questions, how are related to C1.2?

then:

> write the minimal row with the tests/ clause

**What came back:**

A fair challenge, and the answer was to concede the framing rather than defend it. I had offered two
questions — whether the row should report the cost of the level chosen, and whether it should report
that a sub-part was dropped — as if they were part of the requirement. **They were not.** C1.2 asks for
three things per stage: which context level was used, a reason grounded in size or coupling, and
agreement with the prompt log. All three were already settled for stage 5 by entry 28, so the row
passed before either question was raised. Presenting optional additions as open requirements is what
caused the confusion.

With the requirement restated, the recommendation narrowed to one addition and a rejection of the
other: keep the `tests/` exclusion, because it is a direct consequence of the level chosen and so
belongs in a column about that choice; drop the §3 point, because entry 32 already records it and the
row is not the place to repeat the log.

Row 5 written to `SYSTEM_MODEL.md` § Context Strategy. Rows 1–4 untouched.

**Why the next prompt changed:**

Stage 5 is complete — §5.1, §5.2, §5.3 and the Context Strategy row. Next is stage 6, External
dependencies, the last section of Task 1.1.

---

## Entry 36 — Stage 6 opened: External dependencies

**Stage:** 6 — External dependencies, before exploration. **Context level:** not yet chosen — that is
this step's decision.

**Prompt sent:**

> lets continue with stage 6, external dependencies

**What came back:**

No exploration yet. The step was set up rather than answered: stage 6 is the last section of Task 1.1,
and under Rule 2 its context level has to be argued from the **size or coupling** of the code before
any file is opened. Three levels were offered — `requirements.txt` alone, a supply-vs-demand pair
(declared list against the imports actually made), and whole-repo including `tests/`, `main.py` and
`config.yaml` — with the trade-off stated as what each level can and cannot see: a declared-only read
cannot detect a package that is imported but never declared, and a runtime-only read cannot detect a
package that is declared but never used.

Also flagged: the brief's gloss is "everything the service relies on", which is wider than the pip
list, so the level chosen partly decides how wide the section can honestly be.

**Why my next prompt changed:**

The trade-off table made the cost of each level explicit, so the next prompt could name one.

---

## Entry 37 — Stage 6 read at level B: the declared list against the imports actually made

**Stage:** 6 — External dependencies. **Context level:** **B — two surfaces**: `backend/requirements.txt`
(supply) read against every `import` statement in `backend/app/*.py` and `backend/main.py` (demand).
`tests/` deliberately excluded.

**Prompt sent:**

> lets go with B

**Why this level, in the terms C1.2 asks for (coupling, not size):** a dependency list is a *declaration*
and an import is a *use*, and the two are not checked against each other by anything in the repo. That
is the same supply-and-demand coupling that justified reading `storage.py` with `api.py` in stage 5:
neither file alone contains the finding, because the finding is the gap between them. Reading only
`requirements.txt` could not detect a package relied on but never declared; reading only the imports
could not detect a package declared but never used. Both defects are present, so both surfaces were
needed.

**What came back — the gap, in both directions:**

- **Declared with no importer anywhere in the runtime surface: three of six.** `pytest`, `pytest-cov`
  and `httpx` appear in `requirements.txt:4-6` and in no `import` under `app/` or `main.py`. Level B can
  see the absence but cannot explain it — the explanation is in the excluded `tests/`. Recorded as the
  cost of the level, not resolved by it.
- **Relied on but never declared: `starlette`.** `api.py:4` imports `CORSMiddleware` from
  `fastapi.middleware.cors`, which is a re-export —
  `CORSMiddleware.__module__` is `starlette.middleware.cors`, checked by execution rather than assumed.
  The service depends on Starlette directly through the FastAPI namespace, and the version it gets is
  whatever `fastapi==0.109.0` resolves to.
- **Relied on and not declarable as a package at all: the Python runtime.** There is no
  `pyproject.toml`, no `setup.py`, no `python_requires`, no `.python-version`. Nothing in the repository
  states a supported interpreter version, although the pinned `pydantic==2.5.3` bounds one in practice.
- **`uvicorn` is a dependency of one entry path only.** It is imported at `main.py:6` and used at
  `main.py:10`, inside the `if __name__ == "__main__"` guard. Served by any external ASGI runner against
  `app.api:app`, uvicorn is never touched.
- **Standard library demand:** `typing`, `datetime`, `uuid`, and `re`. `re` is the odd one — imported
  *inside a function body* at `utils.py:48`, in `extract_variables`, which nothing in the application
  calls.
- **Pinning discipline:** all six are exact `==` pins; no ranges, and no lock file of any kind.
- **Confirming stage 1 from the demand side:** no database driver, no HTTP client used by the
  application itself, no LLM SDK. The only external system the service relies on is the memory of its
  own process.

**Why my next prompt changed:**

Pending — the findings exist; the next prompt settles the shape of § External dependencies.

---

## Entry 38 — Asked to continue; offered three shapes for § 6

**Stage:** 6 — External dependencies, write-up step. No new reading; the level-B findings from entry 37
are the material.

**Prompt sent:**

> lets continue with the next task

**What came back:** not the section. Three candidate shapes for § 6, with the trade-off between them:

| Shape | Organising principle | What it makes visible | What it buries |
|---|---|---|---|
| **A — one table per declared package** | the six lines of `requirements.txt` | version pin, purpose, where imported | the undeclared `starlette` and the unstated interpreter, which have no row to live in |
| **B — by kind of reliance** (declared runtime · declared but unimported · undeclared but relied on · standard library · unstated runtime) | *how* the service depends, not *what* on | exactly the two-directional gap level B was chosen to find | the at-a-glance version table an assessor scans for |
| **C — B's sections, with A's table as the first of them** | both | the pins *and* the gap | nothing; costs length |

Flagged that C1.1 requires **every** external dependency, and that "every" is the whole reason the
undeclared and the unstated ones have to appear somewhere — shape A has no place to put them.

**Why my next prompt changed:**

It did not change shape yet — I stopped on a word. `starlette` appeared in the level-B findings as the
undeclared dependency, and I could not weigh shape A against shape C without knowing whether it was a
real dependency or a detail of how FastAPI is packaged. Asking was cheaper than choosing blind.

---

## Entry 39 — Asked what Starlette is before choosing the shape

**Stage:** 6, still at the shape decision. No writing done.

**Prompt sent:**

> what is starlette?

**What came back:** Starlette is the ASGI toolkit FastAPI is built on — `FastAPI` subclasses
Starlette's application class and adds the Pydantic/OpenAPI layer over it, so routing, the
request/response objects, middleware and the test client are all Starlette's. Three touch points in
this repository were named: the `CORSMiddleware` re-export at `api.py:4`, the `TestClient` used in
`tests/` (Starlette's, wrapping `httpx` — the same object behind the `raise_server_exceptions` trap),
and the ASGI app object uvicorn serves.

The point that mattered for the decision: Starlette is never named in `requirements.txt`, arrives
transitively through `fastapi==0.109.0`, and is nonetheless imported from **by hand** in the source.
That is the "relied on but undeclared" case — and the one shape A has no row for.

**Why my next prompt changed:** the answer settled the shape question rather than reopening it. Once
Starlette was confirmed as a genuine direct reliance, a package-by-package table could not be complete
on its own, so the choice collapsed to C.

---

## Entry 40 — Shape C chosen; § 6 and the stage-6 context row written

**Stage:** 6 — write-up. This is the step that closes Task 1.1's checklist.

**Prompt sent:**

> Lets go for C

**What came back:** § 6 External dependencies, in six parts — 6.1 the declared list (all six pins, with
the import site of each), 6.2 declared but imported by nothing the application runs, 6.3 relied on but
declared nowhere, 6.4 the standard library surface, 6.5 the unstated interpreter, 6.6 what the service
does not depend on. Plus the stage-6 row in § Context Strategy, and the status note at the head of the
document updated now that all six checklist sections exist.

**One finding that was not in entry 37**, surfaced while verifying the pins before writing them down:
the installed FastAPI reports **`0.141.1` against a pinned `0.109.0`**. Nothing in the repository
detects the divergence — no version assertion, no CI check, no lock file. Recorded in §6.1 as the
difference between a declaration and a guarantee.

**Honesty note carried into the row:** §6.2 attributes `pytest`/`httpx` to `tests/conftest.py:3-4` and
`test_api.py:7-8`, which stage 6's level-B context excluded. The attribution comes from the stage-4
whole-repo reading and the § Context Strategy row says so, rather than letting the row claim a
narrower context than the section actually rests on.

**Why my next prompt changed:** § Architecture through § External dependencies are all written, so
Task 1.1 is done and the next prompt starts Task 1.3.

---

## Entry 41 — Task 1.3 opened; baseline before fix

**Task:** 1.3 — Bug #1, `GET /prompts/{id}` returns 500 instead of 404.

**Prompt sent:**

> no its fine, keep it and move on to task 1.3

(The first clause settles the previous turn: the FastAPI pin-divergence paragraph written into §6.1
without a step of its own stays as written. See entry 40.)

**What came back:** not a fix. The bug site was located and the step was framed as *establish the
baseline first*, with three scopes offered:

| Scope | What it runs | What it buys |
|---|---|---|
| A | the one provided test, `test_get_prompt_not_found` | the exact failure this task owes a fix for, and nothing else |
| B | the whole suite | the before-picture of all four bugs at once, so C1.4's "nothing previously working broken" has a recorded starting point |
| C | no baseline — fix straight away | speed, at the cost of no evidence the test failed before it passed |

Facts established while framing the step, cited rather than re-derived:

- The bug is `api.py:70-72`. `storage.get_prompt` returns `Optional[Prompt]`, and `if prompt.id:`
  dereferences before guarding — the one place in the file where that happens (§2.3 of the system
  model).
- There is a **second** defect in the same handler, independent of the 500: if the guard is ever
  falsy, the function falls off the end and returns `None` against a `response_model=Prompt`.
- The provided test is `tests/test_api.py:61-69` and asserts `404`.
- Known trap, already recorded: `TestClient` defaults to `raise_server_exceptions=True`, so the
  failure will surface as a raised `AttributeError`, not as an assertion against a 500 response.

**Why my next prompt changed:**

Pending — awaiting the choice of baseline scope.

---

## Entry 42 — Baseline recorded: 3 failed, 10 passed

**Task:** 1.3, baseline step.

**Prompt sent:**

> lets go with B

**What came back:** `python -m pytest tests/ -v` before any change. **3 failed, 10 passed.**

| Test | Result | Reads on |
|---|---|---|
| `test_health_check` | PASSED | |
| `test_create_prompt` | PASSED | |
| `test_list_prompts_empty` | PASSED | |
| `test_list_prompts_with_data` | PASSED | |
| `test_get_prompt_success` | PASSED | |
| `test_get_prompt_not_found` | **FAILED** — `AttributeError` at `app/api.py:73` | Bug #1 |
| `test_delete_prompt` | **FAILED** — `AttributeError` at `app/api.py:73` | Bug #1 |
| `test_update_prompt` | PASSED | |
| `test_sorting_order` | **FAILED** — `assert 'First' == 'Second'` | Bug #3 |
| `test_create_collection` | PASSED | |
| `test_list_collections` | PASSED | |
| `test_get_collection_not_found` | PASSED | |
| `test_delete_collection_with_prompts` | PASSED | |

**Three things the whole-suite scope bought that scope A would not have:**

1. **Bug #1 breaks two tests, not one.** `test_delete_prompt` fails at the same `api.py:73` — after
   deleting, it re-fetches and expects `404` or `500` (`test_api.py:83`), and the handler raises before
   either can be returned. The task owes a fix that turns both green.
2. **The trap held.** Both Bug #1 failures are a raised `AttributeError`, not a `500` response, exactly
   as `raise_server_exceptions=True` predicted. Nothing had to be discovered the hard way.
3. **Bugs #2 and #4 have no failing test.** `test_update_prompt` passes with the `updated_at` bug
   present, and `test_delete_collection_with_prompts` passes *because* it asserts the orphaning
   behaviour. Those two tasks will have to bring their own test; Bug #1 and Bug #3 have one provided.

This is the recorded starting point C1.4's "nothing previously working broken" is measured against:
**the ten passing tests above must still pass at the end.**

**Why my next prompt changed:**

Pending — the baseline is evidence, not a fix. The next prompt settles the shape of the fix.

---

## Entry 43 — Fix applied in shape A; suite goes 3 failed → 1 failed

**Task:** 1.3, fix step. Preceded by entry 42a below — a correction I had to make before the choice
could be made honestly.

**Prompt sent:**

> If I undestand correctly C would create another Bug, right?

**What came back — a correction of my own previous message.** I had listed, against option C (push the
404 into `storage.py`), that it "would break `create_prompt`'s 400 path". That was **wrong**:
`create_prompt` calls `storage.get_collection` (`api.py:81`), not `get_prompt`. `get_prompt` has exactly
two callers, `api.py:70` and `api.py:91`, and both want a 404 on a miss — so C would not have produced
a wrong response at all.

The honest objection to C is **layering, not correctness**: `storage.py` imports only `typing` and
`app.models` (`storage.py:7-8`), so raising `HTTPException` there would make a layer that knows nothing
about HTTP unusable outside an HTTP app, contradict the `Optional[Prompt]` contract recorded in §5.2,
and leave no way for a future caller to *ask* whether a prompt exists without catching an exception.

*Flagged for C1.5: this is a wrong AI claim, caught by checking the call sites rather than trusting the
summary. Candidate for `docs/ai-verification-note.md`.*

**Prompt sent:**

> Lets go for A, then

**What came back — the fix.** `api.py:66-73` reduced to the idiom `get_collection` already uses at
`api.py:137-140`:

```python
@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
```

Both defects go at once: the dereference is gone because the guard now precedes it, and the
fall-off-the-end `None` against `response_model=Prompt` is gone because the early raise leaves only one
exit. The detail string matches `delete_prompt` (`api.py:123`), so the two prompt 404s read alike. The
three BUG comments were removed with the bug — leaving them would describe code that no longer exists.

**Suite after the fix: 1 failed, 12 passed** (from 3 failed, 10 passed).

- `test_get_prompt_not_found` — PASSED
- `test_delete_prompt` — PASSED
- `test_sorting_order` — still FAILED; that is Bug #3, Task 1.5, and untouched here
- All ten tests passing at baseline still pass. C1.4's "nothing previously working broken" holds so far.

**Why my next prompt changed:**

Pending — the provided test is green, but the work order says each fix carries a test of its own, so
the next prompt settles whether one is owed here and what it should assert.

---

## Entry 44 — The test obligation was checked against the brief, and my version of it was wrong

**Task:** 1.3, closing step.

**Prompt sent:**

> My understanding from the document is that we do not have to provide any further test, wouldnt you
> agree? Rereade the document to answer this question

**Why this prompt matters (C1.3 — added a constraint).** I had just been offered three angles for an
*additional* test. The prompt refused the frame and sent me back to the source instead: the constraint
added is "answer from the brief, not from your own summary of it."

**What came back — agreement, and the reason it had been got wrong.** The "each fix carries a test"
line came from `CLAUDE.md`'s work order, which I had written, not from the brief. The brief is per-task
and deliberately uneven:

| Task | The brief's own words | Test owed? |
|---|---|---|
| Bug #1 | "fix it to return a proper 404, and **make the provided test pass**" (line 57) | **No** |
| Bug #2 | "**verify with a test**" (line 60) | Yes |
| Bug #3 | "fix the order, **verify**" (line 63) | Not as a test; one is provided |
| Bug #4 | "implement it, and **add a test**" (line 66) | Yes, explicitly |
| PATCH | four behaviour checkboxes, no test wording (67–71) | No |

And C1.4's evidence line asks that "all **provided** tests pass and nothing that worked before is
broken" (line 186) — it never asks for tests the student wrote.

So Task 1.3 owes no further test. The provided `test_get_prompt_not_found` is green and the ten
baseline passes are intact.

**Prompt sent:**

> Lets go for 1 and 2 in the same commit

**What came back:** `CLAUDE.md` corrected in the same commit as the fix — the work order now carries
the per-task wording above instead of "each with a test", a Known Trap records the distinction so it is
not re-litigated at Task 1.5, and CURRENT STATE moves to Task 1.4.

**Why my next prompt changed:**

Task 1.3 is closed. The next prompt opens Task 1.4 — Bug #2, `updated_at` unchanged on PUT — which is
the first task that does owe a test of its own.

---

## Entry 45 — Commit messages audited against the brief; Rule 6 rewritten to require approval

**Task:** protocol, running alongside 1.4. No code touched.

**Prompt sent:**

> I saw that the document @1785592803-Module_1_Project_Brownfield_Challenge.pdf says meaningfull commit
> messages, do you think we are delivering so far? Please add to CLAUDE.md to ask me for my approval on
> the commit message before comitting

**Why this prompt matters (C1.3 — added a constraint).** It adds a standing constraint to the working
protocol rather than to a single output: every future commit message must be approved before it is
written. It also asks for an honest audit of work already committed, which is a different question from
"is the next one good".

**What came back — the audit of the fourteen commits written in this repository.** Verdict: above the
bar, with two real weaknesses.

Holding up: imperative subjects that name the task and criterion; bodies that give the *why* rather than
restating the diff; `file.py:line` citations; and decisions recorded that leave no trace in the diff at
all — `1a0e98d` exists to explain a sub-section that was deliberately *not* written.

Two weaknesses, both mine:

1. **Bundling.** `acf6440` carries the Bug #1 fix *and* a correction to `CLAUDE.md`'s work order, and
   `45afbbc` carries §6, the Context Strategy row and two bookkeeping files. `CLAUDE.md`'s own Rule 6
   says one logical change per commit. The first was asked for explicitly and is the user's call; the
   habit is still worth naming.
2. **Length.** Several bodies run past twenty lines. Meaningful is not the same as maximal, and a
   grader reading fourteen essays is being asked for patience the rubric does not require.

**What was done:** Rule 6 rewritten. It now requires the full message to be shown in chat and approved
before `git commit` runs — with the explicit note that "commit it" in a prompt approves the *commit*,
not the *message* — and it records the subject/body conventions and the no-bundling rule that the audit
found were being followed by habit rather than by rule.

**The rule was then tightened twice, by the user, over three more prompts.** The first draft of the
message for this very change ran twelve lines — the habit the audit had just named, reappearing in the
message about it. Trimmed to six, it was still too long:

> I think a commit should not be more than 2 sentences long. Wouldnt you agree? Around 20 characters
> tops

I agreed on two sentences and pushed back on twenty characters, showing what that budget actually buys
(`Require commit appr` is already over) and offering fifty characters — the git convention — for the
subject instead. The reply was "yeah, I meant words".

**The standing rule, now written into Rule 6:** subject imperative and **≤ 50 characters**; body **at
most two sentences of about twenty words**; nothing else — no bullets, no "Also …" paragraph, no test
tables. Bundling is what makes two sentences insufficient, so the no-bundling rule carries the weight.
Earlier commits stay as they were written; rewriting history to match a later convention would be worse
than the inconsistency.

**Why my next prompt changed:**

The protocol question is settled. The next prompt returns to Task 1.4 — Bug #2, `updated_at` unchanged
on PUT.

---

## Entry 46 — Task 1.4 opened: Bug #2, `updated_at` unchanged on PUT

**Task:** 1.4, step 1 of the step-by-step run.

**Prompt sent:**

> Lets go with task 1.4

**What came back.** No analysis and no fix — the reply set up step 1 only, as Rule 0b requires. The
brief's wording for Bug #2 is *"Find where updates are handled, set `updated_at` to the current time,
and verify with a test"*, and Task 1.3 already established that **no provided test fails for this bug**:
`test_update_prompt` passes with the bug present. So the task owes a test that does not exist yet, and
step 1 is about deciding how the bug is going to be *observed* before anything is changed.

Three angles were offered for the step-1 prompt: observe it by execution first (drive a PUT through
`TestClient` and look at the two timestamps); read the handler and the model statically and reason out
the cause; or go straight to writing the failing test the brief owes and let it be the observation.

**Why my next prompt changed:** to be written when I send it.

---

## Entry 47 — All three angles, in order: read, execute, then write the test

**Task:** 1.4, steps 1–3. This entry covers the read.

**Prompts sent (two, the first a question about the previous reply):**

> I think since its asking for a test on our own, the correct choice will be C, but I dont get 100% the
> trade-off you are talking about

> I think we can do the three of them. Read, then execute and then create the test

**What came back to the first.** The trade-off spelled out: a red test says only *"this assertion did
not hold"*, never *why*. Test-first collapses observation and verification into one artifact, so the
first red run cannot distinguish the genuine bug from a wrong field name (`KeyError`), a string-versus-
`datetime` comparison, or a strict `>` on two calls landing in the same clock tick — and `utcnow()` is
naive (`models.py:13-14`), so there is no timezone to disambiguate. The mitigation offered was to make
the first failure informative rather than to abandon the angle.

**Why my second prompt matters (C1.3 — restructured).** Rather than picking one of the three angles, I
restructured the step into a sequence of all three: read for the mechanism, execute to see the real
payload, then write the test against what was actually observed. That removes the ambiguity the
trade-off described instead of mitigating it — the test is now written with the response shape and the
timestamp values already in hand.

**What came back — the read.** Reported in the chat reply, not reproduced here; the findings are carried
into `CLAUDE.md`'s *Established in Task 1.4* block once the step closes.

**Why my next prompt changed:** the read is done; next is the execution that confirms it.

---

## Entry 48 — Step 2: the bug observed by execution, in a throwaway probe

**Task:** 1.4, step 2.

**Prompt sent:**

> I think the first one should be enough as we will create later a test with that information. any
> objections?

**Why this prompt matters (C1.3 — narrowed).** It rejects the two heavier angles (temporarily applying
the fix; forcing clock separation with a sleep) and narrows step 2 to a single throwaway script with no
repository footprint, on the stated ground that the test written in step 3 is what will carry the
evidence forward.

**The one objection raised, and taken.** With the bug present, `updated_at` is a *copy* of the old
value, so the probe was guaranteed to show equality whatever the clock does — the script therefore could
not settle the granularity question as a by-product. It was extended to sample `get_current_time()` five
times directly and measure resolution on its own.

**What came back.** The bug reproduced on the first run: a `POST` then a `PUT` that genuinely changed
`content` returned **byte-identical `created_at` and `updated_at`**.

```
POST  created_at 2026-09-20T10:29:19.445615   updated_at 2026-09-20T10:29:19.445630
PUT   created_at 2026-09-20T10:29:19.445615   updated_at 2026-09-20T10:29:19.445630
content actually changed : True
```

Three facts for the test design, none of them guessable from the read alone:

1. **Timestamps serialise as ISO-8601 strings**, not `datetime` objects — `"2026-09-20T10:29:19.445615"`,
   naive, no offset, as `models.py:13-14` implies.
2. **Clock resolution is about two microseconds** — five back-to-back `utcnow()` calls were all
   distinct. So no `sleep` is needed and a strict comparison will not be flaky on this machine.
3. **The obvious assertion is a trap.** `created_at` and `updated_at` are *already different at
   creation* (`...445615` vs `...445630`) because `models.py:34-35` runs two separate `default_factory`
   calls. An assertion of the form `updated_at > created_at` therefore **passes with the bug present**
   and proves nothing. The test has to compare `updated_at` before the `PUT` against `updated_at`
   after it.

**Why my next prompt changed:** the observation is complete and the failure mode of the naive assertion
is known. The next prompt writes the test.

---

## Entry 49 — Step 3: the owed test written, and failing for the right reason

**Task:** 1.4, step 3.

**Prompt sent:**

> Lets go for the second row as I dont want to modify any of the provided tests

**Why this prompt matters (C1.3 — added a constraint).** It rules out editing the provided suite at all,
which is the stricter reading of C1.4's "all provided tests green": a green provided test that was
edited to become green proves less than one left alone. The new test therefore stands entirely on its
own.

**Context for the choice, found while reading the file.** The provided `test_update_prompt` is a
half-written version of this test — it captures `original_updated_at` (`test_api.py:89`), sleeps 0.1 s
"to ensure timestamp would change" (`:98-99`), and then leaves the assertion **commented out** at
`:108` with the note *"Uncomment after fix"*. The constraint means that line stays commented and the
assertion is made in a test of my own instead.

**What was written.** `tests/test_api.py` — `TestPrompts::test_update_prompt_refreshes_updated_at`,
inserted before `test_sorting_order`, plus a `from datetime import datetime` import at the top. It
creates a prompt, parses both timestamps out of the JSON with `fromisoformat`, issues the `PUT`, and
asserts:

- `updated_at` after the `PUT` is **strictly greater** than `updated_at` before it;
- `created_at` is **unchanged** — the fix must touch one field, not both.

Two decisions recorded in its docstring: the comparison is before-versus-after rather than
`updated_at > created_at`, for the reason established in entry 48; and **no `sleep`** is used, because
the clock was measured at microsecond resolution. The provided test's 0.1 s delay is left where it is.

**The result — red, for exactly the right reason.** Both earlier assertions (`200`, content changed)
passed, so the failure is isolated to the timestamp:

```
>       assert datetime.fromisoformat(data["updated_at"]) > original_updated_at
E       AssertionError: assert datetime.datetime(2026, 9, 20, 10, 35, 14, 781003)
E                            > datetime.datetime(2026, 9, 20, 10, 35, 14, 781003)
```

This is the ambiguity described in entry 47 closed by construction: the red run reports two identical
datetimes, not a `KeyError`, not a type mismatch, not a tick collision.

**Why my next prompt changed:** the bug is now pinned by a failing test of my own. The next prompt makes
it green — one field at `api.py:106`.

---

## Entry 50 — Step 4: Bug #2 fixed, and the stale BUG comments removed with it

**Task:** 1.4, step 4.

**Prompt sent:**

> lets go for 2, as I do not think more test is needed (and it is not required)

**Why this prompt matters.** Two decisions in one line. It takes the angle that also tidies the source
comments, and it declines the third angle on the explicit ground that the brief does not ask for it —
the same discipline applied in Task 1.3, where an invented test obligation had to be corrected out of
`CLAUDE.md`.

**What changed — `backend/app/api.py`, two edits, one logical change:**

1. `api.py:106` — `updated_at=existing.updated_at` became `updated_at=get_current_time()`. No new import
   was needed; `get_current_time` is already in the model import block at `api.py:11`.
2. `api.py:96-97` — the `# BUG #2: We're not updating the updated_at timestamp!` header and the inline
   `# BUG: Should be get_current_time()` were replaced by a comment describing what the block now
   actually does: a full replacement, `created_at` carried over, `updated_at` refreshed. A comment
   announcing a bug that is no longer there is a false statement about the code.

`created_at=existing.created_at` at `api.py:104` was deliberately left alone — the fix is one field.

**Result: `13 passed / 1 failed`.** `test_update_prompt_refreshes_updated_at` is green. The single
remaining failure is `test_sorting_order` — Bug #3, Task 1.5 — exactly as it stood before this task
began. The ten tests that were passing at the Task 1.3 baseline are still passing, plus the Bug #1
recoveries, plus the new one.

**Why my next prompt changed:** Bug #2 is closed. The next prompt is the commit.

---

## Entry 51 — Task 1.4 committed

**Task:** 1.4, step 5 — the commit.

**Prompt sent:**

> yes

**What it approved.** The message proposed under Rule 6, unedited, and the single-commit split: the fix
and the test that verifies it are one logical change, travelling with the log shard and the `CLAUDE.md`
bookkeeping.

```
Fix Bug #2: refresh updated_at on PUT

Asserting updated_at > created_at would pass with the bug, since models.py:34-35
fills both from separate calls; the test compares before and after instead.
```

The body spends its two sentences on the reasoning that leaves no trace in the diff — why the obvious
assertion was rejected — rather than restating the one-line change, which the diff already shows.

**Why my next prompt changed:** Task 1.4 is closed. The next prompt opens Task 1.5, Bug #3.

---

## Entry 52 — Task 1.5 opened: Bug #3, sort order

**Task:** 1.5, step 1 — deciding where to look first.

**Prompt sent:**

> lets go for the next bug

**What came back.** Not the fix. Task 1.5 was opened under Rule 0b and step 1 was framed as a choice
of *evidence source* before any code is changed: the helper (`utils.py`), the failing provided test
(`test_sorting_order`), or the observed pytest output. The brief's wording for Bug #3 is "fix the
order, **verify**" — a provided test already covers it, so no new test is owed, and the only open
question is what to read first.

**Why my next prompt changed:** the task is open but no evidence has been gathered yet; the next
prompt picks the starting point.

---

## Entry 53 — Task 1.5 step 1: the contract `test_sorting_order` actually imposes

**Task:** 1.5, step 1 — reading the failing provided test before touching the helper.

**Prompt sent:**

> lets go for B

**What came back.** `tests/test_api.py:146-165`, read in full. Four facts, all of which constrain the
fix:

1. **The request carries no query parameters** — `client.get("/prompts")` at `:161`. The fix therefore
   has to land on the endpoint's *defaults*; making `descending=true` work only when a client asks for
   it explicitly would leave this test red.
2. **"Newest" is defined by creation order, not by a named field.** The test creates `First`, sleeps
   0.1 s, creates `Second`, and asserts `prompts[0]["title"] == "Second"` (`:165`). It never names
   `created_at` or any `sort_by` value.
3. **One assertion, position 0 only.** `prompts[1]` is not checked, nor `total`, nor the order of any
   third item. The bar is low and precise.
4. **The 0.1 s sleep at `:158` means the test does not depend on clock resolution** — unlike the
   timestamp question settled in Task 1.4, there is nothing to measure here.

The docstring at `:147-150` states the intent in the brief's own words — "prompts are sorted newest
first" — and flags the bug.

**Why my next prompt changed:** the contract is now fixed and it is narrower than expected: the
defaults are load-bearing. That makes the endpoint's declared default parameter values the next thing
to check, not the helper body.

---

## Entry 54 — Task 1.5 step 2: there are no sort query parameters at all

**Task:** 1.5, step 2 — checking what `GET /prompts` defaults to, since the test sends no parameters.

**Prompt sent:**

> lets go with A

**What came back.** `api.py:42-61`. The step was framed around "the declared default values of the
`sort_by` and `descending` query parameters" — **and that framing was wrong**. `list_prompts` declares
exactly two parameters, `collection_id` and `search` (`api.py:44-45`). Sorting is not part of the
endpoint's public surface at all: `descending=True` is a **literal at the call site**
(`api.py:60`), not a client-controllable default.

Consequences for the fix:

- The worry the step existed to rule out — "fix the helper, and the test is still red because the
  default is ascending" — **cannot occur**. There is no default to get wrong.
- Every caller of the listing endpoint gets `descending=True`, unconditionally. So the helper only has
  to honour the argument it is handed; no new parameter, no signature change on the route.
- `api.py:58` already carries the comment `# Sort by date (newest first)` and `:59` the hint
  `# Note: There might be an issue with the sorting...`. The call site states the correct intent — it
  is the helper that does not deliver it. This confirms, from the other side, what was established in
  stage 3.

**Why my next prompt changed:** the last thing that could have made this a two-file fix is ruled out.
The fix is confined to `utils.py`, and the next prompt reads the helper body.

---

## Entry 55 — Task 1.5 step 3: one caller, and the helper body

**Task:** 1.5, step 3 — proving the helper has no other caller before changing it, then reading it.

**Prompt sent:**

> lets go with B

**What came back.** `grep -rn "sort_prompts_by_date" --include=*.py .` returns **three lines and no
more**: the definition (`utils.py:7`), the import (`api.py:14`), and the single call (`api.py:60`).
Nothing in `tests/` calls it directly — the provided test goes through the HTTP route. So the helper
has exactly one caller, and changing its behaviour cannot silently flip the order anywhere else. That
satisfies the C1.4 condition "nothing previously working broken" by construction rather than by
hoping.

The body, `utils.py:7-14`:

```python
def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by creation date.

    Note: There might be a bug here. Check the sort order!
    """
    # BUG #3: This sorts ascending (oldest first) when it should sort descending (newest first)
    # The 'descending' parameter is ignored!
    return sorted(prompts, key=lambda p: p.created_at)
```

Three things worth naming:

1. **The signature already defaults to `descending: bool = True`** — so the declared contract has
   always been newest-first. The parameter is accepted, documented by its own name, and then dropped.
2. **The sort key is `created_at`, not `updated_at`.** That matches what the test means by "newest"
   (creation order, entry 53) and it is the field Task 1.4 deliberately left untouched.
3. `sorted` is stable and returns a new list — the helper does not mutate its argument, which is
   consistent with the uncopied-objects hazard recorded in stage 3 but does not worsen it.

**Why my next prompt changed:** the defect is now fully specified — one expression, one file, one
caller. The next prompt is the fix itself.

---

## Entry 56 — Task 1.5 step 4: the fix, and a fully green suite

**Task:** 1.5, step 4 — making `descending` load-bearing.

**Prompt sent:**

> Lets go for A

**What was changed.** One file, `backend/app/utils.py`, one expression:

```python
return sorted(prompts, key=lambda p: p.created_at, reverse=descending)
```

`reverse=descending` was chosen over the alternative that also passes the test, `reverse=True`.
Hard-coding `True` would have made `test_sorting_order` green while leaving the parameter as dead as
it was — the signature would still promise something the body does not honour. Rule 5 calls that a bug
still present, not a bug fixed. The three-line docstring-plus-comment block announcing the defect
(`# BUG #3: ...`, `# The 'descending' parameter is ignored!`, and the docstring's "Check the sort
order!") was replaced by a single line describing what the function now does; a comment advertising a
bug that is gone is a false statement about the code. The full Google-style docstring is owed to
Task 1.9, not written here.

Nothing in `api.py` was touched. The call site was already correct (entry 54).

**Result: `14 passed`, nothing failing.** This is the first fully green run of the project — the
baseline was 3 failed / 10 passed (Task 1.3), then 12 passed / 1 failed, then 13 passed / 1 failed,
and the one remaining failure was this bug. `test_delete_collection_with_prompts` is still green,
because Bug #4 is not fixed yet and that test asserts the current orphaning behaviour — the trap
recorded for Task 1.6 is unchanged.

**Why my next prompt changed:** the fix is verified by the provided test, which is exactly what the
brief asks for Bug #3 ("fix the order, verify"). The next prompt is the commit.

---

## Entry 57 — Task 1.5 committed

**Task:** 1.5, step 5 — the commit.

**Prompt sent:**

> yes

**What it approved.** The message proposed under Rule 6, unedited, and the single-commit split: the
one-expression fix travels with the log shard and the `CLAUDE.md` bookkeeping, because no new test was
written for this bug — the provided one already covers it.

```
Fix Bug #3: sort prompts newest first

reverse=True would also pass test_sorting_order but leaves the declared descending
parameter dead at utils.py:7; reverse=descending makes the signature honest.
```

The body names the rejected alternative rather than the change itself, which is the one piece of
reasoning the diff cannot show.

**Why my next prompt changed:** Task 1.5 is closed and the suite is fully green. The next prompt opens
Task 1.6, Bug #4 — where the strategy decision and the trap at `tests/test_api.py:154-179` have to be
settled together.

---

## Entry 58 — Task 1.6 opened: Bug #4, orphaned prompts

**Task:** 1.6, step 1 — deciding what settles the strategy.

**Prompt sent:**

> lets go with task 1.6

**What came back.** Not a strategy. Task 1.6 was opened under Rule 0b, and step 1 was framed around
the one thing that makes this bug unlike the previous three: it has **no single obviously-correct
fix**. Cascade-delete the prompts, null their `collection_id`, or refuse to delete a non-empty
collection are all defensible, and the choice is a design decision that has to be defended in the
Module 5 oral. Three candidates were offered for what should settle it first — the brief's own
wording, the provided test that currently asserts the buggy behaviour, or the handler itself.

**Why my next prompt changed:** the strategy cannot be chosen until it is known whether the brief
already names one; the next prompt picks the evidence source.

---

## Entry 59 — Task 1.6 step 1: the brief confirms the choice is mine, and adds an obligation

**Task:** 1.6, step 1 — checking whether the brief already names a strategy.

**Prompt sent:**

> lets go with A, but my understanding it is that its an open choice.

**Constraint added (C1.3).** The prompt does not just pick an option — it states my own reading and
asks for it to be checked. That is a different request from "read the brief": it makes the step a
verification of a claim I am making, so a disagreement has to surface rather than being smoothed over.

**What came back.** My reading is correct, and the brief is explicit about it. `brief.txt:64-67`:

> Bug #4 — collection deletion orphans prompts
> Deleting a collection leaves its prompts with an invalid collection_id. Decide on a strategy — delete
> the prompts, null the field, or prevent deletion — implement it, and add a test. Record your
> reasoning in a line or two: you may be asked about this choice in your Module 5 defense.

Three things the wording settles:

1. **The choice is genuinely open** — the brief names all three options and delegates the decision. The
   three candidates carried in `CLAUDE.md` under *Open decisions* are exactly the brief's own three,
   in the brief's own order.
2. **There is a written obligation beyond the code** — "Record your reasoning in a line or two." That
   is a deliverable, not a chat answer, and it has to survive to the Module 5 defence.
3. **The rubric is outcome-agnostic.** The C1.4 evidence line says only "orphaned prompts **handled**"
   (`brief.txt:183`), never which way — so no strategy is graded higher than another, and the grade
   rests on the reasoning and the test, not on the pick.

**Noted for a later task, not acted on:** `brief.txt:84` proposes collection-deletion as the
deliberate probe for the AI-verification note — "Ask it to explain the collection-deletion behaviour
or to justify a fix, then check the answer against the code." That belongs to Task 1.8 (C1.5) and is
recorded in `CLAUDE.md` rather than pursued here, per Rule 0.

**Why my next prompt changed:** the decision is confirmed mine to make, so the next step is to find
what narrows it — the provided test at `tests/test_api.py:154-179`, which currently asserts the buggy
behaviour.

---

## Entry 60 — Task 1.6 step 2A: the guard `if prompts:` decides which strategies survive

**Task:** 1.6, step 2, angle A — reading the provided test that asserts the current buggy behaviour.

**Prompt sent:**

> We will go thorugh all of them. Start with A.

**Restructured (C1.3).** Three angles were offered as alternatives; the prompt converted them into a
**sequence** — test, then implementation cost, then semantics — and set the starting point. Same shape
as the restructuring in Task 1.4 (entry 47): refusing a forced choice between complementary evidence
sources, while still keeping one step per reply.

**Line numbers corrected.** `CLAUDE.md` recorded this test at `tests/test_api.py:154-179`. That is
**stale** — the new test added in Task 1.4 pushed the file down by 36 lines. It now lives at
`tests/test_api.py:190-215`, and the file is 215 lines long. Corrected in `CLAUDE.md`.

**What came back.** The decisive detail is the **guard**, not the assertion:

```python
prompts = client.get("/prompts").json()["prompts"]     # :211
if prompts:                                             # :212
    # Prompt exists with orphaned collection_id
    assert prompts[0]["collection_id"] == collection_id # :214
    # After fix, collection_id should be None or prompt should be deleted
```

Running each candidate strategy through it:

| Strategy | What `GET /prompts` returns afterwards | `if prompts:` | Result |
|---|---|---|---|
| **Cascade-delete the prompts** | empty list | falsy — body **skipped** | **passes** |
| **Null the `collection_id`** | one prompt, `collection_id is None` | truthy — body runs, `None != collection_id` | **fails** |
| **Prevent deletion of a non-empty collection** | one prompt, id intact | truthy — body runs, ids match | **passes** |

So the test does **not** eliminate cascade, which was the expectation going in — the `if prompts:`
guard was written precisely so that a cascade fix would not break it. What it eliminates is
**nulling the field**, the one option whose own name appears in the test's closing comment at `:215`.

**The conflict this exposes.** The docstring at `:193-195` says "After fixing, update the test to
verify correct behavior" — the test invites its own modification. That collides head-on with the
standing constraint set in Task 1.4: **no provided test may be modified.** Under that constraint the
strategy space is cascade or prevent. If the constraint is relaxed for this one test, on the test's own
written invitation, all three are back open. That is a decision for the user, not an inference for me,
and it is put to them rather than resolved here.

**Why my next prompt changed:** the constraint is now precise, and one strategy is conditionally dead.
The next step is B — what each surviving strategy costs to build — as the sequence set out.

---

## Entry 61 — Task 1.6 step 2B: what each strategy costs to build

**Task:** 1.6, step 2, angle B — the handler plus the storage primitives, to price the three options.

**Prompt sent:**

> B

**The handler**, `api.py:143-156`:

```python
@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    # BUG #4 ... Should either: delete the prompts, set collection_id to None, or prevent deletion
    if not storage.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    # Missing: Handle prompts that belong to this collection!
    return None
```

**The primitives that exist** in `storage.py`: `get_prompts_by_collection` (`:58-59`, called by
nothing), `delete_prompt` (`:34-38`), `update_prompt` (`:27-31`). Every strategy is buildable from
what is already there — **no new storage method is needed by any of the three.** Cost is therefore not
a tie-breaker on its own, and the differences are structural rather than in line count.

| Strategy | Sketch | Structural notes |
|---|---|---|
| **Cascade-delete** | `for p in storage.get_prompts_by_collection(id): storage.delete_prompt(p.id)` | Finally gives `get_prompts_by_collection` its first caller. Order is irrelevant — the two dicts are structurally independent (stage 5), so the prompts remain findable after the collection is gone. Iterating a fresh list while deleting from `_prompts` is safe because `get_prompts_by_collection` already materialises a new list. |
| **Null the field** | fetch, set `collection_id = None`, `storage.update_prompt(...)` | `update_prompt` re-binds the same object into the same key, so it is nearly a no-op — storage hands out **uncopied** objects (stage 3), meaning a plain in-place mutation would also "work". Going through `update_prompt` anyway keeps the write visible instead of relying on the aliasing hazard. Killed by the provided test (entry 60) unless that test is modified. |
| **Prevent deletion** | `if storage.get_prompts_by_collection(id): raise HTTPException(409, ...)` | **The only one that forces the handler to be restructured.** The 404 check is currently *fused* with the delete at `:151` — `if not storage.delete_collection(...)` both tests existence and performs the deletion in one expression. A non-empty guard has to run **before** the delete, so existence must first be established separately via `storage.get_collection`, splitting one line into two. It also changes the route's public contract: a `204`-only endpoint gains a second, non-404 error status. |

**Why my next prompt changed:** cost does not separate the options — all three are three lines against
existing primitives. The differences that matter are semantic, which is exactly angle C, the last of
the three.

---

## Entry 62 — Task 1.6 step 2C: what the data model says about the relationship

**Task:** 1.6, step 2, angle C — framing the strategy argument from the repository's own declarations.

**Prompt sent:**

> I agree with A

**The declarations**, `models.py:19-58`:

```python
class PromptBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None            # :23

class Collection(CollectionBase):                  # :54-58
    id, name, description, created_at              # no prompt list, no back-reference
```

Five facts, each one evidence about whether membership is essential or incidental:

1. **`collection_id` is `Optional` with a default of `None`** (`:23`). A prompt with no collection is a
   fully valid prompt, not a degraded one. The model already has a first-class representation for
   "unfiled".
2. **It is the only client-supplied field with no `Field(...)` constraint** (contrast `:20-22`). Nothing
   is asserted about it — not a length, not a format, not that it refers to anything real.
3. **`title` and `content` are required and non-empty; `collection_id` is neither.** The model's own
   ranking of what a prompt *is* puts the collection link last.
4. **`Collection` has no back-reference** (`:54-58`). It does not own or enumerate its prompts. The link
   is declared once, on the child, pointing up.
5. **`PUT` already unfiles a prompt silently** when the body omits `collection_id` (`api.py:108`,
   exercised by `test_api.py:92-101`). Transitioning a prompt to "no collection" is **existing,
   tested, accepted behaviour** — not a new state this fix would invent.

What each fact implies, read against the three strategies:

| Strategy | The model-based case for it | The model-based case against it |
|---|---|---|
| **Cascade-delete** | Treats the collection as an owner; matches a user's folder intuition | Nothing in the model expresses ownership — `Collection` has no prompt list (fact 4), and `content` being required while `collection_id` is optional (fact 3) says the prompt is the valuable entity. Destroys data the model says stands alone |
| **Null the field** | Facts 1 and 5 make it the state the model already has a name for, and the one the API already reaches by another route | Blocked by the provided test unless that test is modified (entry 60) |
| **Prevent deletion** | Protects against surprise data loss | Facts 1 and 2 say the reference was never guaranteed to be valid; adding a new error status to a `204` endpoint asserts an integrity rule the model never declared |

The evidence is laid out; the choice is the user's and is deliberately not made here.

**Why my next prompt changed:** all three angles are gathered. The next prompt makes the decision —
including whether the no-modify-provided-tests constraint holds for `test_api.py:190-215`.

---

## Entry 63 — Task 1.6 step 3: strategy chosen, and the test-modification question

**Task:** 1.6, step 3 — the decision.

**Prompt sent:**

> I think Null the field is the better compromise, but I dont know if we should modify a test asi it
> is a grading tool

**Decision recorded: null the `collection_id`.** Reached from the data model (entry 62) and from the
user-facing comparison: it is the only strategy that destroys no data and imposes no new workflow
burden, and `Optional[str] = None` (`models.py:23`) is a state the model already declares and `PUT`
already produces (`api.py:108`).

**The second half of the prompt is the real question**, and it is the right one to have asked — the
provided test suite *is* the C1.4 grading instrument, so editing it looks like editing the ruler.
What the brief actually says, checked rather than assumed:

- `brief.txt:53` — "all provided tests must pass"
- `brief.txt:109` — "All provided tests passing"
- `brief.txt:186` — "All provided tests pass and nothing that worked before is broken"

Every one of these requires the suite to be **green**. **None of them says the test files are
immutable.** And the test in question carries written instructions to the contrary in its own
docstring (`tests/test_api.py:193-195`):

> NOTE: Bug #4 - prompts become orphaned after collection deletion.
> This test documents the current (buggy) behavior.
> **After fixing, update the test to verify correct behavior.**

So updating it is **following** the provided material, not circumventing it. The opposite reading
creates a contradiction: a test whose own docstring says it "documents the current (buggy) behavior",
still green in a repository that claims the bug is fixed, is a worse signal to a grader than a clean
one-line diff. It would mean the suite asserts the bug is still present.

The standing "no provided test may be modified" constraint from Task 1.4 is therefore **relaxed for
this one test only**, on that test's own written invitation, and the reasoning is recorded here and in
the commit body so the exception is visible rather than silent. `test_update_prompt`, the other test
with a commented-out assertion, stays untouched — its docstring contains no such instruction.

**Why my next prompt changed:** both halves of the decision are settled, so the next step is the
implementation — handler, test edit, and the "line or two" of recorded reasoning the brief requires.

---

## Entry 64 — Task 1.6 step 4: implemented, with the reasoning on the handler

**Task:** 1.6, step 4 — the implementation.

**Prompt sent:**

> Lets go for C

**Where the reasoning lives.** On `delete_collection` itself (`api.py:145-158`), as a docstring. The
brief's "record your reasoning in a line or two" (`brief.txt:66`) is satisfied by an artefact that
sits on the code it justifies and is found by whoever next reads the handler — not by a `git log`
entry. Task 1.9 will complete it with Args/Returns/Raises; the strategy paragraph is written now,
while the argument is fresh, because that is the part that cannot be reconstructed later.

**Three changes.**

1. **`api.py`** — the three `BUG #4` comments and the `# Missing: Handle prompts...` marker removed,
   the strategy docstring added, and the fix itself:

   ```python
   for prompt in storage.get_prompts_by_collection(collection_id):
       storage.update_prompt(
           prompt.id, prompt.model_copy(update={"collection_id": None})
       )
   ```

   `model_copy` rather than mutating `prompt.collection_id` in place. Storage hands out **uncopied**
   objects (stage 3), so in-place mutation would also appear to work — by writing through an alias,
   silently, without the store being told. Going through `update_prompt` with a fresh object keeps the
   write explicit and does not deepen the aliasing hazard. `updated_at` is deliberately **not** bumped:
   unfiling is a consequence of deleting the collection, not a client edit of the prompt.

   The loop runs **after** the 404 guard. It has to: the existence check and the deletion are fused
   into one expression at `:159` (entry 61), and the two dicts are independent, so the prompts are
   still findable once the collection is gone.

2. **`tests/test_api.py:190-214`** — the provided test, updated on its own written instruction. The
   docstring now states what it verifies and why, and the tail became:

   ```python
   prompts = client.get("/prompts").json()["prompts"]
   assert len(prompts) == 1
   assert prompts[0]["id"] == prompt_id
   assert prompts[0]["collection_id"] is None
   ```

   The `if prompts:` guard was **removed rather than kept**. Retaining it would have let the test pass
   silently if the prompt were wrongly deleted — the exact hole that made the original test tolerate a
   cascade (entry 60). Survival of the prompt is now the first thing asserted. Name, fixtures and
   setup are unchanged.

3. **A new test**, `test_delete_collection_leaves_no_dangling_reference` — the one the brief demands
   explicitly. It covers what the updated provided test does not: the unfiled prompt is still
   individually retrievable with `title` and `content` intact, filtering by the dead id now returns
   `[]` with `total == 0`, and the collection itself is 404.

**Verified red first.** With the loop removed, both collection-deletion tests fail, each on
`AssertionError: assert '<uuid>' is None` — the right reason, not a `KeyError` or a shape mismatch.
With the loop restored: **15 passed**, nothing failing.

**Why my next prompt changed:** Bug #4 is closed and the suite is green. The next prompt is the commit.

---

## Entry 65 — Task 1.6: full verbose run before committing

**Task:** 1.6, step 5 — confirming the suite before the commit rather than after.

**Prompt sent:**

> Lets run all the test to check if they are all green (run pytest test/ -v) inside the backend folder

**Constraint added (C1.3).** The commit was already proposed and awaiting approval; this prompt
inserted a verification gate ahead of it and named the exact command and directory — the same
`cd backend && pytest tests/ -v` that `CLAUDE.md` records as the project's verification command and
that C1.4 is graded on. Running the graded command verbatim, rather than the `-q` form used while
iterating, is the difference between "my tests pass" and "the graded command passes".

**What came back.** `15 passed`, every test named:

| | Test | Origin |
|---|---|---|
| 1 | `TestHealth::test_health_check` | provided |
| 2–7 | `test_create_prompt`, `test_list_prompts_empty`, `test_list_prompts_with_data`, `test_get_prompt_success`, `test_get_prompt_not_found`, `test_delete_prompt` | provided |
| 8 | `test_update_prompt` | provided — untouched, commented assertion still commented |
| 9 | `test_update_prompt_refreshes_updated_at` | **added in Task 1.4** |
| 10 | `test_sorting_order` | provided — green since Task 1.5 |
| 11–13 | `test_create_collection`, `test_list_collections`, `test_get_collection_not_found` | provided |
| 14 | `test_delete_collection_with_prompts` | provided — **updated in Task 1.6** |
| 15 | `test_delete_collection_leaves_no_dangling_reference` | **added in Task 1.6** |

Thirteen provided tests, all green; two added. Against the Task 1.3 baseline of 3 failed / 10 passed,
every previously-passing test is still passing — the second half of the C1.4 condition, "nothing that
worked before is broken".

The 30 warnings are all pre-existing and unrelated to any fix: Pydantic V1-style `class Config`
(`models.py:34,54`) and `datetime.utcnow()` deprecation (`models.py:14`). Not touched — out of scope
for the bug tasks, and no task in the brief asks for them.

**Why my next prompt changed:** nothing left to verify. The next prompt is the commit.

---

## Entry 66 — Task 1.6 committed

**Task:** 1.6, step 6 — the commit.

**Prompt sent:**

> go ahead

**What it approved.** The message proposed under Rule 6, unedited, and the single-commit split: the
handler fix, the updated provided test and the new test are one logical change — the strategy is not
implemented until all three exist.

```
Fix Bug #4: unfile prompts on collection delete

Nulling collection_id fits a model where membership is optional and unconstrained
while title and content are required; the provided test's docstring asked for this update.
```

The body spends one sentence on the strategy argument and one on the modification of a provided test
— the two decisions an assessor is most likely to question, and neither visible in the diff.

**Why my next prompt changed:** all four bugs are fixed and the suite is green. The next prompt opens
Task 1.7, the missing `PATCH /prompts/{id}` endpoint — the last item of the C1.4 MUST PASS row.

---

## Entry 67 — Task 1.7 opened: the missing PATCH endpoint

**Prompt sent:**

> Lets go for task 1.7

**What came back.** No implementation — the reply opened step 1 of the task and stopped. It read the
brief's four checkboxes for the endpoint (`brief.txt:69-73`: partial updates, `updated_at` refreshed,
404 on a missing prompt, follow existing patterns) and the two things already in the repo that the
endpoint has to be built against: the `PUT` handler at `api.py:85-109`, which is a full rebuild, and
`PromptUpdate` at `models.py:31-32`, which is `PromptBase` unchanged and therefore has `title` and
`content` required.

The step it put to me is the request model — how the endpoint tells "field omitted" apart from "field
set to null" — with three angles: a new all-`Optional` `PromptPatch` model read through
`exclude_unset`; reusing `PromptUpdate` as-is; or taking a raw `dict` body and merging by hand.

It also flagged, outside the task, that this shard contains literal `—` text instead of em dashes
from an earlier session's escaping.

**Why my next prompt changed:** n/a — this is the opening prompt of the task.

---

## Entry 68 — Task 1.7 step 1, clarified: the three angles as concrete requests

**Prompt sent:**

> what you mean in B with " but collection_id: None becomes unexpressible — you could never unfile a
> prompt via PATCH, and title/content are still required, failing the checkbox outright. Use an example
> if needed for each trade-off

**What came back.** The same three angles, re-expressed as actual request bodies against a stored
prompt, rather than as prose about model shapes.

The core of it: with **B** (reuse `PromptUpdate`), `PATCH {"description": "new"}` never reaches the
handler at all — `title` and `content` are required on `PromptBase` (`models.py:20-21`), so FastAPI
returns 422 during validation. And a handler written as "skip fields that are `None`" cannot tell
`{"collection_id": null}` — meaning *take this prompt out of its collection* — from a body that simply
omitted the key, because both arrive as `None` on the model. Both are read as "leave it alone", so
unfiling is unreachable. This matters because `PUT` **can** unfile (`api.py:108`, exercised by
`test_api.py:92-101`), so B would make PATCH strictly weaker than the endpoint it supplements.

**A** fixes exactly that by not using `None` as the signal: all fields `Optional`, and *presence* is
read from `model_dump(exclude_unset=True)`, which reports which keys the client actually sent.
**C** (raw `dict`) has the same correct presence semantics but loses `min_length=1`, so
`PATCH {"title": ""}` would be stored where `POST`/`PUT` would have rejected it with a 422.

**Why my next prompt changed:** this narrowed the question — the trade-off is not three-way. B fails a
brief checkbox outright and C drops validation the rest of the API enforces, so the next prompt can
settle A's remaining detail (whether the optional fields keep their `Field` constraints) instead of
re-opening the choice. **C1.3: this iteration added a constraint** — it asked for the comparison to be
grounded in concrete request bodies rather than model descriptions.

---

## Entry 69 — Task 1.7 step 1: can the handler fetch the missing fields instead?

**Prompt sent:**

> For A, couldnt we retrieve from the id the title and the content? Using prompt search function or
> simillar?

**What came back.** Yes — and the answer separated two layers I had been treating as one. Fetching the
stored prompt by id is exactly the second half of angle A: `storage.get_prompt(prompt_id)`, the same
call `PUT` already makes at `api.py:87`, supplies every field the client did not send. That is the
merge.

What it cannot do is rescue angle B, because of a property established back in stage 3: **validation is
entirely pre-handler**. FastAPI builds and validates the body model before the handler function is
entered, so with `PromptUpdate` a body missing `title` is a 422 while `prompt_id` is still just a string
in the URL — no lookup has happened and none can. The model must stop *demanding* the field; only then
does the handler get the chance to *supply* it from storage.

So the division is: the model says which fields the client is allowed to omit, and storage says what
those omitted fields are worth. The handler is where they meet.

Also confirmed which function: `storage.get_prompt(prompt_id)` (`storage.py:21-23`), not the search
helper in `utils.py` — search filters a list of prompts by text, it does not fetch one by id.

**Why my next prompt changed:** the question is now settled in favour of A and the merge mechanism is
clear, so the next prompt can close step 1 on the one detail left open — whether `PromptPatch`
re-declares the `Field` constraints — and move to writing the handler.

---

## Entry 70 — Task 1.7 step 1 closed: `PromptPatch` written

**Prompt sent:**

> then I understand you decided to go for angle A, in that case I agree

**What came back.** Angle A confirmed and written: a new `PromptPatch` in `app/models.py:34-49`, a
plain `BaseModel` rather than a subclass of `PromptBase` — subclassing would inherit the required
`title` and `content`, which is the whole thing being avoided.

The one detail left open at the end of the last step, whether the optional fields re-declare their
constraints, was taken as the consistency option and flagged as reversible: `title` keeps
`min_length=1, max_length=200`, `content` keeps `min_length=1`, `description` keeps `max_length=500`.
The alternative — bare `Optional[str] = None` — would have left a hole only `PATCH` has, where
`{"title": ""}` succeeds while the same body is a 422 on `POST` and `PUT`.

A class docstring on the model records why presence is read through `exclude_unset` rather than by
testing for `None`, so the omitted-versus-explicit-null distinction is documented where the model is
defined rather than only in this log.

**Why my next prompt changed:** the request model is settled, so the next prompt moves to the handler
— specifically how it merges the sent fields onto the stored prompt, which is where the
`model_copy`-versus-rebuild choice from Task 1.6 comes back.

---

## Entry 71 — Task 1.7 step 2: the handler written, angle B

**Prompt sent:**

> Lets go for B. Regarding: 1- do not update un this case. 2-ok

**What came back.** `patch_prompt` written at `api.py:112-145`, plus `PromptPatch` added to the import
at `api.py:8`. The explicit rebuild, mirroring the shape of `PUT` at `api.py:96-105` rather than
collapsing into a `model_copy` call, so the two write routes read alike.

The three decisions, as they landed in code:

- **Merge** — `changes = prompt_data.model_dump(exclude_unset=True)`, then each field is
  `changes.get("field", existing.field)`. A key the client did not send falls through to the stored
  value; a key sent as `null` is present in `changes` and therefore wins, which is what makes unfiling
  reachable.
- **Empty body** — `updated_at=get_current_time() if changes else existing.updated_at`. My call: no
  fields sent is not an edit, so the timestamp does not move.
- **Collection validation** — `if changes.get("collection_id") is not None:`. One condition covers both
  cases, since a key that was never sent and a key sent as null both fail it; the first must not be
  validated because nothing was asked for, the second because `null` means unfile and there is no
  collection to look up. A 400 is raised for an unknown id, the same status and detail `PUT` uses at
  `api.py:99-100`.

The 404 guard is first, before the body is touched, as in every other handler that addresses a prompt
by id. A docstring on the handler records the `exclude_unset` reasoning and the empty-body rule;
Args/Returns/Raises are owed to Task 1.9 along with the earlier functions.

**Suite: 15 passed** — unchanged from the end of Task 1.6, so nothing that worked before is broken.

**Why my next prompt changed:** the endpoint exists and the provided tests still pass, but nothing yet
exercises `PATCH` itself — the four brief checkboxes are so far only claims. The next prompt is about
how to demonstrate them.

---

## Entry 72 — Task 1.7 step 3: two tests, the compromise option

**Prompt sent:**

> Lets go for B as its a compromise

**What came back.** Two tests appended to `TestPrompts` in `tests/test_api.py`, ahead of
`class TestCollections`, rather than a new file — appending leaves every provided test byte-identical,
so the no-modification constraint holds, and the `client` / `sample_prompt_data` fixtures are already
in scope. That was the open question I left unanswered in my prompt; it was taken as the
append-in-place option and flagged.

- `test_patch_prompt_partial_update` — creates a prompt, sends `{"description": "Revised description"}`
  and nothing else, then asserts the description changed, `title`, `content` and `id` did not,
  `created_at` is byte-identical, and `updated_at` moved. It closes with a `GET` so the change is shown
  to be stored rather than echoed back by the handler. No `sleep` is needed: `utcnow()` was measured at
  microsecond resolution back in Task 1.4.
- `test_patch_prompt_not_found` — `PATCH` against an unknown id is 404.

**Suite: 17 passed.**

What this angle consciously does not cover, which angle A would have: explicit-null unfiling, and the
empty body leaving `updated_at` alone. Both are behaviours I decided rather than inherited from the
brief, and both are now documented only in the handler docstring.

**Why my next prompt changed:** the endpoint is implemented and demonstrated, so the task is finished
and the next prompt is the commit.

---

## Entry 73 — Task 1.7 committed

**Prompt sent:**

> only one commit

**What it approved.** The message proposed under Rule 6, unedited, and a single commit rather than
splitting the model and handler from the tests — the endpoint is not implemented until something
demonstrates it.

```
Add PATCH /prompts/{id} for partial updates

Presence is read from exclude_unset, not from None, so an explicit null unfiles
a prompt while an omitted key leaves it alone; an empty body is not an edit.
```

Both sentences go on the decisions that leave no trace in the diff — the presence rule and the
empty-body rule — rather than on the explicit-rebuild style, which the diff shows plainly.

**This closes Tasks 1.3-1.7 and shard `02`.** All four bugs are fixed, `PATCH /prompts/{id}` exists,
and the suite is 17 passed, which is the whole of the C1.4 MUST PASS row.

**Why my next prompt changed:** the code work is done. The next prompt opens Task 1.8, the
AI-verification note, in a new shard `03-task-1.8.md` starting at entry 74 — and the brief has already
pre-chosen the probe if no organic mistake is to hand (`brief.txt:84`).

---

## Entry 74 — Task 1.8 opened; the candidate mistakes are counted before any is chosen

**Prompt:**

> go for task 1.8

**What came back:** no note written. Step 1 was framed as a *selection* problem rather than a writing
problem: Rule 4 says AI mistakes are captured live, and the log already carries several, so the first
question is which instance the note documents — not what to write about it.

The brief's own words for the task were re-read (`brief.txt:77-84`): "what the AI produced, why it was
wrong, how you detected it, and what you did instead", traceable to a prompt-log entry, and explicitly
**not** a syntax error an editor would flag. The last line of that section suggests a deliberate probe
(ask for the collection-deletion behaviour from memory, then check it) *if* no wrong answer was ever
hit — which is a fallback, not a requirement.

The log was then searched rather than recalled, and the candidates enumerated with their entry numbers:

| Candidate | Entry | What was wrong |
|---|---|---|
| The "only route" claim about `GET /prompts/{id}` | 16 | Stated as a property of routes; it is a property of return types. Flagged in-entry as a C1.5 candidate. |
| A second unverified "only", this time over fields | 25 | Same failure mode as 16, caught the same way — asserted over a set that had not been enumerated. |
| "Unreachable" as a description of a storage limitation | 33 | Overstated; the chain was traced instead of asserted and the word did not survive. |
| Moving the 404 into `storage.py` "would break `create_prompt`'s 400 path" | 43 | Wrong about the call sites. Flagged in-entry for C1.5. |
| "`list_prompts` declares `sort_by` and `descending` query parameters" | 54 | No such parameters exist; the framing invented a client-facing default. |

Two of these (16, 43) were already tagged for C1.5 when they happened, which is exactly the trace
C1.5 asks for.

**Why the next prompt changed:** the choice between them is mine, and it is a real trade-off — one
deeply worked instance versus a pair that shows the same failure mode recurring, versus running the
brief's suggested probe on top of the organic material. Recorded with the next prompt.

---

## Entry 75 — Three cases chosen; the four fields proposed from the log before any prose is written

**Prompts sent, in order:**

> Lets write in detail 43, 16 and 25. we should nswer what tha AI produced, why it was wrong, how I
> detect it and waht I did instead. Searching on the logs create a table with a propossal on every of
> this fields. We might have to compact the log files in order to fit them in context.

> Add to the 3 bugs the reference where they can be found. Then, write them by chronological order and
> do the clossing section adding also the other bugs in one line

**What came back.** The organic material was chosen over the brief's fallback probe — five wrong
outputs had already been caught and recorded live, so manufacturing a sixth would have been the weaker
evidence. Three were selected: **43, 16, 25**.

*Compaction turned out not to be needed.* The three entries were read by line range
(`sed -n '390,440p'`, `'804,860p'`, `'95,152p'`) rather than by loading the shards whole — about 130
lines in total against roughly 1,600 in the two files. That is the same discipline the sharding exists
for, applied one level finer.

**One table per case** was returned before any prose, each with the four fields the brief names, drawn
from the log rather than from memory:

| Case | What the AI produced | Why it was wrong |
|---|---|---|
| 16 | "`GET /prompts/{prompt_id}` is the **only** route that doesn't test the storage result for falsiness" | `list_prompts` doesn't test it either (`api.py:48,52,56,60`); and the property belongs to return types, not routes |
| 25 | "`collection_id` is the **only** field in the whole schema with no `Field(...)` constraint" | `PromptList`, `CollectionList`, `HealthResponse` have none either (`models.py:64-76`); the set was never enumerated |
| 43 | Option C "would break `create_prompt`'s 400 path" | `create_prompt` calls `get_collection` (`api.py:81`), not `get_prompt`; `get_prompt`'s two callers both want 404 |

Detection and remedy per case were proposed alongside, and the through-line was offered as an optional
closing section rather than assumed.

**Two constraints I added on the second prompt**, which is what turned the proposal into the
deliverable:

1. **Each case must carry a reference to where it can be found** — entry number, the merged
   `docs/prompt-log.md`, and the working shard with line numbers. Without that, C1.5's "traceable to
   an entry in your prompt log" rests on the reader's willingness to search.
2. **Chronological order, not strongest-first** — 16, then 25, then 43. Strongest-first would have led
   with the decision-steering error, but it would have destroyed the fact that 25 is a *repeat* of 16.
   The sequence is itself a finding.

Plus the closing section, **with the two unwritten cases named in one line each** (entries 33 and 54),
so the note shows the full count of what was caught without inflating three write-ups into five.

`docs/ai-verification-note.md` written: three cases in chronological order, each with where-to-find-it,
the four fields, and a closing section naming the shared failure mode — *a claim about a set, asserted
without enumerating the set* — the three properties that make them worth documenting, and the one-line
mentions of entries 33 and 54.

**Why the next prompt changed:** the deliverable exists; what remains is the commit, which needs its
message approved.

---

## Entry 76 — Task 1.9 opened; the scope is counted before anything is written

**Prompt:**

> lets go for task 1.9

**What came back:** no docstring written. Step 1 was framed as a *scope* question, because C1.6's
failure modes are all scope or accuracy failures — "docstrings listing parameters that don't exist or
omitting ones that do" (`brief.txt:218-219`) — and the rubric's word is "**every** function you
modified or added" (`brief.txt:88`). Which functions those are is a fact about the diff, not a matter
of recollection, so the diff was read rather than remembered: `git diff` of the intake commit
(`1df4cbd`) against `HEAD`.

The inventory that came back:

| Function | File | Touched how |
|---|---|---|
| `get_prompt` | `api.py:66` | Modified — Bug #1, the `None` dereference replaced by a 404 guard |
| `update_prompt` | `api.py:86` | Modified — Bug #2, `updated_at=get_current_time()` |
| `sort_prompts_by_date` | `utils.py:7` | Modified — Bug #3, `reverse=descending` |
| `delete_collection` | `api.py:178` | Modified — Bug #4, the unfiling loop; already carries a strategy docstring |
| `patch_prompt` | `api.py:113` | **Added** — Task 1.7; already carries a behaviour docstring |
| 4 test functions | `tests/test_api.py` | **Added** — Tasks 1.4, 1.6, 1.7; each already has a prose docstring |
| `test_delete_collection_with_prompts` | `tests/test_api.py` | Modified — Task 1.6, on its own written instruction |
| `PromptPatch` | `models.py:34` | **Added** — a class, not a function; undocumented |

Also noted: the brief prints a worked example of the shape it wants (`brief.txt:92-103`) — one summary
line, then `Args:`, `Returns:`, `Raises:` — and that example's `Raises: ValueError` is for a
hypothetical `storage.get_prompt`, not for anything in this repository. Copying its *Raises* line would
be exactly the "listing what doesn't exist" failure.

Two of the five app functions already carry docstrings, written for a different purpose: `patch_prompt`
documents presence-vs-`None` semantics and `delete_collection` documents the orphan strategy, which is
where Task 1.6's "record your reasoning in a line or two" lives. Neither has `Args`/`Returns`/`Raises`.
So the question is not only *which* functions but *what happens to prose that is already there*.

**Why the next prompt changed:** the boundary is mine to draw — app functions only, or the test
functions and `PromptPatch` too — and so is the treatment of the two existing docstrings. Recorded with
the next prompt.

---

## Entry 77 — scope fixed at A, and the style guide is read instead of guessed

**Prompt:**

> go with A, regarding modiifying the existing summary body for delete_collection and patch prompt
> lets search what the Google-style docstrings standard say about this, before making any call.

**Why this prompt is an iteration (C1.3 — added a constraint):** the reply offered a choice between
keeping the existing prose as the body and compressing it, and I refused to pick from the options as
offered. The constraint added was *evidential*: no call on docstring layout until the actual Google
Python Style Guide says what layout is. C1.6 grades the docstrings against a named standard, so an
opinion about the standard is worth less than the standard.

**What came back:** scope set to the **five app functions** — `get_prompt`, `update_prompt`,
`sort_prompts_by_date`, `delete_collection`, `patch_prompt`. Test functions and `PromptPatch` are out.

Then the style guide itself (`google.github.io/styleguide/pyguide.html`), fetched rather than recalled:

| Rule | Where | Verbatim |
|---|---|---|
| Summary line | §3.8.1 | "organized as a summary line (one physical line not exceeding 80 characters) terminated by a period, question mark, or exclamation point" |
| Extended description | §3.8.1 | "When writing more (encouraged), this must be followed by a blank line, followed by the rest of the docstring starting at the same cursor position as the first quote of the first line." |
| Section headings | §3.8.3 | "Certain aspects of a function should be documented in special sections... Each section begins with a heading line, which ends with a colon." |
| Style consistency | §3.8.3 | "may be descriptive-style... or imperative-style... but the style should be consistent within a file" |
| What to describe | §3.8.3 | "the docstring should describe the function's calling syntax and its semantics, but generally not its implementation details" |

The canonical `fetch_smalltable_rows` example confirms the order: summary, blank line, prose
paragraph, `Args:`, `Returns:`, `Raises:` — and **nothing after `Raises:`**.

So the layout question is answered by the guide, not by preference: extended prose sits **between the
summary line and `Args:`**, never below the sections. Both existing paragraphs keep their position;
the sections are appended beneath them.

Two things the guide settles that were not asked:

- **Imperative, not descriptive.** `api.py` already reads "Partially update a prompt." and "Delete a
  collection and unfile…"; `utils.py` reads "Sort prompts…", "Check if…", "Extract…". Both files are
  already consistently imperative, so the three new summaries must be imperative too. The brief's own
  example ("Retrieve a prompt…") happens to agree.
- **One genuine tension.** "Semantics, not implementation details" cuts against `delete_collection`,
  whose paragraph is a *decision record* citing `models.py:23,54-58` — and that paragraph is where
  `brief.txt:66` ("record your reasoning in a line or two") is satisfied. The guide would not put it
  there; the brief put it there.

**Why the next prompt changed:** the `delete_collection` tension is the only thing the standard does
not resolve, so it is the one call left to make before writing. Recorded with the next prompt.

---

## Entry 78 — the cost of option A is challenged rather than accepted

**Prompt:**

> I dont understand the cost of A

**What came back:** the cost was restated concretely instead of abstractly — the ~22-line docstring
was rendered as a reader would meet it in an IDE hover or `help()`, with the useful summary on line 1
and eleven lines of design argument between it and `Args:`. Two specific consequences were named:
the API contract sits below the fold for anyone who only wants to know whether their prompts get
deleted, and the citations to other files by line number rot silently on any edit — which is the other
C1.6 failure mode, a docstring that no longer matches the code.

It was also said plainly that A's cost is **not** a grading cost: A passes C1.6, and the argument for A
is that the brief asked for the reasoning to be recorded and this is where it was recorded.

**Why the next prompt changed:** the answer exposed that one of the three options carried a cost of a
completely different kind, which I wanted named before choosing.

---

## Entry 79 — the odd one out among the options is isolated

**Prompt:**

> why C is the onky one that changes system_model state to finished?

**What came back:** because C is the only option that moves the text **out of the code**. A keeps it in
the docstring, B in a comment; both stay inside `api.py` and touch no other deliverable. C relocates it
into `SYSTEM_MODEL.md`, which is recorded as finished, is the evidence file for **C1.1/C1.2** rather
than for the Bug #4 decision, and under Rule 3 describes what the code does rather than what we chose
— there is no section in it that owns a design rationale.

Conclusion offered: C's cost is scope and bookkeeping, not prose quality, and it is arguably outside
Task 1.9 altogether. The real choice was narrowed to A versus B — published surface, or beside the code.

**Why the next prompt changed:** with C set aside the decision was a clean two-way one, and I took it.

---

## Entry 80 — option B, plus a constraint the options did not offer

**Prompt:**

> Lets go for B and avoid references to any line of code

**Why this prompt is an iteration (C1.3 — added a constraint):** "avoid references to any line of code"
was mine, not one of the three options. It removes the rot risk identified in entry 78 at its source:
prose that never names a line cannot go stale when a line moves.

**What came back:** all five docstrings written, and the constraint applied slightly wider than the
literal words — flagged at the time rather than done quietly:

| Function | What happened |
|---|---|
| `get_prompt` | New docstring. `Raises:` documents the 404 only. |
| `update_prompt` | New docstring. Records that an omitted field is reset rather than kept, so a body without a collection unfiles the prompt. The two comment lines above the rebuild were deleted, since the docstring now says the same thing. |
| `sort_prompts_by_date` | Summary line kept; `Args:`/`Returns:` appended. No `Raises:` — the guide permits omitting a section that does not apply, and inventing one would be the failure C1.6 names. |
| `patch_prompt` | Prose kept in place above `Args:`, but rewritten to drop `model_dump(exclude_unset=True)` in favour of the behaviour it produces. |
| `delete_collection` | Docstring reduced to what the route does to the caller's data; the ten-line rationale moved to a comment block above the decorator, with all three file:line citations rewritten as plain description. |

The wider reading: `model_dump(exclude_unset=True)` is not a line reference, but it is an
implementation detail, and §3.8.3 says a docstring describes semantics and "generally not its
implementation details". The same sentence now reads "presence is judged by whether a key appears in
the body, not by whether its value is null", which is the behaviour a client can observe. Revertible if
the narrower reading was meant.

**Verification:** `pytest tests/ -q` → **17 passed**, unchanged from before the edit, which is what a
documentation-only change should do. `grep -rn "py:[0-9]" app/` returns nothing.

**Why the next prompt changed:** the docstring half of Task 1.9 is done; the README half is the other
checkbox and is graded by being run on a clean clone, not by being read.

---

## Entry 81 — the whole repository is swept for comments that the fixes made false

**Prompt:**

> Review all the code and solve all the notes that are not true anymore. Tell me all of them for my
> approval (before doing changes)

**Why this prompt is an iteration (C1.3 — restructured the prompt):** the reply had offered exactly one
stale comment, found in passing, as an optional ride-along. I refused the framing and turned it into a
sweep: every comment in the backend, checked against what the code now does, reported before anything
is touched. A single example found by accident is not evidence that it is the only one.

**What came back:** every comment in `backend/` enumerated with `grep`, then each judged against the
current behaviour rather than against memory. **Nine** false notes, in three groups that are not
equally free to fix:

- **One in application code** — `api.py`, the "there might be an issue with the sorting" note left by
  the previous developer, which Bug #3's fix made false.
- **One of my own** — the docstring of the test updated in Task 1.6 points at the `delete_collection`
  docstring for the strategy, which entry 80 moved into a comment above the route. My own edit created
  this one, an hour after it was written.
- **Seven in provided tests** — the "NOTE: This test currently FAILS due to Bug #1", "might fail due to
  Bug #3" and "will fail due to Bug #2" scaffolding, all now false. These are covered by the standing
  constraint that no provided test may be modified, relaxed once in Task 1.6 and only for the test that
  instructed its own update.

The sweep also turned up something that is **not** a comment problem: `test_delete_prompt` asserts
`status_code in [404, 500]`, which still passes if the 404 regresses to the 500 that Bug #1 produced.
Reported as a finding, not folded into the comment cleanup, because tightening it edits an assertion in
a provided test rather than deleting dead prose.

**Why the next prompt changed:** the three groups need three separate decisions, and the provided-test
group needs a ruling on the constraint rather than a preference. Recorded with the next prompt.

---

## Entry 82 — the nine notes are resolved, with the constraint relaxed for prose only

**Prompt:**

> go with 1, 2 and ii

**What came back:** all nine applied. Groups 1 and 2 were free; group 3 relaxed the
no-modifying-provided-tests constraint a second time, and **only for prose** — no assertion, no
fixture, no control flow was touched, so `pytest` cannot distinguish the tests before and after.

| Item | Where | Resolution |
|---|---|---|
| 1 | `app/api.py` | The "might be an issue with the sorting" note deleted; the true line above it, "Sort by date (newest first)", kept. |
| 2 | `test_delete_collection_with_prompts` | The pointer at the `delete_collection` docstring replaced with the strategy stated in plain words, so it no longer names a place that could move again. |
| 3-5 | `test_get_prompt_not_found` | Docstring reduced to its true one-line summary; the two inline "there's a bug" notes removed. |
| 6-7 | `test_delete_prompt` | Both notes removed. The assertion itself, `in [404, 500]`, deliberately left alone. |
| 8 | `test_update_prompt` | The false "will fail due to Bug #2" note removed. |
| 9 | `test_sorting_order` | Docstring reduced to its summary; the trailing "will fail until Bug #3 fixed" removed. |

**One place where "delete only" needed interpreting, flagged rather than decided quietly.** Item 8 is
three lines, not one: a false NOTE, a true explanation, and a commented-out assertion carrying
`# Uncomment after fix`. Only the false NOTE and that trailing instruction were deleted. The commented
assertion stays commented, because uncommenting it is exactly the assertion edit option **iii** would
have allowed and **ii** does not, and Task 1.4 already covers that behaviour in a test of my own.

**Verification:** `pytest tests/ -q` → **17 passed**, unchanged. A grep for `bug #`, `will fail`,
`might fail`, `after fix` now returns only three hits, all in docstrings I wrote, all true: two naming
Bug #4 as the thing the test covers and one naming Bug #2.

**Left standing, on purpose:** `test_delete_prompt` still asserts `status_code in [404, 500]` and so
would pass if the 404 regressed. Tightening it is an assertion edit; it stays a known weakness rather
than becoming a silent scope creep.

**Why the next prompt changed:** with the code's own notes true again, the remaining untrue document is
the README — which still marks fixed routes as buggy and lists two deleted files.

---

## Entry 83 — the README is rewritten, and running its own steps breaks it

**Prompt:**

> go with C, and test the run steps on a clean clone

**What came back:** the README rewritten as the service's README — what PromptLab is, prerequisites, a
clone/venv/install/run block, a test block, a true endpoint table including `PATCH`, a corrected
structure tree, a "Known issues and limitations" section, and the week plan kept as a trimmed Roadmap.
The stale material went: the ❌/⚠️ bug markers against routes that are now fixed, and the two files
`PROJECT_BRIEF.md` and `GRADING_RUBRIC.md`, deleted in the intake commit but still in the tree diagram.

Then the steps were **executed rather than reviewed**. A faithful clean clone was built with
`git archive HEAD | tar -x` plus the uncommitted working changes — no `.git`, no `__pycache__`, no
virtual environment — and the README block was run line by line:

| Step | Result |
|---|---|
| `python -m venv .venv` | passed |
| `pip install -r requirements.txt` | **failed** |
| `python main.py` | not reached |
| `pytest tests/ -v` | not reached |

`pydantic==2.5.3` publishes no wheel for Python 3.13, the only interpreter on this machine, so pip
fell back to building `pydantic-core` from source, tried to bootstrap a Rust toolchain, and ended in
`metadata-generation-failed`. That is precisely the C1.6 failure the rubric names: "README steps that
fail on a fresh machine."

A second fact surfaced with it: the pins have never been what this code runs on. Every green suite in
this module, including this morning's, used FastAPI 0.141 and Pydantic 2.13 against pins of 0.109 and
2.5.3, and Starlette is imported directly by `api.py` while appearing in no requirements file.

**Why the next prompt changed:** three fixes were offered — narrow the README's version range, bump the
pins, or both — and none of them was the one I wanted.

---

## Entry 84 — a fourth option, from me rather than from the list

**Prompt:**

> another option would be downloading python version and libraries to match the requirements, right?

**Why this prompt is an iteration (C1.3 — restructured the problem):** the three options offered all
changed *the repository* to fit the machine. Mine changes the machine to fit the repository. The
question is not cosmetic: it decides whether a documentation task is allowed to edit dependency pins.

**What came back:** yes, and cheaply — `uv 0.11.19` is installed, so a standalone 3.12 can be fetched
into uv's own cache with no system install and no PATH change. Named option **D**, and its cost stated
without softening: the README must then advertise **Python 3.10–3.12**, so a grader on 3.13, today's
default download, still fails. D proves the repository's own pins; B would make `requirements.txt`
state what the tests have actually been running on all along.

Recommendation given as D first, B second — verify honestly, then decide with real numbers whether to
ship pins that exclude current Python.

**Why the next prompt changed:** I took D.

---

## Entry 85 — the pins are vindicated and the run command is not

**Prompt:**

> yes, go with D

**What came back:** `uv python install 3.12` fetched CPython 3.12.13 in seven seconds. The clean clone
was rebuilt from scratch and the README steps re-run against it:

| Step | Result |
|---|---|
| `python -m venv .venv` | **passed** |
| `pip install -r requirements.txt` | **passed** — fastapi 0.109.0, pydantic 2.5.3, starlette 0.35.1, uvicorn 0.27.0, pytest 7.4.4 |
| `pytest tests/ -v` | **passed — 17 passed**, on the pinned stack, not just the development one |
| `python main.py` | **failed** |

The last row is the find. `python main.py` does not start a server on either stack. It prints
`WARNING: You must pass the application as an import string to enable 'reload' or 'workers'.` and
exits — status 1 under the pinned uvicorn 0.27.0, status 3 under the development 0.52.4. `main.py`
passes the imported `app` object together with `reload=True`, which uvicorn refuses, and its own
module docstring says "Run with: python main.py".

This is **not** one of the brief's four bugs and it is not a Python-version problem. It is a defect the
clean-clone test found precisely because the steps were executed instead of read — the README would
have shipped a run command that has never worked.

The 17-passing suite never caught it because the tests drive the app through `TestClient`, which
imports `app.api:app` directly and never goes near `main.py`.

**Why the next prompt changed:** the fix touches `main.py` or the README's run command, and choosing
between them is a scope decision. Recorded with the next prompt.

---

## Entry 86 — whether the defect had ever been documented, and what that exposed

**Prompt:**

> the problem with main.py was documented?

**Why this prompt is an iteration (C1.3 — narrowed the context):** the reply had presented three ways
to *fix* `main.py` and invited a choice between them. I did not want a fix yet. I wanted to know what
the existing documentation had said about the thing that turned out to be broken, which is a different
search over a different set of files — `SYSTEM_MODEL.md`, the earlier log shards, the verification note
and the brief, not `main.py`.

**What came back:** no, never documented — and `SYSTEM_MODEL.md`, the deliverable recorded as finished,
asserts the opposite in four places:

| Line | Claim | Status |
|---|---|---|
| `:34` | "runs as a single process with a single entrypoint (`main.py:6-10`)" | The entrypoint does not run |
| `:53` | "`main.py` — Process entrypoint. Imports the app and hands it to uvicorn on port 8000" | That handoff is the rejected combination |
| `:573` | "`uvicorn` — ASGI server. Called once, at `main.py:10`" | Called, then refuses |
| `:645` | "a directory run in place by `python main.py` (`main.py:3`)" | False as written |

The fourth is the sharpest: the citation `(main.py:3)` points at the module docstring, `"Run with:
python main.py"`. The document proved how the service runs by quoting the code's own claim about how
it runs. Both are wrong and they agree with each other, which is exactly why neither looked suspicious.

Also noted, and true: `SYSTEM_MODEL.md:579-581` already contained the only accurate description of how
the service can be started — "served by any external ASGI runner pointed at `app.api:app`" — written to
make a point about dependency coupling, not about run instructions.

**Why the next prompt changed:** three separable decisions fell out of one question, so I took all
three at once.

---

## Entry 87 — documentation as the fix, and the three corrections

**Prompt:**

> I think we should go for C as we were not asked to change this part of the code and that is why we
> can use the documentation for. Then correct the SYSTEM_MODEL lines accordingly and yes, add this
> error to the varification note

**What came back:** the reasoning accepted as given — `main.py` is outside what the module asked to
change, and a defect that is not fixed must be *documented* rather than hidden, which is Rule 5 read
the right way round. Three pieces of work:

**1. README (option C).** The run command is now `uvicorn app.api:app --reload`, with a blockquote
warning against `python main.py` directly under it. The prerequisite narrowed from "3.10 or newer" to
**3.10–3.12, not 3.13**, with the reason given and the tested version named. Two entries added at the
top of *Known issues*: the dead entry point, and the undeclared upper bound on the interpreter. The
structure tree now labels `main.py` as not working.

**2. `SYSTEM_MODEL.md`.** All four claims corrected, plus a new paragraph in §6.1 recording the defect
with both measured exit statuses and the reason the suite cannot see it. §6.5 changed in a way worth
noting: it had said `pydantic==2.5.3` "will not build on an interpreter far from the one it was
released for — that is an inference from the pin, not a statement the repository makes". The inference
was honest and it is now **measured**, so the paragraph says so and gives both results.

**3. Verification note.** Deferred to its own step — see the next entry.

**Verification, on the rebuilt clean clone, with the README followed literally:**

| Step | Result |
|---|---|
| `python -m venv .venv` (3.12.13) | passed |
| `pip install -r requirements.txt` | passed |
| `pytest tests/ -v` | **17 passed** |
| `uvicorn app.api:app --reload` | **server up** |
| `GET /health` | `{"status":"healthy","version":"0.1.0"}` |
| `GET /docs`, `/redoc`, `/openapi.json` | 200, 200, 200 |
| `POST /prompts` → `PATCH` with one field | description changed, **title unchanged**, `updated_at` bumped |
| `GET /prompts/nope` | 404 |
| `POST /prompts` with an empty title | 422 |

Every claim the README makes about running the service has now been executed on a clean tree rather
than asserted.

**Why the next prompt changed:** the note's closing section is built on three cases sharing one failure
mode, and this fourth case does not share it. Recorded with the next prompt.

---

## Entry 88 — the note gains a fourth case and a second failure mode

**Prompt:**

> go with A

**What came back:** `docs/ai-verification-note.md` restructured rather than extended. Case 4 written
with the brief's four fields — what the AI produced (the four `SYSTEM_MODEL.md` statements, quoted),
why it was wrong (uvicorn refuses an app object together with `reload=True`; both exit statuses
given), how it was detected (the README steps executed on a clean clone, not read), and what was done
instead (four corrections, a new §6.1 paragraph, and the README documenting the command that works
while naming the broken one under *Known issues*).

The closing section, previously "What the three have in common", is now "What the four have in
common" and splits in two:

- **Mode 1 — a claim about a set, asserted without enumerating the set.** Cases 1, 2 and 3, unchanged,
  with entries 33 and 54 still named as further instances.
- **Mode 2 — a self-description read instead of executed.** Case 4 alone. It quantifies over nothing,
  names a line, and the line it names *supports* it.

A comparison table sets the two side by side, and the argument the split makes is that **mode 2 is the
more dangerous**: a mode 1 error is contradicted by the source, so any reader who opens the file can
catch it, while a mode 2 error is confirmed by the source, so reading more carefully makes it look
better rather than worse. The survival times bear it out — mode 1 caught inside the same exchange,
mode 2 surviving four tasks and several reviews.

The three shared properties became four, the new one being that no tooling caught any of them: a green
suite and a service that will not start are compatible states, because the tests import the
application directly and never execute the broken file.

**Why option C was not taken.** It would have looked stronger — one deep thesis covering all four — but
the unifying sentence would have had to be stretched to fit, and a note whose subject is
over-generalisation cannot afford to over-generalise in its own conclusion.

**Why the next prompt changed:** Task 1.9's work is complete and unstaged. What remains is the commit
split and the messages, which need approval before anything is written.

---

## Entry 89 — the shards are merged, and the merge is made repeatable

**Prompt:**

> do it

**What came back:** `docs/prompt-log.md`, the C1.3 deliverable, written for the first time — it had
been deliberately empty until now, so that no merged file could exist before the work it records.

The merge is a script, `docs/prompt-log/merge_log.py`, rather than a one-off paste, because the shards
stay in place and any later task will invalidate a hand-merged file. It drops each shard's front
matter, splits on the entry headings rather than on `---` rules, and concatenates in filename order
under one heading.

**Two things it found that a paste would not have.**

- **The first splitter lost eleven entries.** Splitting on `\n---\n` silently dropped every entry
  containing a horizontal rule of its own: 88 entries went in, 77 came out, and the gap was caught
  only because the script asserts that the numbers it collects run 1..N with no holes. The assertion
  was there before the bug, which is the only reason it was a two-minute problem.
- **The em-dash trap recorded in `CLAUDE.md` was real but described wrongly.** It said the shards hold
  literal `—` text. They do not. Four shards are clean UTF-8; shard `02` alone carries **68 literal
  `—` and 2 `–` escape sequences**, written that way by an earlier session. The merge
  unescapes any `\uXXXX` on the way out and leaves the shards exactly as committed, which is what the
  trap note instructed. The note has been corrected rather than just ticked off.

**The header is not a summary of the log**; it is the part a grader needs and the entries cannot
provide: what the file is, that the first person is me rather than the assistant, how the liveness is
evidenced (one shard per task, each committed as written, interleaved with the work), a task map from
entry ranges to deliverables, and an index of the **30 C1.3 iterations** with what each one did. The
index is derived from the entries by the script, not hand-kept, so it cannot drift from them.

**Verification:** 88 entries in, 88 out, numbering continuous from 1; zero `\uXXXX` escapes left; and
the merged body compared against the shard bodies character for character with whitespace stripped —
identical, so nothing was lost or silently rewritten.

**Why the next prompt changed:** Module 1's deliverables are all in place. What remains is the
verification pass the brief describes — the suite, then a fresh clone followed by my own README.
