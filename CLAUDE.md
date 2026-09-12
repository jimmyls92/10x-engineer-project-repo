# CLAUDE.md — PromptLab Module 1 (Brownfield Challenge)

Working protocol for this repository. Read this before doing anything else in a new session.

---

# ⇒ CURRENT STATE

**Keep this block accurate. Update it whenever a task starts or finishes, in the same commit as the
work.** It is how a new session resumes without reading everything.

| | |
|---|---|
| **Current task** | **Task 1.1 — explore the code and write it up.** In progress: stage 1 of 6 done. |
| **Log shard to append to** | `docs/prompt-log/01-tasks-1.1-1.2.md` — entries 7–12 |
| **Next entry number** | 13 |
| **Context stage** | **Stage 2 — Routes. Context level not yet chosen; it is the user's call and must be argued from size or coupling.** Stage 1 used whole-repo (`backend/`, 587 lines) and is recorded in `SYSTEM_MODEL.md` § Context Strategy. |

**Task 1.1 is staged by section of the deliverable**, one context decision each — the user's
restructuring in entry 8, because one rationale cannot honestly cover six different questions:
1. Architecture ✅ · 2. Routes ← *next* · 3. Data flow · 4. Prompt/collection relationship ·
5. Storage layer + limitations · 6. External dependencies.

**Done:** setup. Working protocol agreed, `CLAUDE.md` written, prompt log opened and sharded.
Task 1.1 stage 1 — `docs/SYSTEM_MODEL.md` § Architecture (1.1 what it is, 1.2 components, 1.3 how
they fit, 1.4 characteristics) and the § Context Strategy stage-1 row.

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

**Pending at the end:** merge the log shards into `docs/prompt-log.md` (see
`docs/prompt-log/README.md`). That file is currently empty on purpose — until the merge commit exists,
the graded deliverable does not.

---

## Context

AIE 500 / PromptLab, Module 1, Competency C1 — *Codebase Comprehension & AI-Assisted Debugging*.
Source of truth for requirements: `1785592803-Module_1_Project_Brownfield_Challenge.pdf` (repo root).

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

### 6. Commit messages are graded

Meaningful, specific commit messages. One logical change per commit.

## Work order

Progress lives in CURRENT STATE at the top of this file, not here.

1. Protocol setup — `CLAUDE.md` and the prompt log opened. ← *before any code is read*
2. Task 1.1 / 1.2 — staged exploration → `docs/SYSTEM_MODEL.md` (incl. context strategy).
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
