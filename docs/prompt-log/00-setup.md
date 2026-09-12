# Prompt Log — 00 · Setup

Shard of the working prompt log. Merged into `docs/prompt-log.md` at the end of the module; see
`docs/prompt-log/README.md`.

**Covers:** everything before Task 1.1 proper — reading the brief, building the working protocol, and
one discarded first attempt at Task 1.1 that was thrown away and restarted.
**Entries:** 1–6. **AI tool:** Claude Code (Opus 5), run from the repository root.

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
