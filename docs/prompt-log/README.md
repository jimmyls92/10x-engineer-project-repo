# Working prompt-log shards

**The graded deliverable is `docs/prompt-log.md`** (one file up). These are the working originals it
is assembled from.

The log is written live, one shard per task from the module brief, and each shard is committed as it
is written rather than at the end. That is deliberate: the brief states the prompt log "cannot be
convincingly reconstructed afterwards", so the commit history of this directory is the evidence that
it was not — each shard lands before or alongside the code change it describes.

Sharding also keeps the working context small. Later tasks load one short file instead of the whole
history.

## Shards

| File | Covers | Status |
|---|---|---|
| `00-setup.md` | Protocol setup, and one discarded first attempt at Tasks 1.1–1.2 | Complete — entries 1–6 |
| `01-tasks-1.1-1.2.md` | Task 1.1 exploration (all six sections + context strategy) | Complete — entries 7–40 |
| `02-tasks-1.3-1.7.md` | Bugs #1–#4 and `PATCH /prompts/{id}` | Complete — entries 41–73 |
| `03-task-1.8.md` | AI-verification note | Complete — entries 74–75 |
| `04-task-1.9.md` | Docstrings, the README, and the corrections the clean-clone test forced | Complete — entries 76–88 |

Entry numbering is continuous across shards, so the merge is a concatenation in filename order.

The filename keeps both task numbers because the shard is simultaneously the record of the Task 1.1
exploration and the Task 1.2 deliverable itself — every entry here *is* prompt-log content. The
context strategy section belongs to Task 1.1, not to Task 1.2; the earlier wording had that wrong.

A shard is split further if it grows large enough to be awkward to load (`02` is the likely
candidate — five items). Splits keep the numeric prefix and add a suffix, e.g. `02a-`, `02b-`.

## Merge

Once, after Task 1.9, as its own commit: concatenate in filename order under a single heading, drop
the per-shard front matter, write to `docs/prompt-log.md`. The shards stay in place afterwards.
