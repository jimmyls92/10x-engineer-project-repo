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
| `04-task-1.9.md` | Docstrings, the README, and the corrections the clean-clone test forced | Complete — entries 76–89 |

Entry numbering is continuous across shards, so the merge is a concatenation in filename order.

The filename keeps both task numbers because the shard is simultaneously the record of the Task 1.1
exploration and the Task 1.2 deliverable itself — every entry here *is* prompt-log content. The
context strategy section belongs to Task 1.1, not to Task 1.2; the earlier wording had that wrong.

A shard is split further if it grows large enough to be awkward to load (`02` is the likely
candidate — five items). Splits keep the numeric prefix and add a suffix, e.g. `02a-`, `02b-`.

## Merge

**Done.** Run `python docs/prompt-log/merge_log.py` from the repository root; it rewrites
`docs/prompt-log.md` from these shards. It concatenates in filename order under a single heading,
drops the per-shard front matter, repairs the literal `\uXXXX` escape sequences that shard `02` was
written with, and builds the header's task map and C1.3 index from the entries themselves. It asserts
that the entry numbers it collects are continuous from 1, which is what catches a shard that has been
split or renumbered.

The shards stay in place and remain the working originals. **Never edit `docs/prompt-log.md` by
hand** — edit the shard and re-run the script.
