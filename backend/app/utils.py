"""Utility functions for PromptLab.

The list helpers sort, filter and search prompts for ``GET /prompts``. None
of them modifies the list it is given. The two text helpers,
``validate_prompt_content`` and ``extract_variables``, are not called by
the API or the tests.
"""

from typing import List
from app.models import Prompt


def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by creation date, newest first by default.

    Args:
        prompts: The prompts to sort. The list itself is not modified.
        descending: If True, the default, the newest prompt comes first; if
            False, the oldest does.

    Returns:
        A new list holding the same prompts, ordered by creation date.
    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    """Keep the prompts filed in the given collection.

    The match on ``collection_id`` is exact, and the collection need not
    exist: an unknown id gives an empty list. Passing ``None`` keeps the
    prompts that are in no collection, although ``GET /prompts`` only calls
    this when a ``collection_id`` is given.

    Args:
        prompts: The prompts to filter. The list itself is not modified.
        collection_id: Identifier of the collection to keep.

    Returns:
        A new list of the matching prompts, in their original order.
    """
    return [p for p in prompts if p.collection_id == collection_id]


def filter_prompts_by_tags(prompts: List[Prompt], tags: List[str]) -> List[Prompt]:
    """Keep the prompts that carry any of the given tags.

    The match on each tag is exact. A tag that no prompt carries is not an
    error; it matches nothing.

    Args:
        prompts: The prompts to filter. The list itself is not modified.
        tags: The tags to look for.

    Returns:
        A new list of the matching prompts, in their original order.
    """
    return [p for p in prompts if any(tag in p.tags for tag in tags)]


def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    """Keep the prompts whose title or description contains the query.

    The match ignores case and looks for the query anywhere in the text.
    The prompt's ``content`` is not searched, and a prompt without a
    description can match on its title only. An empty query matches every
    prompt, although ``GET /prompts`` never passes one.

    Args:
        prompts: The prompts to search. The list itself is not modified.
        query: The text to look for.

    Returns:
        A new list of the matching prompts, in their original order.
    """
    query_lower = query.lower()
    return [
        p for p in prompts
        if query_lower in p.title.lower() or
           (p.description and query_lower in p.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Check that prompt text is at least 10 characters once trimmed.

    Leading and trailing whitespace is ignored when counting; spaces inside
    the text still count, so ``"a b c d e f"`` passes. Nothing in
    the application calls this function: the API accepts any ``content``
    of at least 1 character (``PromptBase.content``), so a prompt this
    function rejects can still be stored.

    Args:
        content: The prompt text to check. ``None`` is accepted and
            treated as empty.

    Returns:
        ``True`` if the text has at least 10 characters after stripping
        whitespace from both ends, ``False`` otherwise.

    Examples:
        >>> validate_prompt_content("Summarize this article.")
        True
        >>> validate_prompt_content("   too short   ")
        False
        >>> validate_prompt_content("")
        False
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> List[str]:
    """List the template variables written as ``{{name}}`` in prompt text.

    A name is one or more letters, digits or underscores with no spaces
    inside the braces, so ``{{ name }}`` and ``{{first-name}}`` are not
    variables. Nothing in the application calls this function.

    Args:
        content: The prompt text to scan.

    Returns:
        The variable names in order of appearance, without the braces.
        A name used more than once appears once per use; the list is empty
        if the text has no variables.

    Examples:
        >>> extract_variables("Dear {{name}}, your order {{order_id}} shipped.")
        ['name', 'order_id']
        >>> extract_variables("{{name}} and {{name}} again")
        ['name', 'name']
        >>> extract_variables("{{ name }} and {{first-name}}")
        []
    """
    import re
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)
