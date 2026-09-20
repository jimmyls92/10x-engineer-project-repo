# CLAUDE.md — PromptLab Module 1 (Brownfield Challenge)

Working protocol for this repository. Read this before doing anything else in a new session.

---

# ⇒ CURRENT STATE

**Keep this block accurate. Update it whenever a task starts or finishes, in the same commit as the
work.** It is how a new session resumes without reading everything.

| | |
|---|---|
| **Current task** | **Task 1.6 is COMPLETE** — Bug #4 fixed at `api.py:159-164` by nulling `collection_id`; the provided test was updated on its own written instruction and a new test added; suite **15 passed**. **Next: Task 1.7 — implement `PATCH /prompts/{id}`.** Not started. |
| **Log shard to append to** | `docs/prompt-log/02-tasks-1.3-1.7.md` — open, entries 41–64 written |
| **Next entry number** | 65 |
| **Context stage** | Task 1.1's staged exploration is finished. Six stages, six recorded context decisions: 1 whole-repo (size) · 2 file-level `api.py` (concentrated coupling) · 3 three files (`api.py`, `storage.py`, `utils.py`) · 4 whole-repo including `tests/` (distributed coupling) · 5 `storage.py` + `api.py` (supply vs. demand) · 6 `requirements.txt` against every import in `app/` + `main.py` (declaration vs. use). The bug-fix tasks are not staged exploration and open no new C1.2 rows; the table is closed at six. |

**Task 1.1 is staged by section of the deliverable**, one context decision each — the user's
restructuring in entry 8, because one rationale cannot honestly cover six different questions.
**Use the brief's own section names** (see *Section naming* below):
1. Architecture ✅ · 2. Entry points ✅ · 3. Data flow ✅ · 4. Models and relationships ✅ ·
5. Storage layer ✅ · 6. External dependencies ✅ · plus the Context strategy section ✅, one row per stage.

**Done:** setup. Working protocol agreed, `CLAUDE.md` written, prompt log opened and sharded.
Task 1.1 stage 1 — `docs/SYSTEM_MODEL.md` § Architecture (1.1 what it is, 1.2 components, 1.3 how
they fit, 1.4 characteristics) and the § Context Strategy stage-1 row. Task 1.1 stage 2 —
§ Entry points (2.1 route table, 2.2 the FastAPI-contributed routes, 2.3 notes on the surface) and the
§ Context Strategy stage-2 row. Stages 3, 4, 5 and 6 likewise — **`docs/SYSTEM_MODEL.md` is finished**
and nothing in it is outstanding.

**Established in Task 1.6** (do not re-derive; do cite): **strategy chosen — null the `collection_id`**,
recorded as a docstring on `delete_collection` (`api.py:145-158`), which is where the brief's "record
your reasoning in a line or two" (`brief.txt:66`) is satisfied · the case rests on the data model:
`collection_id` is `Optional`, unconstrained, and `Collection` has no back-reference, while `title` and
`content` are required — so membership is incidental, not essential · **the brief never says provided
tests are immutable**, only that they must pass (`brief.txt:53,109,186`), and `test_delete_collection_with_prompts`
instructed its own update in its docstring, so the no-modify constraint was relaxed **for that one test
only**; `test_update_prompt` stays untouched · the `if prompts:` guard was removed, not kept — it would
let a wrongly-deleted prompt pass silently · `model_copy` + `update_prompt`, never in-place mutation,
because storage hands out uncopied objects · `updated_at` is **not** bumped on unfiling · the loop must
run after the 404 guard, since existence check and deletion are fused in one expression · **suite is
15 passed** · `delete_collection` owes Args/Returns/Raises to Task 1.9, alongside `update_prompt` and
`sort_prompts_by_date`.

**Established in Task 1.5** (do not re-derive; do cite): the fix was one expression, `utils.py:9`,
`reverse=descending` — not `reverse=True`, which would pass the test while leaving the parameter dead
· **`sort_prompts_by_date` has exactly one caller**, `api.py:60`, reached only through the HTTP route;
`grep` returns just definition, import and call · **sorting is not a query parameter** — `list_prompts`
declares only `collection_id` and `search` (`api.py:44-45`) and `descending=True` is a literal at the
call site, so there is no client-facing default to get wrong · `test_sorting_order` sends **no
parameters** and asserts **position 0 only**, defining "newest" by creation order, not by a named field
· the sort key is `created_at`, the field Task 1.4 left untouched · **the suite is now fully green at
14 passed**, which is the "nothing previously working broken" bar for every later task.

**Established in Task 1.4** (do not re-derive; do cite): the bug was one field, `api.py:106`, and
`get_current_time` was already imported (`api.py:11`) · **`created_at` and `updated_at` already differ at
creation** — `models.py:34-35` runs two separate `default_factory` calls — so `updated_at > created_at`
passes with the bug present and proves nothing; the test compares `updated_at` before the PUT against
`updated_at` after it · timestamps serialise as **naive ISO-8601 strings**, parsed with
`datetime.fromisoformat` · `utcnow()` was measured at **microsecond resolution**, so no `sleep` is
needed in a timestamp test · the provided `test_update_prompt` is a half-written version of this test:
it captures `original_updated_at` (`test_api.py:89`), sleeps 0.1 s, and leaves the assertion commented
out at `:108` — left commented, by the user's constraint that no provided test be modified · the
docstring on `update_prompt` is owed to Task 1.9, not written here.

**Established in Task 1.3** (do not re-derive; do cite): **baseline before any fix was 3 failed /
10 passed** — `test_get_prompt_not_found`, `test_delete_prompt` (both `AttributeError` at the old
`api.py:73`) and `test_sorting_order`. Ten passing tests are the bar for "nothing previously working
broken" · **Bug #1 broke two tests, not one** — `test_delete_prompt` re-fetches after deleting
(`test_api.py:83`) · **Bugs #2 and #4 have no failing provided test**: `test_update_prompt` passes with
the `updated_at` bug present, and `test_delete_collection_with_prompts` passes *because* it asserts the
orphaning · `storage.get_prompt` has exactly two callers, `api.py:70` and `api.py:91`, both wanting 404
· after the fix: **12 passed / 1 failed**, the failure being Bug #3.

**Established in stage 6** (do not re-derive; do cite): three of the six pins — `pytest`, `pytest-cov`,
`httpx` — have no importer under `app/` or `main.py` (`requirements.txt:4-6`); `httpx` is imported by
name nowhere in the repository and is needed only because `TestClient` is built on it · **Starlette is
relied on directly and declared nowhere**: `api.py:4` imports `CORSMiddleware`, whose `__module__` is
`starlette.middleware.cors` · no lock file, no `pyproject.toml`, no `python_requires`, no `Dockerfile`
— the interpreter is undeclared too · **the installed FastAPI is `0.141.1` against a pinned `0.109.0`,
and nothing detects it** · `uvicorn` is touched only under the `__main__` guard (`main.py:6,10`) · `re`
is imported inside a function body (`utils.py:48`) in an unreferenced helper · no env vars, no `open()`,
no config parser — the root `config.yaml` is read by nothing under `backend/`.

**Established in stage 5** (do not re-derive; do cite): two structurally independent dicts keyed by the
entity's own `str` id (`storage.py:13-14`); the prompt→collection link is never stored, only recomputed
by iterating every prompt (`storage.py:58-59`) · one module-level instance bound by direct import
(`storage.py:69`, `api.py:13`); `clear()` is called by nothing in `app/` · eleven methods grouped by
return type in §5.2, each with its `api.py` call site · **§5.3 holds thirteen limitations**, of which
rows 4, 5 and 6 share one shape — the guarantee is absent from the layer and whatever stands in for it
lives elsewhere (`api.py:104`, `models.py:35,55`) · row 4 is "no primitive for concurrent writes", *not*
"no concurrency control" — the user corrected that, since `api.py` could serialise externally · rows 2
and 3 share the cause `storage.py:69` but are separately fixable.

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

**Not started:** Task 1.7 (`PATCH /prompts/{id}`) ← *next* · Task 1.8 (AI-verification note) · Task 1.9
(docstrings + README).

**Why this restart exists.** An earlier attempt completed Tasks 1.1 and 1.2 in a single reply. The
output was accurate and it was **deliberately deleted**, because the user learned nothing from
watching it appear. `docs/SYSTEM_MODEL.md` is being rebuilt stage by stage under Rule 0b. Do not
reproduce the remaining sections from `00-setup.md`, and do not treat the findings recorded there as
established — the point is for the user to reach them. `00-setup.md` entries 3 and 4 exist as an
honest record of the discarded attempt, not as a shortcut.

**Open decisions:**

- ~~**Bug #4 strategy**~~ — **settled in Task 1.6: null the `collection_id`.** The reasoning is the
  docstring on `delete_collection` (`api.py:145-158`); that is the artefact to take into the Module 5
  oral. No longer open.

- **Task 1.8 probe is pre-chosen by the brief.** `brief.txt:84` suggests asking the AI to explain the
  collection-deletion behaviour or justify a fix, then checking it against the code, as the deliberate
  C1.5 probe. Surfaced during Task 1.6; do not act on it before Task 1.8.

**Known traps:**

- ~~**`tests/test_api.py` asserts the buggy orphaning behaviour**~~ — **resolved in Task 1.6**: that
  test was updated on its own written instruction, and its `if prompts:` guard removed. The standing
  "no provided test may be modified" constraint still holds for **every other** provided test.
- **`TestClient` defaults to `raise_server_exceptions=True`**, which re-raises rather than returning
  500. Confirmed at the Task 1.3 baseline — both Bug #1 failures surfaced as a raised `AttributeError`,
  not as a 500 response. Kept because the same will hold for any later handler that can raise.
- **The brief asks for a new test on two tasks only.** Bug #2 "verify with a test" (brief line 60) and
  Bug #4 "add a test" (line 66). Bug #1 says "make the provided test pass" (57) and Bug #3 says only
  "verify" (63); C1.4's evidence line asks for "all **provided** tests" (186). Do not invent test
  obligations the brief does not impose — this file used to, see the work order.

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

### 6. Commit messages are graded, and the user approves every one before it is written

"Meaningful commit messages" is a checklist item in the brief (page 3). Meaningful, specific messages;
**one logical change per commit**.

**Never run `git commit` without showing the message first and getting an explicit yes.** Propose the
full message — subject and body as they will actually be committed — in the chat reply, say which files
are staged, and stop. The user may accept it, edit it, or ask for a different split into commits. This
is the same stop Rule 0b imposes on every other step: a commit is a step, and the message is the part
of it that gets graded.

If the user has already said "commit it" in the prompt being acted on, that is approval for the commit
but **not** for the message — still show the message and wait, unless they say to stop asking.

**Length, set by the user and not negotiable:**

- **Subject**: imperative, **≤ 50 characters**, naming the change — `Fix Bug #1: 404 on missing prompt`.
  The task or criterion goes in the body if it will not fit.
- **Body**: **at most two sentences, about twenty words each.** Why, not what — the diff already shows
  what changed. Cite `file.py:line` inside a sentence rather than adding a line for it.
- Nothing else. No bullet lists, no "Also …" paragraph, no test-count tables.

*The messages written before this rule are much longer. They stand as committed — rewriting history to
match a later convention would be worse than the inconsistency.*

**Do not bundle.** One logical change per commit is what keeps two sentences sufficient: if the message
needs an "Also …", it is two commits. Propose the split and let the user decide.

**What the body is for.** The one thing a short message must still carry is the reasoning that leaves
no trace in the diff — a claim corrected, a section deliberately not written, an option rejected. If
only one sentence can be spent, spend it there.

## Work order

Progress lives in CURRENT STATE at the top of this file, not here.

1. Protocol setup — `CLAUDE.md` and the prompt log opened. ← *before any code is read*
2. Task 1.1 — staged exploration → `docs/SYSTEM_MODEL.md`, six sections plus context strategy.
   (Task 1.2, the prompt log, runs continuously alongside every task — it is not a step of its own.)
3. Tasks 1.3–1.7 — 4 bug fixes + `PATCH /prompts/{id}`. **The test obligation is per task, in the
   brief's own words, and is not uniform** — an earlier version of this line said "each with a test",
   which overstates the brief and was corrected in Task 1.3:
   - **1.3** Bug #1 — "make the **provided** test pass". No new test owed.
   - **1.4** Bug #2 — "**verify with a test**". One is owed; nothing provided fails for this bug.
   - **1.5** Bug #3 — "fix the order, **verify**". A provided test covers it; no new test demanded.
   - **1.6** Bug #4 — "implement it, and **add a test**". One is owed, explicitly.
   - **1.7** PATCH — four behaviour checkboxes, no test wording.
4. Task 1.8 — `docs/ai-verification-note.md`.
5. Task 1.9 — docstrings on touched functions + README run instructions.
6. Merge the log shards → `docs/prompt-log.md`, as its own commit.
7. Verify: `cd backend && pytest tests/ -v`, then clone to a fresh directory and follow the README.

## Verification command

```
cd backend
pytest tests/ -v
```
