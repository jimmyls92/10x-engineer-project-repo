# CLAUDE.md — PromptLab Module 1 (Brownfield Challenge)

Working protocol for this repository. Read this before doing anything else in a new session.

---

# ⇒ CURRENT STATE

**Keep this block accurate. Update it whenever a task starts or finishes, in the same commit as the
work.** It is how a new session resumes without reading everything.

| | |
|---|---|
| **Current task** | **Task 1.1 — explore the code and write it up.** In progress: stages 1–4 of 6 done. |
| **Log shard to append to** | `docs/prompt-log/01-tasks-1.1-1.2.md` — entries 7 onwards |
| **Next entry number** | 32 |
| **Context stage** | **Stage 5 — Storage layer, in progress. Context level chosen: two files, `storage.py` + `api.py`**, argued from coupling — `storage.py` calls nothing and is called from exactly one file, so it defines the whole supply and `api.py` the whole demand; a limitation is a gap between them that neither file shows alone. Cost stated: `tests/` out of scope this stage. Sub-parts: **5.1 ✅** what the store is · **5.2 ✅** the operation surface (cut by return type) · **5.3 limitations ← next**. The planned "how objects enter and leave" was **dropped by the user in entry 32** as already established in §3; limitations moved up from 5.4 to 5.3, and anything resting on object identity cites §3 rather than restating it. **Parked for 5.3 — four items deliberately cut from 5.2 so that 5.4 reaches them:** (1) no duplicate-**id** check, assignment silently replaces (`storage.py:19,43`) — state the caveat that ids are server-generated (§4.4) so no route reaches it today; (2) no duplicate-**content** check, two prompts with identical title/content under different ids both stored — the user's own addition; (3) the collection half has no update method; (4) `update_prompt` takes a complete `Prompt`, so the store offers replacement and never modification. **Standing constraint the user imposed: a sub-part may only make claims of its own kind — 5.1–5.2 describe, 5.3 judges.** Stage 1 whole-repo (size), stage 2 file-level `api.py` (concentrated coupling), stage 3 three files (`api.py`, `storage.py`, `utils.py`), stage 4 whole-repo including `tests/` (distributed coupling). Rows 1–4 plus the closing note on what the narrowing bought are in `SYSTEM_MODEL.md` § Context Strategy; **the stage-5 row is written last, after 5.4.** §4.2 has already characterised part of the storage layer, so stage 5 cites rather than re-derives. |

**Task 1.1 is staged by section of the deliverable**, one context decision each — the user's
restructuring in entry 8, because one rationale cannot honestly cover six different questions.
**Use the brief's own section names** (see *Section naming* below):
1. Architecture ✅ · 2. Entry points ✅ · 3. Data flow ✅ · 4. Models and relationships ✅ ·
5. Storage layer ← *next* · 6. External dependencies · plus the Context strategy section, which grows
a row per stage.

**Done:** setup. Working protocol agreed, `CLAUDE.md` written, prompt log opened and sharded.
Task 1.1 stage 1 — `docs/SYSTEM_MODEL.md` § Architecture (1.1 what it is, 1.2 components, 1.3 how
they fit, 1.4 characteristics) and the § Context Strategy stage-1 row. Task 1.1 stage 2 —
§ Entry points (2.1 route table, 2.2 the FastAPI-contributed routes, 2.3 notes on the surface) and the
§ Context Strategy stage-2 row.

**Established in stage 4** (do not re-derive; do cite): the link is many-to-one, declared only on the
child (`models.py:23`); `Collection` has no back-reference (`models.py:54-59`) · `collection_id` is the
one client-supplied field with no `Field(...)` constraint, and is not typed `UUID` · integrity is
imposed in exactly two handlers, at write time only (`api.py:80-83,96-99`); nothing checks on read ·
`storage.get_prompts_by_collection` (`storage.py:58-59`) is the query a cascade would need and is
called by nothing · **observed**: deleting a collection leaves the prompt with its `collection_id`
intact, and the dead id still filters · `PUT` unfiles a prompt when the body omits `collection_id`
(`api.py:108`), as `test_api.py:92-101` does · `PromptCreate` and `PromptUpdate` are identical to
`PromptBase`, so update cannot express "leave unchanged" · ids/timestamps are server-assigned via
`default_factory` and absent from the `*Create` DTOs · `utcnow()` is naive (`models.py:13-14`) ·
`from_attributes = True` is vestigial, there is no ORM.

**Established in stage 3** (do not re-derive; do cite): storage hands out and files away **uncopied**
objects (`storage.py:19,23,26`), and `PUT` is the only route that could mutate the store but rebuilds
instead (`api.py:103-111`) · the sort defect is in the helper, not the call site — `descending` is
declared and never read (`utils.py:7-14`), `api.py:60` passes it correctly · validation is entirely
pre-handler, so every handler guard is existence or cross-entity, never field-level · the collection
filter exists twice (`storage.py:58`, `utils.py:17`) and the flow uses the utils one (`api.py:52`) ·
`utils.py` is typed `List[Prompt]` throughout, which is why collections have no listing transform.
**Verified by execution, not reading** (§3.3): miss on `GET /prompts/{id}` is an observed 500 over
`AttributeError: 'NoneType' object has no attribute 'id'`; body violations are 422; unknown
`collection_id` is 400. `TestClient`'s default `raise_server_exceptions=True` re-raises instead of
returning 500 — this matters for the Task 1.3 test.

**Established in stage 2** (do not re-derive; do cite): ten declared routes, all in `api.py` with no
`APIRouter`, plus `/docs`, `/redoc`, `/openapi.json` from the app object · the listing pipeline is a
fixed filter → search → sort and `total` is computed after it (`api.py:51-62`) · `PUT` is a full
rebuild, not a merge (`api.py:103-111`) · 404 discipline splits on return type — `Optional` getters
need a guard, `List` getters do not, and `api.py:73` is the one place the result is dereferenced before
being guarded · unknown addressed resource is 404 but unknown referenced collection in a body is 400
(`api.py:83,99`) · `api.py:113` returns an `Optional` unchecked, safe only via the upstream guard.

**Established in stage 1** (do not re-derive; do cite): `models` is the dependency leaf, no cycles
(`app/models.py:3-6`, `storage.py:8`, `utils.py:4`, `api.py:7-15`) · `api.py` is the sole coupling hub
at 160 lines, so later stages should justify going file-level there · storage is a concrete global
with no injection seam (`storage.py:69`, `api.py:13`) · all validation is declarative in `models.py`
(`20-22`, `46-47`) · `extract_variables` and `validate_prompt_content` are unreferenced
(`utils.py:30,43`) · the service never calls an LLM (`requirements.txt:1-6`).

**Not started:** Task 1.3 (Bug #1, 404) ·
Task 1.4 (Bug #2, `updated_at` on PUT) · Task 1.5 (Bug #3, newest-first sorting) · Task 1.6 (Bug #4,
orphaned prompts) · Task 1.7 (`PATCH /prompts/{id}`) · Task 1.8 (AI-verification note) · Task 1.9
(docstrings + README).

**Why this restart exists.** An earlier attempt completed Tasks 1.1 and 1.2 in a single reply. The
output was accurate and it was **deliberately deleted**, because the user learned nothing from
watching it appear. `docs/SYSTEM_MODEL.md` is being rebuilt stage by stage under Rule 0b. Do not
reproduce the remaining sections from `00-setup.md`, and do not treat the findings recorded there as
established — the point is for the user to reach them. `00-setup.md` entries 3 and 4 exist as an
honest record of the discarded attempt, not as a shortcut.

**Open decisions:**

- **Bug #4 strategy** — cascade-delete the prompts / null their `collection_id` / block deletion of a
  non-empty collection. Belongs to Task 1.6; do not raise it before then. The reasoning must be
  recorded; it is defended in the Module 5 oral.

**Known traps:**

- **`tests/test_api.py:154-179` asserts the *current*, buggy orphaning behaviour** — line 178 asserts
  the prompt keeps the deleted collection's id, guarded by `if prompts:`. C1.4 requires every provided
  test green, so the Bug #4 strategy and this test have to be settled together in Task 1.6. Do not
  raise it before then.
- **`TestClient` defaults to `raise_server_exceptions=True`**, which re-raises rather than returning
  500. Matters when writing the Task 1.3 test.

**Pending at the end:** merge the log shards into `docs/prompt-log.md` (see
`docs/prompt-log/README.md`). That file is currently empty on purpose — until the merge commit exists,
the graded deliverable does not.

---

## Context

AIE 500 / PromptLab, Module 1, Competency C1 — *Codebase Comprehension & AI-Assisted Debugging*.
Source of truth for requirements: `1785592803-Module_1_Project_Brownfield_Challenge.pdf` (repo root).

The PDF has no text layer the `Read` tool can take directly, and `pdftoppm` is not installed. Extract
it with PyMuPDF, which *is* installed — write to a file rather than stdout, because the Windows
console encoding cannot print the `→` the brief uses:

```
python -c "import pymupdf,pathlib; d=pymupdf.open('1785592803-Module_1_Project_Brownfield_Challenge.pdf'); pathlib.Path('brief.txt').write_text('\n'.join(p.get_text() for p in d),encoding='utf-8')"
```

## Section naming

**Use the brief's own words for every section and task heading.** The user asked for this explicitly;
matching names is how an assessor confirms a checklist item is covered without having to interpret a
synonym. The Task 1.1 checklist, verbatim from page 1:

| Section in `SYSTEM_MODEL.md` | The brief's gloss |
|---|---|
| **Architecture** | what the service is and how it's put together |
| **Entry points** | every route the application exposes |
| **Data flow** | how a request travels from route to storage and back |
| **Models and relationships** | how prompts and collections relate |
| **Storage layer** | how it works and what its limitations are |
| **External dependencies** | everything the service relies on |
| **Context strategy** | per exploration stage: whole repository or single file, and why, based on the size or coupling of the code |

Task names, also verbatim: **1.1** Understand the codebase · **1.2** Keep a prompt log · **1.3–1.7**
Fix the bugs and add the missing endpoint · **1.8** Document one AI mistake · **1.9** Document what you
rescued. Note that the context strategy section belongs to **Task 1.1**, not 1.2 — 1.2 is the prompt
log. The *criterion* C1.2 is what grades the context strategy; the task and criterion numbers do not
line up, and conflating them is what produced the earlier mislabelling.

Two criteria (C1.3, C1.5) are graded on **process evidence that can only be captured while working**.
The brief states explicitly that this evidence "cannot be convincingly reconstructed afterwards."
Everything below exists to protect that.

## Deliverables

| Criterion | Evidence file | Requirement |
|---|---|---|
| C1.1 | `docs/SYSTEM_MODEL.md` | Architecture, **every** route, request→storage→back data flow, prompt/collection relationship, storage layer + its limitations, **every** external dependency. Nothing may contradict the code. |
| C1.2 | `docs/SYSTEM_MODEL.md` § Context Strategy | Per exploration stage: whole-repo or file-level context, with a reason grounded in the **size or coupling** of the code. Must match the prompt log. |
| C1.3 | `docs/prompt-log.md` | ≥2 iterations that **narrowed context, added a constraint, or restructured** a prompt because the output was not good enough. Rewording does not count. |
| C1.4 | Repository + `pytest tests/ -v` | **MUST PASS.** All 4 bugs fixed, `PATCH /prompts/{id}` implemented, all provided tests green, nothing previously working broken. |
| C1.5 | `docs/ai-verification-note.md` | ≥1 specific wrong AI output: what it produced, why it was wrong, how it was detected, what was done instead. Must be traceable to a `prompt-log.md` entry. |
| C1.6 | Docstrings + `README.md` | Google-style docstrings (Args/Returns/Raises matching the real implementation) on **every** function added or modified. README run steps must work on a clean clone. |

## Rules

### 0. Answer the current task, and only the current task

Work the task named in CURRENT STATE. Scope is set by what that task asks for and what the rubric
grades it on — nothing else.

Do **not** raise, decide, or ask about anything belonging to a later task, even when the whole
codebase is already in context and the answer seems obvious now. Having the context is not a reason
to use it early. If something relevant to a later task surfaces, add it to **Open decisions** or
**Known traps** in CURRENT STATE and carry on.

*This rule exists because a Bug #4 strategy decision (Task 1.6) was put to the user during Task 1.1.
It was out of scope and the user rejected it.*

Finishing a task means: deliverable written, its log entry appended, CURRENT STATE updated, committed.
Then stop and report — do not roll straight into the next task.

### 0b. Work step by step. Never complete a task in one reply.

**This is an educational project. The user is learning to work with AI, not commissioning output.** A
correct deliverable that appeared in one turn is a failed turn, however good it is. This rule was
added *after* Tasks 1.1 and 1.2 were one-shotted and the result deleted on purpose.

Break every task into small steps — typically 3 to 6. At each step:

1. **Say what this step is for**: what it should achieve, and why it comes now rather than later.
2. **Give the user 2–3 concrete angles** they could take, with the trade-off between them. Enough that
   the choice is informed; not so much that it is made for them.
3. **Stop. Wait for their prompt.** They write it — you do not draft it for them. Choosing the angle
   and phrasing the prompt is the skill being practised, and C1.3 grades iteration *they* drove.
4. Act on what they actually sent, then log the entry, then propose the next step.

Hard limits:

- **One step per reply.** Never run two steps because the next one seems obvious.
- **Never pre-empt a step's finding.** If you already know the answer (from earlier context, from
  `00-setup.md`, from a discarded attempt) do not state it. Set up the step that lets the user find
  it. Volunteering the conclusion destroys the step's value.
- **Do not write a deliverable until its content has been worked through step by step.** The document
  is a write-up of work already done together, never the first place the analysis appears.
- If the user says to go faster or to just do it, do that — but say once what is being skipped.

*Rule 0 keeps work inside the task. Rule 0b keeps it inside one step. They fail differently: Rule 0
was broken by asking a Task 1.6 question during Task 1.1; Rule 0b was broken by answering all of
Task 1.1 at once.*

### 1. Prompt log is written live, never reconstructed

The log is **sharded by task** under `docs/prompt-log/`, one file per task from the brief, and merged
into `docs/prompt-log.md` once at the end. `docs/prompt-log/README.md` holds the shard table and the
merge procedure. **Load only the shard for the current task** — that is the point of the split; do not
read the whole history to append one entry.

After **every** user prompt in this repo, append an entry to the current shard (the one named in
CURRENT STATE) before or alongside doing the work. An entry contains:

- **Prompt** — the user's message, verbatim.
- **What came back** — summary of the response; paste the relevant part.
- **Why the next prompt changed** — one line. If the output was good enough, say so.

Write entries in the user's first-person voice — he is the one prompting. Never invent a prompt that
was not actually sent. Never backfill a gap by guessing; if an entry is missing, mark it as missing.

Flag explicitly in the entry whenever an iteration **narrowed context, added a constraint, or
restructured** the prompt — those are the C1.3 evidence points.

Entry numbers run continuously across shards, so the merge is a plain concatenation in filename order.
The next number is in CURRENT STATE. Start a new shard when the task changes; split an oversized shard
with a lettered suffix (`02a-`, `02b-`) and update the table in `docs/prompt-log/README.md`.

### 2. Exploration is staged deliberately, and the staging is honest

Explore in stages, and **do not read files ahead of their stage**. The rationale recorded in
`SYSTEM_MODEL.md` § Context Strategy must be the actual reason, matching the prompt log:

- **Stage 1 — whole-repo orientation.** Small repo; need overall shape and module boundaries before
  detail is meaningful.
- **Stage 2+ — file-level deep reads.** Target individual files (`storage.py`, `api.py`, …) where
  coupling or subtle behaviour means whole-repo context would dilute attention.

Record for each stage which context level was used and why. A rationale that does not match what the
log shows actually happened is a C1.2 failure.

### 3. Verify every claim against the source

`SYSTEM_MODEL.md` must describe what the code does, not what the AI said it does. Before writing any
claim about behaviour, confirm it in the source. The most common reason C1.1 comes back *Not Yet* is
a claim that contradicts the code.

### 4. Capture AI mistakes the moment they happen

When a statement turns out to contradict the code, **stop and document it** in
`docs/ai-verification-note.md`: what was produced, why it was wrong, how it was caught, what was done
instead. Cross-reference the `prompt-log.md` entry it came from.

A syntax error an editor would flag does not count. The target is output that *looked right*.
Preference is for organically occurring mistakes; if none has surfaced by the time the fixes are done,
run a deliberate probe (e.g. ask for a justification of the collection-deletion behaviour from memory,
then check it against the code).

### 5. Never hide a bug

Explicitly called out in the rubric: catching an exception and discarding it counts as a bug still
present. Fixes must address the cause.

### 5b. Keep replies short and scannable

The user asked for this explicitly. Long prose replies are harder to follow than the work deserves.

- **Bullets over paragraphs.** Bold the thing that matters in each bullet.
- **Use tables instead of bullets** when a comparison or the message itself can be enhance.
- **Cut anything that is not a finding, a decision, or a question.** No recaps of what was just done
  when the diff already says it, no restating the rule being followed, no narrating the plan.
- **Cite `file.py:line` instead of quoting code** unless the exact text is the point.
- This constrains **chat replies only**. Deliverables (`SYSTEM_MODEL.md`, the prompt log,
  `ai-verification-note.md`, docstrings) stay as thorough as the rubric needs — they are graded on
  completeness, not brevity.

Rule 0b still holds: short does not mean skipping the step, the angles, or the stop.

### 6. Commit messages are graded

Meaningful, specific commit messages. One logical change per commit.

## Work order

Progress lives in CURRENT STATE at the top of this file, not here.

1. Protocol setup — `CLAUDE.md` and the prompt log opened. ← *before any code is read*
2. Task 1.1 — staged exploration → `docs/SYSTEM_MODEL.md`, six sections plus context strategy.
   (Task 1.2, the prompt log, runs continuously alongside every task — it is not a step of its own.)
3. Tasks 1.3–1.7 — 4 bug fixes + `PATCH /prompts/{id}`, each with a test.
4. Task 1.8 — `docs/ai-verification-note.md`.
5. Task 1.9 — docstrings on touched functions + README run instructions.
6. Merge the log shards → `docs/prompt-log.md`, as its own commit.
7. Verify: `cd backend && pytest tests/ -v`, then clone to a fresh directory and follow the README.

## Verification command

```
cd backend
pytest tests/ -v
```
