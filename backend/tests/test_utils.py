"""Unit tests for the helpers in ``app.utils``.

These call the helpers directly, without HTTP. Each class covers one helper,
with its cases grouped as behaviour, error conditions and edge cases, after
the Module 3 brief's "all utility functions and error conditions".
"""

from datetime import datetime
from types import SimpleNamespace
from typing import Optional

import pytest

from app.models import Prompt
from app.utils import filter_prompts_by_collection, sort_prompts_by_date


def make_prompt(
    title: str,
    created_at: datetime = datetime(2026, 1, 1),
    collection_id: Optional[str] = None,
) -> Prompt:
    """Build a prompt with known fields, so its place in a result is fixed.

    Args:
        title: The prompt's title, used to tell prompts apart in assertions.
        created_at: The creation time to give it.
        collection_id: The collection to file it in, or ``None`` for none.

    Returns:
        A ``Prompt`` with those fields.
    """
    return Prompt(
        title=title,
        content="Text.",
        created_at=created_at,
        collection_id=collection_id,
    )


class TestSortPromptsByDate:
    """Tests for ``sort_prompts_by_date``, which orders prompts by ``created_at``."""

    # --- behaviour ---

    def test_sort_prompts_newest_first_by_default(self):
        """Verify the default order puts the most recently created prompt first."""
        old = make_prompt("old", datetime(2026, 1, 1))
        mid = make_prompt("mid", datetime(2026, 1, 2))
        new = make_prompt("new", datetime(2026, 1, 3))

        result = sort_prompts_by_date([mid, old, new])

        assert [p.title for p in result] == ["new", "mid", "old"]

    def test_sort_prompts_oldest_first_when_ascending(self):
        """Verify ``descending=False`` puts the oldest prompt first."""
        old = make_prompt("old", datetime(2026, 1, 1))
        mid = make_prompt("mid", datetime(2026, 1, 2))
        new = make_prompt("new", datetime(2026, 1, 3))

        result = sort_prompts_by_date([mid, new, old], descending=False)

        assert [p.title for p in result] == ["old", "mid", "new"]

    def test_sort_prompts_returns_new_list(self):
        """Verify the result is a new list and the input keeps its order."""
        old = make_prompt("old", datetime(2026, 1, 1))
        new = make_prompt("new", datetime(2026, 1, 2))
        prompts = [old, new]

        result = sort_prompts_by_date(prompts)

        assert result is not prompts
        assert prompts == [old, new]

    # --- error conditions ---

    def test_sort_prompts_item_without_created_at_raises(self):
        """Verify an item with no ``created_at`` raises ``AttributeError``.

        The helper does not check its input; callers pass only stored
        prompts, which always have the field.
        """
        prompt = make_prompt("p", datetime(2026, 1, 1))

        with pytest.raises(AttributeError, match="created_at"):
            sort_prompts_by_date([prompt, object()])

    # --- edge cases ---

    def test_sort_prompts_empty_list(self):
        """Verify an empty list gives an empty list."""
        assert sort_prompts_by_date([]) == []

    @pytest.mark.parametrize("descending", [True, False])
    def test_sort_prompts_equal_dates_keep_order(self, descending):
        """Verify prompts created at the same moment keep their original order.

        Args:
            descending: The sort direction under test.
        """
        same = datetime(2026, 1, 1)
        first = make_prompt("first", same)
        second = make_prompt("second", same)

        result = sort_prompts_by_date([first, second], descending=descending)

        assert [p.title for p in result] == ["first", "second"]


class TestFilterPromptsByCollection:
    """Tests for ``filter_prompts_by_collection``, an exact match on ``collection_id``."""

    # --- behaviour ---

    def test_filter_prompts_keeps_collection_in_order(self):
        """Verify only the prompts in the collection are kept, in their original order."""
        prompts = [
            make_prompt("a1", collection_id="col-a"),
            make_prompt("b1", collection_id="col-b"),
            make_prompt("a2", collection_id="col-a"),
            make_prompt("none"),
        ]

        result = filter_prompts_by_collection(prompts, "col-a")

        assert [p.title for p in result] == ["a1", "a2"]

    def test_filter_prompts_returns_new_list(self):
        """Verify the result is a new list and the input is unchanged."""
        a = make_prompt("a", collection_id="col-a")
        b = make_prompt("b", collection_id="col-b")
        prompts = [a, b]

        result = filter_prompts_by_collection(prompts, "col-a")

        assert result is not prompts
        assert prompts == [a, b]

    # --- error conditions ---

    def test_filter_prompts_item_without_collection_id_raises(self):
        """Verify an item with no ``collection_id`` raises ``AttributeError``.

        The helper does not check its input; callers pass only stored
        prompts, which always have the field.
        """
        with pytest.raises(AttributeError, match="collection_id"):
            filter_prompts_by_collection([SimpleNamespace(title="x")], "col-a")

    # --- edge cases ---

    def test_filter_prompts_unknown_collection_empty(self):
        """Verify an id that no prompt has gives an empty list, not an error."""
        prompts = [make_prompt("a", collection_id="col-a")]

        assert filter_prompts_by_collection(prompts, "nope") == []

    def test_filter_prompts_none_keeps_unfiled(self):
        """Verify ``None`` keeps the prompts that are in no collection."""
        prompts = [make_prompt("filed", collection_id="col-a"), make_prompt("unfiled")]

        result = filter_prompts_by_collection(prompts, None)

        assert [p.title for p in result] == ["unfiled"]

    @pytest.mark.parametrize("query", ["col", "COL-1", "col-1 "])
    def test_filter_prompts_match_is_exact(self, query):
        """Verify a prefix, a different case or extra whitespace does not match.

        Args:
            query: A near miss for the stored id ``col-1``.
        """
        prompts = [make_prompt("p", collection_id="col-1")]

        assert filter_prompts_by_collection(prompts, query) == []

    def test_filter_prompts_empty_string_not_none(self):
        """Verify ``""`` keeps only prompts stored with ``""``, not those with ``None``.

        POST and PUT store an empty ``collection_id`` unchecked, so such
        prompts can exist; ``GET /prompts`` never reaches them, since it
        skips the filter for an empty value.
        """
        prompts = [make_prompt("empty", collection_id=""), make_prompt("unfiled")]

        result = filter_prompts_by_collection(prompts, "")

        assert [p.title for p in result] == ["empty"]
