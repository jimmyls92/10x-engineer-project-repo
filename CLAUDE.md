# CLAUDE.md — PromptLab Module 1 (Brownfield Challenge)

Working protocol for this repository. Read this before doing anything else in a new session.

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

### 1. Prompt log is written live, never reconstructed

After **every** user prompt in this repo, append an entry to `docs/prompt-log.md` before or alongside
doing the work. An entry contains:

- **Prompt** — the user's message, verbatim.
- **What came back** — summary of the response; paste the relevant part.
- **Why the next prompt changed** — one line. If the output was good enough, say so.

Write entries in the user's first-person voice — he is the one prompting. Never invent a prompt that
was not actually sent. Never backfill a gap by guessing; if an entry is missing, mark it as missing.

Flag explicitly in the entry whenever an iteration **narrowed context, added a constraint, or
restructured** the prompt — those are the C1.3 evidence points.

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

1. Protocol setup — `CLAUDE.md`, `docs/prompt-log.md` opened. ← *before any code is read*
2. Task 1.1 / 1.2 — staged exploration → `docs/SYSTEM_MODEL.md` (incl. context strategy).
3. Tasks 1.3–1.7 — 4 bug fixes + `PATCH /prompts/{id}`, each with a test.
4. Task 1.8 — `docs/ai-verification-note.md`.
5. Task 1.9 — docstrings on touched functions + README run instructions.
6. Verify: `cd backend && pytest tests/ -v`, then clone to a fresh directory and follow the README.

## Verification command

```
cd backend
pytest tests/ -v
```
