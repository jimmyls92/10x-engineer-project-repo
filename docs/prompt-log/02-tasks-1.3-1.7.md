# Prompt log — shard 02

**Covers:** Tasks 1.3–1.7 — Bug #1 (404), Bug #2 (`updated_at` on PUT), Bug #3 (sorting), Bug #4
(orphaned prompts), and `PATCH /prompts/{id}`.

**Entries 41 onwards.** Numbering continues from `01-tasks-1.1-1.2.md`, which closed at entry 40.
Written live, entry by entry, before or alongside the change it describes. See `README.md` in this
directory for the shard table and the merge procedure.

---

## Entry 41 — Task 1.3 opened; baseline before fix

**Task:** 1.3 — Bug #1, `GET /prompts/{id}` returns 500 instead of 404.

**Prompt sent:**

> no its fine, keep it and move on to task 1.3

(The first clause settles the previous turn: the FastAPI pin-divergence paragraph written into §6.1
without a step of its own stays as written. See entry 40.)

**What came back:** not a fix. The bug site was located and the step was framed as *establish the
baseline first*, with three scopes offered:

| Scope | What it runs | What it buys |
|---|---|---|
| A | the one provided test, `test_get_prompt_not_found` | the exact failure this task owes a fix for, and nothing else |
| B | the whole suite | the before-picture of all four bugs at once, so C1.4's "nothing previously working broken" has a recorded starting point |
| C | no baseline — fix straight away | speed, at the cost of no evidence the test failed before it passed |

Facts established while framing the step, cited rather than re-derived:

- The bug is `api.py:70-72`. `storage.get_prompt` returns `Optional[Prompt]`, and `if prompt.id:`
  dereferences before guarding — the one place in the file where that happens (§2.3 of the system
  model).
- There is a **second** defect in the same handler, independent of the 500: if the guard is ever
  falsy, the function falls off the end and returns `None` against a `response_model=Prompt`.
- The provided test is `tests/test_api.py:61-69` and asserts `404`.
- Known trap, already recorded: `TestClient` defaults to `raise_server_exceptions=True`, so the
  failure will surface as a raised `AttributeError`, not as an assertion against a 500 response.

**Why my next prompt changed:**

Pending — awaiting the choice of baseline scope.

---

## Entry 42 — Baseline recorded: 3 failed, 10 passed

**Task:** 1.3, baseline step.

**Prompt sent:**

> lets go with B

**What came back:** `python -m pytest tests/ -v` before any change. **3 failed, 10 passed.**

| Test | Result | Reads on |
|---|---|---|
| `test_health_check` | PASSED | |
| `test_create_prompt` | PASSED | |
| `test_list_prompts_empty` | PASSED | |
| `test_list_prompts_with_data` | PASSED | |
| `test_get_prompt_success` | PASSED | |
| `test_get_prompt_not_found` | **FAILED** — `AttributeError` at `app/api.py:73` | Bug #1 |
| `test_delete_prompt` | **FAILED** — `AttributeError` at `app/api.py:73` | Bug #1 |
| `test_update_prompt` | PASSED | |
| `test_sorting_order` | **FAILED** — `assert 'First' == 'Second'` | Bug #3 |
| `test_create_collection` | PASSED | |
| `test_list_collections` | PASSED | |
| `test_get_collection_not_found` | PASSED | |
| `test_delete_collection_with_prompts` | PASSED | |

**Three things the whole-suite scope bought that scope A would not have:**

1. **Bug #1 breaks two tests, not one.** `test_delete_prompt` fails at the same `api.py:73` — after
   deleting, it re-fetches and expects `404` or `500` (`test_api.py:83`), and the handler raises before
   either can be returned. The task owes a fix that turns both green.
2. **The trap held.** Both Bug #1 failures are a raised `AttributeError`, not a `500` response, exactly
   as `raise_server_exceptions=True` predicted. Nothing had to be discovered the hard way.
3. **Bugs #2 and #4 have no failing test.** `test_update_prompt` passes with the `updated_at` bug
   present, and `test_delete_collection_with_prompts` passes *because* it asserts the orphaning
   behaviour. Those two tasks will have to bring their own test; Bug #1 and Bug #3 have one provided.

This is the recorded starting point C1.4's "nothing previously working broken" is measured against:
**the ten passing tests above must still pass at the end.**

**Why my next prompt changed:**

Pending — the baseline is evidence, not a fix. The next prompt settles the shape of the fix.

---

## Entry 43 — Fix applied in shape A; suite goes 3 failed → 1 failed

**Task:** 1.3, fix step. Preceded by entry 42a below — a correction I had to make before the choice
could be made honestly.

**Prompt sent:**

> If I undestand correctly C would create another Bug, right?

**What came back — a correction of my own previous message.** I had listed, against option C (push the
404 into `storage.py`), that it "would break `create_prompt`'s 400 path". That was **wrong**:
`create_prompt` calls `storage.get_collection` (`api.py:81`), not `get_prompt`. `get_prompt` has exactly
two callers, `api.py:70` and `api.py:91`, and both want a 404 on a miss — so C would not have produced
a wrong response at all.

The honest objection to C is **layering, not correctness**: `storage.py` imports only `typing` and
`app.models` (`storage.py:7-8`), so raising `HTTPException` there would make a layer that knows nothing
about HTTP unusable outside an HTTP app, contradict the `Optional[Prompt]` contract recorded in §5.2,
and leave no way for a future caller to *ask* whether a prompt exists without catching an exception.

*Flagged for C1.5: this is a wrong AI claim, caught by checking the call sites rather than trusting the
summary. Candidate for `docs/ai-verification-note.md`.*

**Prompt sent:**

> Lets go for A, then

**What came back — the fix.** `api.py:66-73` reduced to the idiom `get_collection` already uses at
`api.py:137-140`:

```python
@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
```

Both defects go at once: the dereference is gone because the guard now precedes it, and the
fall-off-the-end `None` against `response_model=Prompt` is gone because the early raise leaves only one
exit. The detail string matches `delete_prompt` (`api.py:123`), so the two prompt 404s read alike. The
three BUG comments were removed with the bug — leaving them would describe code that no longer exists.

**Suite after the fix: 1 failed, 12 passed** (from 3 failed, 10 passed).

- `test_get_prompt_not_found` — PASSED
- `test_delete_prompt` — PASSED
- `test_sorting_order` — still FAILED; that is Bug #3, Task 1.5, and untouched here
- All ten tests passing at baseline still pass. C1.4's "nothing previously working broken" holds so far.

**Why my next prompt changed:**

Pending — the provided test is green, but the work order says each fix carries a test of its own, so
the next prompt settles whether one is owed here and what it should assert.

---

## Entry 44 — The test obligation was checked against the brief, and my version of it was wrong

**Task:** 1.3, closing step.

**Prompt sent:**

> My understanding from the document is that we do not have to provide any further test, wouldnt you
> agree? Rereade the document to answer this question

**Why this prompt matters (C1.3 — added a constraint).** I had just been offered three angles for an
*additional* test. The prompt refused the frame and sent me back to the source instead: the constraint
added is "answer from the brief, not from your own summary of it."

**What came back — agreement, and the reason it had been got wrong.** The "each fix carries a test"
line came from `CLAUDE.md`'s work order, which I had written, not from the brief. The brief is per-task
and deliberately uneven:

| Task | The brief's own words | Test owed? |
|---|---|---|
| Bug #1 | "fix it to return a proper 404, and **make the provided test pass**" (line 57) | **No** |
| Bug #2 | "**verify with a test**" (line 60) | Yes |
| Bug #3 | "fix the order, **verify**" (line 63) | Not as a test; one is provided |
| Bug #4 | "implement it, and **add a test**" (line 66) | Yes, explicitly |
| PATCH | four behaviour checkboxes, no test wording (67–71) | No |

And C1.4's evidence line asks that "all **provided** tests pass and nothing that worked before is
broken" (line 186) — it never asks for tests the student wrote.

So Task 1.3 owes no further test. The provided `test_get_prompt_not_found` is green and the ten
baseline passes are intact.

**Prompt sent:**

> Lets go for 1 and 2 in the same commit

**What came back:** `CLAUDE.md` corrected in the same commit as the fix — the work order now carries
the per-task wording above instead of "each with a test", a Known Trap records the distinction so it is
not re-litigated at Task 1.5, and CURRENT STATE moves to Task 1.4.

**Why my next prompt changed:**

Task 1.3 is closed. The next prompt opens Task 1.4 — Bug #2, `updated_at` unchanged on PUT — which is
the first task that does owe a test of its own.
