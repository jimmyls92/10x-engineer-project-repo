# Prompt log — Module 3

Written live, one entry per prompt, in the order sent. Module 2's log (entries 1-198) is on branch
`Week-2`. The set-up prompts that created this branch and cleared this file came before the log was
opened and are not recorded here.

---

## Set-up — Module 3 brief and `CLAUDE.md`

### Entry 1

**Prompt**

> read the pdf @Module_3_Project_Production_Ready.pdf and with tha inforamtion create brief.txt and modify as needed CLAUDE.md. Confirm the changes with me

**What came back**

Claude regenerated `brief.txt` from `Module_3_Project_Production_Ready.pdf` with the PyMuPDF command
in `CLAUDE.md` (263 lines, replacing Module 2's brief) and read it: Tasks 3.1-3.5 (test suite at 80%
coverage, one spec feature by TDD, GitHub Actions CI with gate evidence, Docker, a documented
refactor), criteria C2.4-C2.8 with C2.4 and C2.7 MUST PASS, and the final judgment of C2.1 and C2.2.
It did not edit `CLAUDE.md`. It proposed seven changes for confirmation, flagging two conflicts
between the brief and `CLAUDE.md`: the coding standard "tests go through the HTTP API ... never by
calling storage directly" against Task 3.1's `test_storage.py`, `test_utils.py` and
`test_models.py`; and the brief's `git push origin main` against delivering on `Week-3` with `main`
untouched. It stopped.

**Why the next prompt changed**

The brief is the source of truth for the module, so the next prompt settles both conflicts in its
favour and approves all seven changes.


### Entry 2

**Prompt**

> its ok with the conflicts, module_3 assigment is what rules here. Apply all seven

**What came back**

Claude applied the seven changes to `CLAUDE.md`. CURRENT STATE: Module 3 on `Week-3`, with the rule
that the brief wins over `CLAUDE.md` where they conflict; Module 2 shrunk to one row (submitted on
`Week-2`, `1c9cc88`, log entries 1-198 there); current task none, next Task 3.1; next entry
number 2. A note that entry numbers in Open decisions and Known traps refer to Module 2's log. Open
decisions: added which feature Task 3.2 implements, kept the eight deferred spec findings. Known
traps: added "never push to `main`" and running tests and lint in a pinned Python 3.12 venv.
*Testing requirements*: endpoint tests through `client`, unit tests in `test_storage.py`,
`test_utils.py` and `test_models.py` calling their module directly, grouped by class or function.
*Verification command*: added the brief's coverage command. Nothing committed.

**Why the next prompt changed**

The set-up was complete, so the next prompt asks to commit it and begin Task 3.1.


### Entry 3

**Prompt**

> commit and start with task 3.1

**What came back**

Following Rule 5, Claude showed the messages before committing, and proposed three commits rather
than one, since they are three logical changes: `brief.txt` replaced, `CLAUDE.md` updated, and the
Module 3 log opened (as Module 2's log was opened in its own commit). It said Task 3.1 starts right
after the commits, and stopped.

**Why the next prompt changed**

The three messages matched the three changes, so the next prompt approves them.


### Entry 4

**Prompt**

> yes

**What came back**

Claude ran the suite (19 passed) and committed `brief.txt` as `e2b0348` and `CLAUDE.md` as
`dc2b036`, then this log, with this entry, as the third commit. Nothing pushed.

It started Task 3.1 by re-reading it (`brief.txt:28-36`) and C2.5 (`:140-154`), and proposed the
task in steps: (1) a pinned environment and a baseline coverage run; (2) `test_models.py`;
(3) `test_utils.py`; (4) `test_storage.py`; (5) the gaps in `test_api.py`, so every endpoint in the
API reference has a success test and a documented failure test; (6) close-out. It checked the setup
first: the repo has **no `.gitignore`**, so `__pycache__` already shows as untracked, and a venv in
`backend/.venv`, where the README creates one, would too. The question for step 1: **where does the
pinned Python 3.12 venv live?** (A) `backend/.venv`, as the README says, with a `.gitignore` added
in its own commit for `.venv/`, `__pycache__/` and `.coverage`; (B) outside the repository, in a temp
folder, with no repo change. It recommended A, and stopped.

## Task 3.1 — Comprehensive test suite

**Why the next prompt changed**

*Pending.*
