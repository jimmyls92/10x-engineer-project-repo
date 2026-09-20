# Prompt log — Task 1.8 (document one AI mistake)

Shard 3 of the working log. Covers `docs/ai-verification-note.md`, the C1.5 deliverable. Entries run
from 74; shard `02` closed at 73.

---

## Entry 74 — Task 1.8 opened; the candidate mistakes are counted before any is chosen

**Prompt:**

> go for task 1.8

**What came back:** no note written. Step 1 was framed as a *selection* problem rather than a writing
problem: Rule 4 says AI mistakes are captured live, and the log already carries several, so the first
question is which instance the note documents — not what to write about it.

The brief's own words for the task were re-read (`brief.txt:77-84`): "what the AI produced, why it was
wrong, how you detected it, and what you did instead", traceable to a prompt-log entry, and explicitly
**not** a syntax error an editor would flag. The last line of that section suggests a deliberate probe
(ask for the collection-deletion behaviour from memory, then check it) *if* no wrong answer was ever
hit — which is a fallback, not a requirement.

The log was then searched rather than recalled, and the candidates enumerated with their entry numbers:

| Candidate | Entry | What was wrong |
|---|---|---|
| The "only route" claim about `GET /prompts/{id}` | 16 | Stated as a property of routes; it is a property of return types. Flagged in-entry as a C1.5 candidate. |
| A second unverified "only", this time over fields | 25 | Same failure mode as 16, caught the same way — asserted over a set that had not been enumerated. |
| "Unreachable" as a description of a storage limitation | 33 | Overstated; the chain was traced instead of asserted and the word did not survive. |
| Moving the 404 into `storage.py` "would break `create_prompt`'s 400 path" | 43 | Wrong about the call sites. Flagged in-entry for C1.5. |
| "`list_prompts` declares `sort_by` and `descending` query parameters" | 54 | No such parameters exist; the framing invented a client-facing default. |

Two of these (16, 43) were already tagged for C1.5 when they happened, which is exactly the trace
C1.5 asks for.

**Why the next prompt changed:** the choice between them is mine, and it is a real trade-off — one
deeply worked instance versus a pair that shows the same failure mode recurring, versus running the
brief's suggested probe on top of the organic material. Recorded with the next prompt.

---

## Entry 75 — Three cases chosen; the four fields proposed from the log before any prose is written

**Prompts sent, in order:**

> Lets write in detail 43, 16 and 25. we should nswer what tha AI produced, why it was wrong, how I
> detect it and waht I did instead. Searching on the logs create a table with a propossal on every of
> this fields. We might have to compact the log files in order to fit them in context.

> Add to the 3 bugs the reference where they can be found. Then, write them by chronological order and
> do the clossing section adding also the other bugs in one line

**What came back.** The organic material was chosen over the brief's fallback probe — five wrong
outputs had already been caught and recorded live, so manufacturing a sixth would have been the weaker
evidence. Three were selected: **43, 16, 25**.

*Compaction turned out not to be needed.* The three entries were read by line range
(`sed -n '390,440p'`, `'804,860p'`, `'95,152p'`) rather than by loading the shards whole — about 130
lines in total against roughly 1,600 in the two files. That is the same discipline the sharding exists
for, applied one level finer.

**One table per case** was returned before any prose, each with the four fields the brief names, drawn
from the log rather than from memory:

| Case | What the AI produced | Why it was wrong |
|---|---|---|
| 16 | "`GET /prompts/{prompt_id}` is the **only** route that doesn't test the storage result for falsiness" | `list_prompts` doesn't test it either (`api.py:48,52,56,60`); and the property belongs to return types, not routes |
| 25 | "`collection_id` is the **only** field in the whole schema with no `Field(...)` constraint" | `PromptList`, `CollectionList`, `HealthResponse` have none either (`models.py:64-76`); the set was never enumerated |
| 43 | Option C "would break `create_prompt`'s 400 path" | `create_prompt` calls `get_collection` (`api.py:81`), not `get_prompt`; `get_prompt`'s two callers both want 404 |

Detection and remedy per case were proposed alongside, and the through-line was offered as an optional
closing section rather than assumed.

**Two constraints I added on the second prompt**, which is what turned the proposal into the
deliverable:

1. **Each case must carry a reference to where it can be found** — entry number, the merged
   `docs/prompt-log.md`, and the working shard with line numbers. Without that, C1.5's "traceable to
   an entry in your prompt log" rests on the reader's willingness to search.
2. **Chronological order, not strongest-first** — 16, then 25, then 43. Strongest-first would have led
   with the decision-steering error, but it would have destroyed the fact that 25 is a *repeat* of 16.
   The sequence is itself a finding.

Plus the closing section, **with the two unwritten cases named in one line each** (entries 33 and 54),
so the note shows the full count of what was caught without inflating three write-ups into five.

`docs/ai-verification-note.md` written: three cases in chronological order, each with where-to-find-it,
the four fields, and a closing section naming the shared failure mode — *a claim about a set, asserted
without enumerating the set* — the three properties that make them worth documenting, and the one-line
mentions of entries 33 and 54.

**Why the next prompt changed:** the deliverable exists; what remains is the commit, which needs its
message approved.
