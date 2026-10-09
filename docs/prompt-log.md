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
step: update CURRENT STATE in `CLAUDE.md` for Module 4.

**Why the next prompt changed**

Pending.
