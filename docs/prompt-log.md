# Prompt Log — Module 1, Brownfield Challenge

Contemporaneous record of my prompting while rescuing the PromptLab backend. Entries are appended as
I work, in order. AI tool used: Claude Code (Opus 5) in the repository root.

Format per entry: the prompt I sent, what came back, and why my next prompt changed.

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

The PDF would not render through the built-in reader (no `pdftoppm` on this machine) and I declined
the suggestion to `pip install pypdf`. It fell back to a stdlib-only extraction script
(`zlib.decompress` over the PDF content streams, regex over the `Tj`/`TJ` text operators) and
recovered the full six pages.

It then summarised the six criteria as a table, correctly separating the two *process-evidence*
criteria (C1.3 prompt log, C1.5 AI-verification note) from the deliverable criteria, and flagged the
brief's warning that the prompt log "cannot be convincingly reconstructed afterwards." It stopped
before reading any source file and asked three setup questions: how the prompt log should be
captured, whether exploration should be staged deliberately, and how to handle the AI-mistake
evidence.

**Why my next prompt changed:**

Nothing was wrong with the answer — it was right to stop and ask. But I noticed the whole protocol
was living only in the chat, which does not survive a new session or a context compaction. So my next
prompt added a durability constraint rather than asking for more analysis.

---

## Entry 2 — Persist the working protocol instead of holding it in chat

**Stage:** Setup. **Context level:** none (no source files read yet — deliberate).

**Prompt sent** (answering the three setup questions):

> 1, but maybe we should wirte this reminder in some kind of CLAUDE.md, dont you think?
> 1, but again, should we remind this in a CLAUDE.md file?
> 1, should we include this rule in a CLAUDE.md file?

i.e. for all three questions I chose the first option — log written live after each exchange,
exploration staged deliberately, wait for a genuine AI mistake rather than manufacturing one — and on
each one I pushed for the rule to be written into a `CLAUDE.md` rather than left in conversation.

**What came back:**

Agreement, and `CLAUDE.md` was written at the repo root before any source file was opened. It encodes
the deliverables table, the six working rules (log live and never reconstruct; stage exploration
honestly and don't read ahead of the stage; verify every claim against source; capture AI mistakes the
moment they happen; never hide a bug; meaningful commits), the work order, and the verification
command. `docs/prompt-log.md` was opened at the same time — this file.

**Why my next prompt changed:**

Protocol is now durable and machine-read at session start, so the setup phase is closed. Next prompt
moves to Task 1.1 and starts Stage 1 exploration.

---
