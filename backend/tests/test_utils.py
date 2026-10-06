"""Unit tests for the helpers in ``app.utils``.

These call the helpers directly, without HTTP. Each class covers one helper,
with its cases grouped as behaviour, error conditions and edge cases, after
the Module 3 brief's "all utility functions and error conditions".
"""

from datetime import datetime
from types import SimpleNamespace
from typing import List, Optional

import pytest

from app.models import Prompt
from app.utils import (
    extract_variables,
    filter_prompts_by_collection,
    filter_prompts_by_tags,
    search_prompts,
    sort_prompts_by_date,
    validate_prompt_content,
)


def make_prompt(
    title: str,
    created_at: datetime = datetime(2026, 1, 1),
    collection_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Prompt:
    """Build a prompt with known fields, so its place in a result is fixed.

    Args:
        title: The prompt's title, used to tell prompts apart in assertions.
        created_at: The creation time to give it.
        collection_id: The collection to file it in, or ``None`` for none.
        tags: The tags to give it, or ``None`` for none.

    Returns:
        A ``Prompt`` with those fields.
    """
    return Prompt(
        title=title,
        content="Text.",
        created_at=created_at,
        collection_id=collection_id,
        tags=[] if tags is None else tags,
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


class TestFilterPromptsByTags:
    """Tests for ``filter_prompts_by_tags``, which keeps prompts carrying every tag given."""

    # --- behaviour ---

    def test_filter_prompts_by_tags_keeps_tagged_in_order(self):
        """Verify only the prompts carrying the tag are kept, in their original order."""
        prompts = [
            make_prompt("a", tags=["ai", "code-review"]),
            make_prompt("b", tags=["ai"]),
            make_prompt("c", tags=["python"]),
        ]

        result = filter_prompts_by_tags(prompts, ["ai"])

        assert [p.title for p in result] == ["a", "b"]


class TestSearchPrompts:
    """Tests for ``search_prompts``, a case-insensitive match on title or description."""

    # --- behaviour ---

    def test_search_prompts_matches_title_ignoring_case(self):
        """Verify a query matches part of a title whatever the case of either."""
        prompts = [
            Prompt(title="Code Review Helper", content="Text."),
            Prompt(title="Email draft", content="Text."),
        ]

        result = search_prompts(prompts, "REVIEW")

        assert [p.title for p in result] == ["Code Review Helper"]

    def test_search_prompts_matches_description(self):
        """Verify a query matches part of a description."""
        prompts = [
            Prompt(title="A", content="Text.", description="Summarises articles"),
            Prompt(title="B", content="Text.", description="Writes emails"),
        ]

        result = search_prompts(prompts, "summar")

        assert [p.title for p in result] == ["A"]

    def test_search_prompts_ignores_content(self):
        """Verify the prompt's ``content`` is not searched."""
        prompts = [Prompt(title="A", content="Translate to French.")]

        assert search_prompts(prompts, "french") == []

    def test_search_prompts_returns_new_list_in_order(self):
        """Verify the result is a new list in the original order, the input unchanged."""
        second = Prompt(title="Review two", content="Text.")
        other = Prompt(title="Other", content="Text.")
        first = Prompt(title="Review one", content="Text.")
        prompts = [second, other, first]

        result = search_prompts(prompts, "review")

        assert result == [second, first]
        assert prompts == [second, other, first]

    # --- error conditions ---

    def test_search_prompts_none_query_raises(self):
        """Verify a ``None`` query raises ``AttributeError``, even on an empty list.

        The query is lowered before any prompt is read, and the helper does
        not check it; ``GET /prompts`` only calls it with a non-empty string.
        """
        with pytest.raises(AttributeError, match="lower"):
            search_prompts([], None)

    # --- edge cases ---

    def test_search_prompts_empty_query_matches_all(self):
        """Verify an empty query matches every prompt."""
        prompts = [
            Prompt(title="A", content="Text."),
            Prompt(title="B", content="Text.", description="D"),
        ]

        assert search_prompts(prompts, "") == prompts

    def test_search_prompts_no_description_uses_title(self):
        """Verify a prompt without a description is matched on its title only."""
        prompts = [Prompt(title="Plain", content="Text.")]

        assert search_prompts(prompts, "plain") == prompts
        assert search_prompts(prompts, "missing") == []


class TestValidatePromptContent:
    """Tests for ``validate_prompt_content``, a minimum of 10 characters once trimmed."""

    # --- behaviour ---

    def test_validate_content_long_enough_true(self):
        """Verify a text well over 10 characters is accepted."""
        assert validate_prompt_content("Summarize this article in three bullets.") is True

    def test_validate_content_short_false(self):
        """Verify a text under 10 characters is rejected."""
        assert validate_prompt_content("Hi there") is False

    @pytest.mark.parametrize(
        "content, expected",
        [
            ("Summarize this article.", True),
            ("   too short   ", False),
            ("", False),
        ],
    )
    def test_validate_content_docstring_examples(self, content, expected):
        """Verify the three examples in the docstring give the results it shows.

        Args:
            content: The example input.
            expected: The result the docstring gives for it.
        """
        assert validate_prompt_content(content) is expected

    # --- error conditions ---

    def test_validate_content_none_false(self):
        """Verify ``None`` is treated as empty and gives ``False``, not an error."""
        assert validate_prompt_content(None) is False

    def test_validate_content_non_string_raises(self):
        """Verify a non-string such as ``123`` raises ``AttributeError``.

        Only falsy values are caught before ``strip()`` is called, so a
        truthy non-string reaches it and fails.
        """
        with pytest.raises(AttributeError, match="strip"):
            validate_prompt_content(123)

    # --- edge cases ---

    @pytest.mark.parametrize("length, expected", [(9, False), (10, True)])
    def test_validate_content_boundary(self, length, expected):
        """Verify exactly 10 characters is enough and 9 is not.

        Args:
            length: The number of characters in the text.
            expected: Whether that length passes.
        """
        assert validate_prompt_content("x" * length) is expected

    @pytest.mark.parametrize(
        "content, expected",
        [
            ("a b c d e f", True),
            ("   abcdefghi   ", False),
        ],
    )
    def test_validate_content_counts_inner_spaces_only(self, content, expected):
        """Verify inner spaces count towards the length and surrounding ones do not.

        Args:
            content: An 11-character text with inner spaces, or a
                9-character text padded with spaces.
            expected: Whether it passes.
        """
        assert validate_prompt_content(content) is expected

    @pytest.mark.parametrize("content", [" " * 10, "\t" * 10, "\n \t \n \t \n \t"])
    def test_validate_content_whitespace_only_false(self, content):
        """Verify a text of only whitespace is rejected, however long.

        Args:
            content: Ten or more spaces, tabs or newlines.
        """
        assert validate_prompt_content(content) is False


class TestExtractVariables:
    """Tests for ``extract_variables``, which finds ``{{name}}`` placeholders."""

    # --- behaviour ---

    def test_extract_variables_in_order_without_braces(self):
        """Verify names come back in order of appearance, without the braces."""
        content = "To {{recipient}}: re {{subject}}, from {{sender}}."

        assert extract_variables(content) == ["recipient", "subject", "sender"]

    def test_extract_variables_repeats_kept(self):
        """Verify a name used more than once appears once per use."""
        assert extract_variables("{{a}} {{b}} {{a}}") == ["a", "b", "a"]

    @pytest.mark.parametrize(
        "content, expected",
        [
            ("Dear {{name}}, your order {{order_id}} shipped.", ["name", "order_id"]),
            ("{{name}} and {{name}} again", ["name", "name"]),
            ("{{ name }} and {{first-name}}", []),
        ],
    )
    def test_extract_variables_docstring_examples(self, content, expected):
        """Verify the three examples in the docstring give the results it shows.

        Args:
            content: The example input.
            expected: The result the docstring gives for it.
        """
        assert extract_variables(content) == expected

    # --- error conditions ---

    def test_extract_variables_none_raises(self):
        """Verify ``None`` raises ``TypeError``, since ``re.findall`` needs a string."""
        with pytest.raises(TypeError, match="expected string"):
            extract_variables(None)

    # --- edge cases ---

    def test_extract_variables_none_found(self):
        """Verify text with no placeholders gives an empty list."""
        assert extract_variables("Plain text with no variables.") == []

    @pytest.mark.parametrize("content", ["{name}", "{{}}", "{{name}", "{name}}"])
    def test_extract_variables_needs_double_braces_and_name(self, content):
        """Verify single, unbalanced or empty braces are not variables.

        Args:
            content: A near miss for ``{{name}}``.
        """
        assert extract_variables(content) == []

    @pytest.mark.parametrize("name", ["var_1", "2", "_", "año"])
    def test_extract_variables_word_characters_allowed(self, name):
        """Verify digits, underscores and non-ASCII letters are accepted in a name.

        ``\\w`` matches any Unicode word character, so ``año`` counts.

        Args:
            name: A name made only of word characters.
        """
        assert extract_variables("{{" + name + "}}") == [name]

    def test_extract_variables_triple_braces(self):
        """Verify ``{{{name}}}`` gives ``name``, the extra braces left as text."""
        assert extract_variables("{{{name}}}") == ["name"]
