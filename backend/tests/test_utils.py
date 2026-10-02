"""Unit tests for the helpers in ``app.utils``.

These call the helpers directly, without HTTP. Each class covers one helper,
with its cases grouped as behaviour, error conditions and edge cases, after
the Module 3 brief's "all utility functions and error conditions".
"""

from datetime import datetime

import pytest

from app.models import Prompt
from app.utils import sort_prompts_by_date


def make_prompt(title: str, created_at: datetime) -> Prompt:
    """Build a prompt with a known creation time, so its sort position is fixed.

    Args:
        title: The prompt's title, used to tell prompts apart in assertions.
        created_at: The creation time to give it.

    Returns:
        A ``Prompt`` with that title and ``created_at``.
    """
    return Prompt(title=title, content="Text.", created_at=created_at)


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
