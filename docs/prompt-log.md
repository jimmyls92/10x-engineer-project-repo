# Prompt log — Module 4

Written live, one entry per prompt, in the order sent. Module 3's log (entries 1-480) is on branch
`Week-3` (`83852ee`). Entries 1-5 were written together with entry 6, because this file was only
cleared at that prompt; they record prompts sent earlier in the same session, verbatim.

---

## Set-up — `Week-4` branch, Module 4 brief and log

### Entry 1

**Prompt**

> create a new branch week-4 and erase the content in prompt-log

**What came back**

Claude acted on nothing. It found an uncommitted Module 3 entry (480) in `docs/prompt-log.md` on
`Week-3`, which erasing the file on a new branch would have destroyed with no copy anywhere. It
proposed an order: commit entry 480 on `Week-3`, create `Week-4` (capital W, matching `Week-2` and
`Week-3`), then empty the log. It showed the commit message and asked whether to also push `Week-3`.

**Why the next prompt changed**

I moved on to the Module 4 brief before answering.

### Entry 2

**Prompt**

> create the new brief.txt form @Module_4_Project_Full_Stack_Frontend.pdf and then commit

**What came back**

Claude started by checking the branch and whether `brief.txt` was tracked; I rejected that command.

**Why the next prompt changed**

I interrupted to answer the question still pending from entry 1.

### Entry 3

**Prompt**

> [Request interrupted by user for tool use]
> yes

**What came back**

Claude read the "yes" as approval of the entry-480 commit. It committed it on `Week-3` as `83852ee`
("Log the no-op push that closed Module 3"), did not push, and created `Week-4` from there. It
regenerated `brief.txt` from `Module_4_Project_Full_Stack_Frontend.pdf` with the PyMuPDF command in
`CLAUDE.md`: 225 lines, Tasks 4.1-4.8 (frontend spec, second spec feature by TDD, React project,
components, API integration, full CRUD flow, UX polish, deployment), What You Submit, Verification
and the criteria. It proposed the commit message for `brief.txt` and stopped.

**Why the next prompt changed**

I wanted `Week-3` pushed before anything else on `Week-4`.

### Entry 4

**Prompt**

> first thing is pushing week-3 and then creating week-4 branch

**What came back**

Claude pushed `Week-3` (`dd82236..83852ee`). `Week-4` already pointed at `83852ee`, the pushed head,
so it was not recreated; it is local only. `brief.txt` was still uncommitted.

**Why the next prompt changed**

Good enough; I approved the `brief.txt` commit.

### Entry 5

**Prompt**

> yes

**What came back**

Claude committed `brief.txt` on `Week-4` as `88f9ed3` ("Replace the brief with Module 4's") and asked
to empty the log and write this first entry.

**Why the next prompt changed**

Good enough; I approved clearing the log.

### Entry 6

**Prompt**

> yes

**What came back**

Claude replaced Module 3's log with this file, recording entries 1-6 of Module 4, and proposed the
commit message "Start the Module 4 prompt log".

**Why the next prompt changed**

Good enough; I approved the commit.

### Entry 7

**Prompt**

> yes

**What came back**

Claude committed this log on `Week-4` ("Start the Module 4 prompt log"), with this entry in it. Next
step: update CURRENT STATE in `CLAUDE.md` for Module 4. It proposed the new rows (Module 4 on
`Week-4`, Module 3 closed at `83852ee`, Task 4.1 next) and asked for permission.

**Why the next prompt changed**

I approved the edit and **added a constraint** on the teaching method.

### Entry 8

**Prompt**

> yes. Regarding the teaching method (rule 0b), dont enter into the specificities of the code, guide me on deciding the functional part but dont enter into code specificities unless a decision on how we write the code impacts the functional. Try to stay as high level as possible with your questions, making me decide only in things that have an impact and not on tirival things.

**What came back**

Claude updated `CLAUDE.md`. CURRENT STATE: Module 4 on `Week-4`, Module 3 closed at `83852ee`, current
task Task 4.1 (not started), next entry 9. Rule 0b: the bullet "ask only about coding and spec-driven
development" became "ask only about decisions with a functional impact, as high level as possible";
code-level and trivial choices are decided by Claude and stated as settled, unless they change the
functional result. The "size the question" bullet no longer splits into the smallest piece, only into
separate functional decisions. Uncommitted; it proposed two commits, one for the rule and one for
the state.

**Why the next prompt changed**

I approved both and **added a constraint**: the low-level decisions Claude settles still need my
confirmation, with the reasons.

### Entry 9

**Prompt**

> yes, only add one thing, the low level decisions that you made between functional/high level decissions, require my confirmation, and explanation on why, and why other choices where discarted

**What came back**

Claude's first reply to this prompt was stopped by a safety classifier and withheld; nothing in it
ran. On the retry, Claude added a bullet to Rule 0b: before the next functional question, Claude
lists the code-level choices it made since the last one, each with why it was chosen and why the
alternatives were discarded, and waits for a yes. It then made the two approved commits, the rule
change first, then the state with this log; CURRENT STATE gives 10 as the next entry.

**Why the next prompt changed**

Pending.
