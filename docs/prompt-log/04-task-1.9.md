# Prompt log — Task 1.9 (document what you rescued)

Shard 4 of the working log. Covers the C1.6 deliverables: Google-style docstrings on every function
modified or added in this module, and a README section whose run steps work on a clean clone. Entries
run from 76; shard `03` closed at 75.

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
