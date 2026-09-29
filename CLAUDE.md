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
| **Current module** | **Module 2** — branch `Week-2`. Brief: `brief.txt`, from `Module_2_Project_Spec_Driven_Development.pdf`. |
| **Current task** | **Task 2.3 — API reference → `docs/API_REFERENCE.md`: COMPLETE.** All 11 endpoints, with a curl example, a real sample response and an error table for each; errors, response formats and authentication notes in shared sections. Every example was run against a live server, and a script re-runs them all on a fresh one (11/11). A fresh-context review found no false claims and 6 gaps, all fixed (log entries 42-51). **Then the PATCH-null fix (entries 53-71):** fixed on `main` (`158eb0b`, pushed), merged into `Week-2` (`971a6cc`), and Tasks 2.1-2.3 updated to match after a fresh-context sweep against the brief. **Next: Task 2.4 — Custom AI agent. Not started.** |
| **Log file to append to** | `docs/prompt-log.md` |
| **Next entry number** | 72 |

**Open decisions:**

- *None yet.*

**Known traps:**

- **`README.md` and `docs/API_REFERENCE.md` list every endpoint.** Any endpoint added later (Module
  3's feature) must also go into the README's Features list and API endpoint summary, and get its own
  section in the API reference (curl example, sample response, errors), or C2.2 fails at Module 3.
- **Two deprecation warnings in `models.py`** (seen in entry 22): the class-based `Config` blocks
  (`models.py:56`, `:75`) and `datetime.utcnow()` (`models.py:14`). No Module 2 task covers them;
  docstrings describe them as they are.
- **`Storage.update_prompt` does not check that `prompt.id` equals `prompt_id`** (entry 30,
  `storage.py:66`). Unreachable today, since PUT and PATCH copy `existing.id` (`api.py:128`, `:178`);
  any new code that replaces a prompt must do the same.
- **An empty-string `collection_id` is handled inconsistently** (entry 37). POST and PUT store `""`
  unchecked (`api.py:86`, `:122` test truthiness); PATCH looks it up and returns 400 (`api.py:172`,
  `is not None`). The docstrings describe it; any spec or doc touching `collection_id` must too.
  A consequence (entry 50): `GET /prompts?collection_id=` ignores the empty value (`api.py:87`), so
  prompts stored with `""` cannot be listed by collection. Stated in the API reference's Known issues.
- **`PATCH` rejects a null `title` or `content` with 422** (fixed in `158eb0b`, entries 53-71;
  `reject_null` in `models.py`). It runs while the body is validated, **before** the 404 and 400
  lookups, so `PATCH /prompts/nope` with `{"title": null}` is 422, not 404. Any doc that lists PATCH
  errors or the order of checks must say so (README, `API_REFERENCE.md`, the `patch_prompt` and
  `PromptPatch` docstrings do). `/openapi.json` still shows both fields as nullable.

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

Break every task into small steps — typically 3 to 6. Before each step:

1. **Explain the decision**: what this step should achieve, and why it comes now rather than later.
2. **Lay out the options** — typically 2–3 — and what follows from each.
3. **Give a recommendation**, and say why.
4. **Stop. Wait for their prompt.** They write it — you do not draft it for them. Choosing the option
   and phrasing the prompt is the skill being practised.
5. Act on what they actually sent, then log the entry, then propose the next step.

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

## Verification command

The provided tests must pass in every module:

```
cd backend
pytest tests/ -v
```

Each module's brief adds its own verification steps.
