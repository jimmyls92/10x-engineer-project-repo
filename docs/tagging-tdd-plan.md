# Tagging System: TDD cycle plan

Working note for Task 3.2. **Kept out of git during the task** (Module 3 log, entry 232) and
committed at the close of Module 3 (entry 478), unchanged apart from this sentence. It summarises
the cycles settled in `docs/prompt-log.md` (Module 3, entries 107-255), so each red and green commit
can follow its row. The spec is
`specs/tagging-system.md`; AC numbers are its acceptance criteria.

**Rules the plan follows** (log entries 107, 112, 131, 226):

- Vertical slices in user-story order, US-1 to US-4. Each slice runs its unit tests red-first, in
  the same red commit as the API tests that share their green.
- One red commit per cycle, then one green commit with the minimum code that passes it.
- Every test in a red commit must be capable of failing. A test that passes on arrival may sit beside
  a genuinely failing one; the red commit's message says so.
- A test joins the red commit of the cycle whose green turns it green, so every green commit leaves
  the whole suite passing.

"Passes on arrival" is marked **(on arrival)**.

---

## US-1: tag a prompt when creating or editing it

| # | Red tests | Fails when committed because… | Green change |
|---|---|---|---|
| 1 | Unit `PromptBase.tags` (`test_models.py`); AC-1.1, AC-1.2, AC-1.6, AC-1.8, AC-2.6; E-5 on PUT and PATCH (`test_update_prompt_unknown_collection_keeps_tags`, finding 9); E-5 on POST **(on arrival)**; E-8 (`test_delete_collection_keeps_tags`) | No `tags` field: `.tags` raises; the key is dropped, so no response carries `tags` (`KeyError` when E-5 reads them back), and `"tags": null` gets 201 | `tags: List[str] = Field(default_factory=list)` on `PromptBase` |
| 2 | AC-1.7 | `update_prompt` rebuilds the `Prompt` without `tags`, so PUT stores `[]` | `update_prompt` passes `tags=prompt_data.tags` |
| 3 | Unit `PromptPatch.tags` (`test_models.py`) | No field on `PromptPatch`, so `.tags` raises | `tags` on `PromptPatch`, as `Optional[List[str]] = None` |
| 4 | AC-1.4 | `patch_prompt` rebuilds without `tags`, so PATCH stores `[]`, not `["ai"]` | `patch_prompt` passes `tags=existing.tags` |
| 5 | AC-1.3, AC-1.5 | PATCH always keeps `["ai"]`, so it ignores `["python"]` and `[]` | `tags=changes.get("tags", existing.tags)` (not `or`, which turns `[]` into `["ai"]`, entry 126) |

Notes:

- E-5 on PUT and PATCH fails in cycle 1 because the setup's tags are not stored, not because a
  rejected request overwrites them (entry 250).
- E-5 on POST passes at every point, since no cycle changes `create_prompt`; it can fail if
  `create_prompt` stored before checking the collection (entries 252-254).

## US-2: invalid tags are refused

| # | Red tests | Fails when committed because… | Green change |
|---|---|---|---|
| 1 | Unit `PromptBase` with each bad tag raises `ValidationError`, and with a 32-character tag is accepted **(on arrival)**; AC-2.3; AC-2.1 **(on arrival)** | `tags` is a plain `List[str]`, so no bad tag is refused | `Tag` type (pattern, min and max length), wired as `tags: List[Tag]` on `PromptBase` |
| 2 | Unit `check_tag_list` with 10 tags returns the list **(fails: no function)**, with 11 raises `ValueError`; AC-2.5; AC-2.2 **(on arrival)** | `check_tag_list` does not exist; 11 tags get 201 | `check_tag_list` with the count check only, called by a `field_validator("tags")` on `PromptBase` |
| 3 | Unit `check_tag_list(["ai", "ai"])` raises `ValueError`; AC-2.4 | No repeat check: `["ai", "ai"]` gets 201 | Repeat check in `check_tag_list` |
| 4 | AC-2.7 (parametrised: PUT **(on arrival)**, PATCH); AC-2.8 | `PromptPatch.tags` is `List[str]`: PATCH `["Python"]` gets 200, and `PATCH /prompts/nope` gets 404 | `PromptPatch.tags: Optional[List[Tag]] = None` |
| 5 | AC-2.9 | `{"tags": null}` passes `PromptPatch`, then `Prompt(tags=None)` raises inside the endpoint: 500 | `"tags"` added to `reject_null` (`models.py:110`) |
| 6 | PATCH with 11 tags; PATCH with a repeated tag (not in the spec's test table, as with finding 9, entry 165) | No list check on `PromptPatch`: `Prompt(...)` raises inside the endpoint: 500 | Second `field_validator("tags")` on `PromptPatch`, calling `check_tag_list` when not `None` |

## US-3: find prompts by tag

Setup for every AC: P1 `["ai", "code-review"]`, P2 `["ai"]`, P3 `["python"]`, created in that order.

| # | Red tests | Fails when committed because… | Green change |
|---|---|---|---|
| 1 | Unit `filter_prompts_by_tags` (`test_utils.py`): A `[ai, x]`, B `[ai]`, C `[python]`, `tags=["ai"]` → `[A, B]`, input order; AC-3.1; AC-3.3; AC-3.9; AC-3.4 **(on arrival)**; AC-3.5 **(on arrival)** | `tag` is not declared, so it is ignored: P3, P2, P1 for every `?tag=`; the helper does not exist | `tag` parameter in `list_prompts`; `if tag:` step calling the helper, before the sort; `filter_prompts_by_tags` keeping a prompt when `any(tag in prompt.tags for tag in tags)` |
| 2 | Unit `filter_prompts_by_tags` (`test_utils.py`): A `[ai]`, B `[ai, code-review]`, `tags=["ai", "code-review"]` → `[B]`; AC-3.2 | `any` keeps every prompt with one of the tags: the unit test gets `[A, B]`, AC-3.2 gets P2, P1 | `any` → `all` |
| 3 | AC-3.6 (both requests); AC-3.8 **(on arrival)** | `tag=[""]`: `all` needs `""`, which no prompt has, so `[]` | `tag = [x for x in tag if x != ""]` in `list_prompts`, before `if tag:`; **also revert the `list_prompts` docstring's interim note that an empty `tag` matches nothing** (entry 322) |
| 4 | AC-3.7 (both requests); E-7 (a 33-character value), the third case of `test_list_prompts_invalid_tag` | Nothing validates `tag`: `?tag=Python` and the 33-character value get 200 and `[]` | `TagQuery` in `models.py`; `tag: List[TagQuery]` in `list_prompts` |

Notes:

- AC-3.4 and AC-3.5 can fail: a tag-first `if`/`elif` between the filters returns P2, P1 (entries
  189-192).
- AC-3.8 guards cycle 3: with a `None` default, the comprehension raises `TypeError` (entry 209).
- AC-3.9 fails in cycle 1 because `tag` is ignored, not because of the repeat (entry 210).

## US-4: see which tags exist and how often

| # | Red tests | Fails when committed because… | Green change |
|---|---|---|---|
| 1 | AC-4.1, AC-4.5 (`test_list_tags_empty`) | No `/tags` route: 404 | `TagSummary` and `TagList` in `models.py` (new `Tag Models` banner); `list_tags` in `api.py` (new `Tag Endpoints` banner), `response_model=TagList`, returning the fixed `{"tags": [], "total": 0}` |
| 2 | Unit `count_tags` (`test_utils.py`): A `[python, ai]`, B `[ai]` → `[TagSummary(name="ai", prompt_count=2), TagSummary(name="python", prompt_count=1)]`; AC-4.2, AC-4.3, AC-4.4, AC-4.6 | `count_tags` does not exist: `ImportError` while `test_utils.py` loads, so no test in it runs; the API body is the fixed empty one | `count_tags` in `utils.py` (counts with `counts.get(tag, 0) + 1`, returns `TagSummary` for `tag in sorted(counts)`); `list_tags` returns `TagList(tags=count_tags(storage.get_all_prompts()), total=len(tags))`, computed on every call |

Notes:

- AC-4.5 passes in cycle 1 only because the body is fixed; from cycle 2 it checks untagged prompts
  (entries 216, 230).
- AC-4.3 and AC-4.4 guard against a tag list computed once and never refreshed (entry 230).
- The `count_tags` unit test lists `python` before `ai`, so first-seen order differs from
  alphabetical and a missing `sorted` fails it (entries 241-243).
