# AI verification note

**Criterion C1.5.** Four specific instances of wrong AI output produced during this module: what the
AI produced, why it was wrong, how it was detected, and what was done instead. Each is traceable to a
numbered entry in the prompt log.

None of the four is a syntax error, and none would have been caught by an editor, a type checker or
the test suite — all four read as authoritative and all four were false. They are given in the order
they happened, because the second is a repeat of the first and that only shows in sequence, and
because the fourth was not caught until the last task of the module, having survived every review in
between.

Cases 1 to 3 share one failure mode; **case 4 is a different one**, and the closing section treats
them separately rather than forcing them together.

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

## Case 4 — "a directory run in place by `python main.py`"

**Where to find it:** prompt log **entries 85 and 86** (`docs/prompt-log.md`; working shard
`docs/prompt-log/04-task-1.9.md`). Task 1.9 — the README run steps. The claim itself is older: it was
written during Task 1.1, exploration stages 1 and 6, and shipped in `docs/SYSTEM_MODEL.md`.

**What the AI produced.** Four separate statements, across two sections of a deliverable that was
recorded as finished:

> It runs as a single process with a single entrypoint (`main.py:6-10`). — §1.1
>
> `main.py` — Process entrypoint. Imports the app and hands it to uvicorn on port 8000
> (`main.py:7,10`). Holds no logic. — §1.2
>
> `uvicorn` — ASGI server. Called once, at `main.py:10`. — §6.1
>
> The service … is a directory run in place by `python main.py` (`main.py:3`). — §6.5

**Why it was wrong.** `python main.py` does not start a server. `main.py:10` passes the imported `app`
*object* together with `reload=True`, and uvicorn accepts `reload` only for an application given as an
import string. It prints `WARNING: You must pass the application as an import string to enable
'reload' or 'workers'.` and exits without binding a port — status 1 on the pinned stack
(uvicorn 0.27.0, Python 3.12.13), status 3 on the environment the document was written in
(uvicorn 0.52.4, Python 3.13.14).

The interesting part is not that the claim was false but **how it was corroborated**. The §6.5
sentence cites `main.py:3` as its evidence. `main.py:3` is the module docstring, and it reads
`Run with: python main.py`. The document established how the service runs by quoting the code's own
claim about how it runs. Both are wrong, and they agree with each other, which is precisely why
neither looked suspicious — a citation was present, and it checked out.

Nothing else in the repository contradicts it. The test suite reaches the application through
`TestClient`, which imports `app.api:app` directly and never executes `main.py`: a fully green suite
and a service that cannot be started by its own documented command are compatible states. Seventeen
passing tests carried no information about this at all.

**How I detected it.** Not by reading. The README's run steps were **executed on a clean clone** — a
tree built with `git archive HEAD`, with no `.git`, no virtual environment and no build cache —
because the brief says C1.6 is checked that way, so the steps had to be run rather than reviewed. The
install step failed first, for an unrelated reason (no `pydantic-core` wheel for Python 3.13), and
only once that was cleared by fetching a 3.12 did the run step get reached at all. It failed
immediately.

This case is the one that best justifies the whole exercise: the claim had been read and approved
several times, carried a line citation, and was consistent with every other document in the
repository.

**What I did instead.** The four statements were corrected in place, and §6.1 gained a paragraph
recording the defect with both measured exit statuses and the reason the suite cannot see it. The
README now documents `uvicorn app.api:app --reload`, the command that works, with `python main.py`
named in *Known issues* as broken rather than quietly dropped — the module was not asked to change
that file, and an unfixed defect that is documented is not a hidden one.

One correction produced a finding of its own. §6.5 had said that `pydantic==2.5.3` "will not build on
an interpreter far from the one it was released for", labelling it explicitly as "an inference from
the pin, not a statement the repository makes". The inference was sound and is now **measured**: the
install fails on Python 3.13 and succeeds on 3.12.13. The repository has an undeclared upper bound on
its interpreter, and that bound excludes the current release of Python.

It is also worth recording what the document already had right. §6.1 contained the sentence "served by
any external ASGI runner pointed at `app.api:app`, the service never touches uvicorn at all" — the
only accurate description of how to start the service anywhere in the repository, written to make a
point about dependency coupling and never connected to the run instructions three sections away.

---

## What the four have in common

**Two failure modes, not one.** Cases 1 to 3 are a single error with different subjects; case 4 is a
different error that the first three would not have predicted. Forcing all four under one heading
would be the same over-generalisation this note is about, so they are kept apart.

### Mode 1 — a claim about a set, asserted without enumerating the set (cases 1, 2, 3)

All three are the same error with different subjects: **a claim about a set, asserted without
enumerating the set.** Cases 1 and 2 assert "only" over routes and over fields; case 3 asserts a
relationship between `get_prompt` and `create_prompt` without looking at who calls what. In every
instance the enumeration was cheap — ten routes, six fields, two call sites — and in every instance it
was skipped in favour of a sentence that read well.

### Mode 2 — a self-description read instead of executed (case 4)

Case 4 quantifies over nothing and generalises from nothing. The claim is specific, it names a file and
a line, and the line it names **supports it**. It is wrong because `main.py` describes itself
incorrectly and that description was read rather than run.

The two modes fail differently and are caught differently:

| | Mode 1 | Mode 2 |
|---|---|---|
| The claim | Quantified — "the only", "always", "would break" | Specific, and cited |
| Why it is wrong | The set was never enumerated | The behaviour was never executed |
| What the source says | Contradicts it, if you look | **Agrees with it** — the docstring repeats the same false thing |
| The cheap check that catches it | `grep`, or one counter-example | Run the command |
| How long it survived | Caught inside the same exchange | Four tasks and several reviews, until the last one |

Mode 2 is the more dangerous of the two, and the survival time is why. A mode 1 error is refuted by
the source, so any reader who opens the file can catch it. A mode 2 error is *confirmed* by the
source, so reading more carefully makes it look better rather than worse. Nothing short of execution
separates "documented" from "true".

### Four properties they share

1. **They looked right.** No syntax error, no type error, no failing test. Cases 1 and 2 were prose
   about code that a reader without the file open would have believed; case 3 named a function and a
   status code, which is exactly what a trustworthy answer looks like.
2. **Detection never needed expertise the codebase didn't supply** — only a refusal to accept the
   first answer. For mode 1 the move is to name a counter-example or force an enumeration:
   *"list_prompts also does not have this pattern"*, *"what do you mean by this?"*, *"would C create
   another Bug?"*. For mode 2 no question would have worked, because the document and the code agreed
   with each other; the move is to stop asking and run it.
3. **Correcting them produced findings the wrong version had hidden.** Case 1 surfaced the unchecked
   `Optional` return at `api.py:113`; case 2 separated model-layer validation from handler-layer
   integrity, which is the frame Bug #4 is reasoned in; case 3 replaced a fake correctness argument
   with the layering argument that actually governs where an `HTTPException` belongs; case 4 turned an
   explicitly labelled inference about the interpreter bound into a measured fact, and produced a
   README *Known issues* section that would otherwise not exist. The corrected claim was in each case
   more useful than the original would have been if it had happened to be true.
4. **None of them was caught by tooling.** The suite was green throughout all four. Case 4 makes the
   point sharpest: seventeen passing tests and a service that will not start are not in conflict,
   because the tests import the application directly and the broken file is never executed. A test
   suite verifies what it imports, not what the documentation claims.

Two further instances were caught the same way and are recorded in the log rather than written up
here: **entry 33**, where a storage limitation was called "unreachable" and the word did not survive
the chain being traced instead of asserted; and **entry 54**, where `list_prompts` was said to declare
`sort_by` and `descending` query parameters, which do not exist — `descending=True` is a literal at the
call site (`api.py:60`), so the client-facing default the sentence worried about could not occur.
