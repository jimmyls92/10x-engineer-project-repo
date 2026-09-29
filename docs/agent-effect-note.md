# Agent effect note

Evidence for criterion **C2.3 — Your agent instructions do something**.

**The agent file is `CLAUDE.md`.** This project is built with Claude Code, which reads `CLAUDE.md` in
every session, so that file stands in for the `.github/copilot-instructions.md` or `.continuerules`
the brief names. The instructions Task 2.4 asks for are its section **PromptLab coding standards**,
under the brief's five headings: *Coding standards specific to this project*, *Preferred patterns and
conventions*, *File naming conventions*, *Error handling approach* and *Testing requirements*.

## How the before and after were produced

- **One task, sent word for word to every run:**

  ```
  This is a standalone exercise, separate from the course tasks in CURRENT STATE.
  Write the code directly, without proposing steps or asking for permission.
  Do not add entries to docs/prompt-log.md, do not edit CLAUDE.md, and do not commit.

  Add an endpoint to the PromptLab API, GET /collections/{collection_id}/prompts,
  that returns the prompts filed in the given collection. Add tests for it in
  backend/tests/test_api.py, then run the suite from backend/ with pytest tests/ -v.
  ```

  The first three lines are there because the rest of `CLAUDE.md` would otherwise make a run stop
  and ask, refuse work outside the current task, or write log entries and commits. The prompt
  describes behaviour only. It names no status code, pattern or test name, because those are what
  the new section should decide.

- **Four fresh, headless runs** (`claude -p`, Claude Code 2.1.284, 2026-09-29), each in its own
  throwaway git worktree checked out at commit `ea2182a`:

  | Run | `CLAUDE.md` it read |
  |---|---|
  | before-1, before-2 | `CLAUDE.md` exactly as committed at `ea2182a`, without the new section |
  | after-1, after-2 | The same file plus **only** the new section (`git diff --stat`: `CLAUDE.md \| 107 +`) |

  Everything else was identical: the code, the rest of `CLAUDE.md`, and the prompt. No user-level
  `CLAUDE.md` exists, so nothing else reached either side. **Two runs per side** show whether a
  difference comes from the file or just from how one run happened to go.

- **What was compared:** each run's `git diff -- backend/`. All four runs passed the suite (23 or 24
  tests).

- **The raw evidence is in [`agent-effect-runs/`](agent-effect-runs/):** `run-<side>-<n>.txt` is
  each run's final report and `diff-<side>-<n>.patch` its diff. Every patch applies cleanly to
  `ea2182a` (`git apply --check`), so any run can be reproduced in the code. The runs' output was
  captured through a Windows console, and three `→` arrows in `run-after-1.txt` came out as `ÔåÆ`.
  They are left as captured.

## The whole comparison

| Rule in the new section | before-1 | before-2 | after-1 | after-2 | Result |
|---|---|---|---|---|---|
| **Compare timestamps as values**, with `datetime.fromisoformat`, never `time.sleep` | order checked by id only | `time.sleep(0.01)` | `fromisoformat` | `fromisoformat` | **Consistent**: 2 of 2 after, 0 of 2 before |
| **Assert one exact status code** (the DELETE in the test's setup) | not checked | not checked | `== 204` | `== 204` | **Consistent**: 2 of 2 after, 0 of 2 before |
| **Tests grouped by resource, named `test_<verb>_<resource>_<behaviour>`** | followed, though the main test has no `_<behaviour>` suffix | new class `TestCollectionPrompts`; `test_empty_collection`, `test_sorted_newest_first` | followed | followed | **Consistent after**: 2 of 2 after, 1 of 2 before |
| **Check an optional value with `is None` / `is not None`**, not truthiness | truthiness | truthiness | `is None` | truthiness | **Not consistent**: 1 of 2 after |
| **Comments explain why**: a surprising decision gets a comment above the code | no | no | no | yes | **Not consistent**: 1 of 2 after |
| **404 when the id in the path names nothing** | 404 | 404 | 404 | 404 | **No effect**: the baseline already did it |
| Reuse `PromptList`, `get_prompts_by_collection` and `sort_prompts_by_date` | yes | yes | yes | yes | **No effect**: the baseline already did it |

**Against the new section:**

- **The error-handling section changed nothing here.** Both baseline runs already returned 404 for
  an unknown collection, copying the existing path-lookup endpoints. This test shows that the code
  alone was enough to teach that rule, not that the rule does nothing.
- **after-1 introduced a formatting slip** that neither baseline run made: it rewrote the next route's
  decorator as `@app.post("/collections",response_model=Collection, status_code=201)`, losing a
  space. Nothing in the section asks for it, and it is the kind of noise a single run can add.

## One instance, before and after: the timestamp check

**The rule** (*Testing requirements*):

> **Compare timestamps as values**, parsed with `datetime.fromisoformat`, never with `time.sleep`:
> `get_current_time()` resolves to microseconds.

**Before**: before-2, test `test_sorted_newest_first`. Without the rule, the run copied the provided
tests' habit of sleeping so that creation timestamps differ:

```python
    def test_sorted_newest_first(self, client: TestClient, sample_collection_data):
        """Verify the prompts come back newest first, as GET /prompts does.

        The sleep keeps the creation timestamps distinct; with equal ones the
        stable sort would keep creation order and the test would fail at random.
        ...
        """
        import time

        collection_id = client.post(
            "/collections", json=sample_collection_data
        ).json()["id"]
        for title in ["First", "Second", "Third"]:
            time.sleep(0.01)
            client.post(
                "/prompts",
                json={
                    "title": title,
                    "content": f"{title} prompt content",
                    "collection_id": collection_id,
                },
            )

        prompts = client.get(f"/collections/{collection_id}/prompts").json()["prompts"]
        assert [p["title"] for p in prompts] == ["Third", "Second", "First"]
```

**After**: after-1, test `test_list_collection_prompts_success`. With the rule, the run creates the
prompts back to back with no sleep, and checks the order on the timestamps themselves:

```python
        response = client.get(f"/collections/{collection_id}/prompts")
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 2
        assert [p["id"] for p in data["prompts"]] == [second["id"], first["id"]]
        created = [datetime.fromisoformat(p["created_at"]) for p in data["prompts"]]
        assert created[0] > created[1]
```

after-2 does the same:

```python
        assert datetime.fromisoformat(
            data["prompts"][0]["created_at"]
        ) > datetime.fromisoformat(data["prompts"][1]["created_at"])
```

**Why this counts as an effect of the file.** The sleep comes from the provided tests, which use
`time.sleep` twice; the new section lists them as Known exceptions not to copy. Neither after run
sleeps, and both compare parsed timestamps, which neither before run does. The only difference
between the two sides is the new section, and the rule is one line of it.
