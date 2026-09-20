# AI verification note

**Criterion C1.5.** Three specific instances of wrong AI output produced during this module: what the
AI produced, why it was wrong, how it was detected, and what was done instead. Each is traceable to a
numbered entry in the prompt log.

None of the three is a syntax error, and none would have been caught by an editor, a type checker or
the test suite — all three read as authoritative and all three were false. They are given in the order
they happened, because the second is a repeat of the first and that only shows in sequence.

---

## Case 1 — "the only route that doesn't test the storage result"

**Where to find it:** prompt log **entry 16**, "Catching an over-broad claim: `list_prompts` doesn't
have that pattern either" (`docs/prompt-log.md`; working shard `docs/prompt-log/01-tasks-1.1-1.2.md`,
lines 390-424). Task 1.1, exploration stage 2 — *Entry points*. The claim was destined for
`docs/SYSTEM_MODEL.md` § Entry points.

**What the AI produced.** Asked to characterise the 404 discipline across the route surface, it
stated:

> `GET /prompts/{prompt_id}` is the **only** route that doesn't test the storage result for falsiness
> before using it.

**Why it was wrong.** Two defects, one visible and one structural.

- *False as stated.* `list_prompts` takes `storage.get_all_prompts()` at `api.py:48` and uses it at
  `api.py:52`, `:56` and `:60` with no falsiness test at all. "Only" was therefore false on the route
  immediately above the one being described.
- *Wrong category.* The property was attributed to **routes** when it belongs to **return types**.
  `get_all_prompts()` and `get_all_collections()` return `List[...]`, never `None`: there is nothing
  to guard, and an empty list is a valid answer meaning "nothing matched", so a falsiness check there
  would itself be a bug, firing on the normal empty case. `get_prompt()` and `get_collection()` return
  `Optional[...]`, where `None` *is* the miss and the caller must separate the two cases before use.
  The original sentence made the two look like the same omission.

**How I detected it.** By reading `api.py` and naming the counter-example rather than accepting the
summary — the prompt sent was *"ok, but list_prompts also does not have this pattern"*. Nothing in the
tooling flagged it: the sentence was prose about code, not code, and the suite was green.

**What I did instead.** I made the model re-derive the claim across all ten declared routes instead of
generalising from the two it had looked at, and re-scope it by return type. The version that went into
`SYSTEM_MODEL.md`:

> Among the routes that call an `Optional`-returning getter and then use the result,
> `GET /prompts/{prompt_id}` is the only one that reaches inside the result before guarding it.

The re-derivation also turned up something the original framing would have hidden:
`PUT /prompts/{prompt_id}` returns `storage.update_prompt(...)` at `api.py:113` unchecked, and that
getter is `Optional[Prompt]` too. It is safe only because existence was established upstream at
`api.py:91-93` — safe by context, not by its own shape. That observation exists only because the wrong
claim was challenged.

---

## Case 2 — "the only field in the whole schema with no `Field(...)` constraint"

**Where to find it:** prompt log **entry 25**, "A second unverified 'only', caught the same way as
entry 16" (`docs/prompt-log.md`; working shard `docs/prompt-log/01-tasks-1.1-1.2.md`, lines 804-830).
Task 1.1, exploration stage 4 — *Models and relationships*.

**What the AI produced.** Describing `collection_id`:

> It is the **only** field in the whole schema with no `Field(...)` constraint — a bare
> `Optional[str]`. Not a foreign key; the model layer knows nothing about collections.

**Why it was wrong.** The second clause is correct and load-bearing; the first is false. `PromptList`,
`CollectionList` and `HealthResponse` declare their fields with no `Field(...)` either
(`models.py:64-76`). "The whole schema" was never enumerated — the sentence was generalised from the
input models alone, and the response models were quietly excluded without saying so.

**How I detected it.** By challenging the sentence directly rather than absorbing it: *"It is the only
field in the whole schema with no Field(...) constraint ... what do you mean by this?"* The question
was about meaning, not about correctness, and the falsehood surfaced because the model had to name the
set it was quantifying over in order to answer.

**What I did instead.** Narrowed the claim to the set it was actually about — of the **six fields a
client can supply**, `collection_id` is the only one carrying no constraint, every other one declaring
limits at `models.py:20-22,46-47`. That is the version in `SYSTEM_MODEL.md` § Models and
relationships. The "not a foreign key" half was kept and sharpened: a database engine enforces a
foreign key continuously and also constrains the parent's deletion, whereas Pydantic validates one
object in isolation and cannot see stored collections — which is precisely why the check has to live
in a handler, and why Bug #4 exists at all.

**This is the same failure as case 1, one stage later:** an "only" quantifier asserted over a set that
had not been enumerated. Case 1 was about routes, this one about fields, and both were caught by me
rather than by the model.

---

## Case 3 — "pushing the 404 into `storage.py` would break `create_prompt`'s 400 path"

**Where to find it:** prompt log **entry 43**, "Fix applied in shape A; suite goes 3 failed → 1 failed"
(`docs/prompt-log.md`; working shard `docs/prompt-log/02-tasks-1.3-1.7.md`, lines 95-115). Task 1.3,
Bug #1 — the missing 404 on `GET /prompts/{prompt_id}`.

**What the AI produced.** Three fix shapes were offered for Bug #1. Against option C — move the 404
out of the handler and raise it inside `storage.get_prompt` — the objection listed was:

> It would break `create_prompt`'s 400 path.

**Why it was wrong.** `create_prompt` calls `storage.get_collection` (`api.py:81`), not
`storage.get_prompt`. Changing `get_prompt` cannot affect it. `get_prompt` has exactly two callers,
`api.py:70` and `api.py:91`, and **both** want a 404 on a miss — so option C would not have produced a
single wrong response anywhere in the application. The objection invented a coupling between two
functions that never touch, and it was the most concrete-sounding reason on the list: it named a
function, a status code and a consequence.

This is the most dangerous of the three, because it was steering a decision. A wrong reason attached
to a defensible conclusion survives review, since the conclusion looks right.

**How I detected it.** By asking the objection to be justified rather than banking it — *"If I
understand correctly C would create another Bug, right?"* — and then having the call sites of
`get_prompt` enumerated with `grep` instead of recalled. Two call sites, both wanting 404; the claimed
third did not exist.

**What I did instead.** I kept the decision and threw away the reason. Option C is rejected on
**layering, not correctness**: `storage.py` imports only `typing` and `app.models` (`storage.py:7-8`),
so raising `HTTPException` there would make a storage layer that knows nothing about HTTP unusable
outside an HTTP application, would contradict the `Optional[Prompt]` contract recorded in
`SYSTEM_MODEL.md` §5.2, and would leave no way for a future caller to *ask* whether a prompt exists
without catching an exception. Option A was then applied at `api.py:66-73`, and the suite went from
3 failed / 10 passed to 1 failed / 12 passed.

---

## What the three have in common

All three are the same error with different subjects: **a claim about a set, asserted without
enumerating the set.** Cases 1 and 2 assert "only" over routes and over fields; case 3 asserts a
relationship between `get_prompt` and `create_prompt` without looking at who calls what. In every
instance the enumeration was cheap — ten routes, six fields, two call sites — and in every instance it
was skipped in favour of a sentence that read well.

Three properties they share, which is what makes them worth documenting rather than just fixing:

1. **They looked right.** No syntax error, no type error, no failing test. Cases 1 and 2 were prose
   about code that a reader without the file open would have believed; case 3 named a function and a
   status code, which is exactly what a trustworthy answer looks like.
2. **The detection was always the same move** — name a counter-example, or make the model enumerate
   the set it is quantifying over. *"list_prompts also does not have this pattern"*, *"what do you mean
   by this?"*, *"would C create another Bug?"*. None required expertise the codebase didn't supply;
   they required not accepting the first answer.
3. **Correcting them produced findings the wrong version had hidden.** Case 1 surfaced the unchecked
   `Optional` return at `api.py:113`; case 2 separated model-layer validation from handler-layer
   integrity, which is the frame Bug #4 is reasoned in; case 3 replaced a fake correctness argument
   with the layering argument that actually governs where an `HTTPException` belongs. The corrected
   claim was in each case more useful than the original would have been if it had happened to be true.

Two further instances were caught the same way and are recorded in the log rather than written up
here: **entry 33**, where a storage limitation was called "unreachable" and the word did not survive
the chain being traced instead of asserted; and **entry 54**, where `list_prompts` was said to declare
`sort_by` and `descending` query parameters, which do not exist — `descending=True` is a literal at the
call site (`api.py:60`), so the client-facing default the sentence worried about could not occur.
