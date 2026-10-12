"""Utility functions for PromptLab.

The list helpers sort, filter and search prompts for ``GET /prompts``, and
``count_tags`` counts the tags in use for ``GET /tags``. None of them
modifies the list it is given. ``add_version`` returns a prompt's history with
a new version added when its content changed, as a new dict. The two text helpers,
``validate_prompt_content`` and ``extract_variables``, are not called by
the API; only ``tests/test_utils.py`` uses them. ``parse_cors_origins`` turns
the ``CORS_ORIGINS`` environment variable into the list of page addresses the
API accepts browser requests from.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.models import Prompt, PromptVersion, TagSummary


# The Vite dev server's address, so a local frontend works with no setting.
DEFAULT_CORS_ORIGINS = ["http://localhost:5173"]


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
    """Keep the prompts that carry every one of the given tags.

    The match on each tag is exact. A tag that no prompt carries is not an
    error; it matches nothing. A tag repeated in ``tags`` counts once. An
    empty ``tags`` keeps every prompt, although ``GET /prompts`` only calls
    this when at least one tag is given.

    Args:
        prompts: The prompts to filter. The list itself is not modified.
        tags: The tags to look for.

    Returns:
        A new list of the matching prompts, in their original order.
    """
    return [p for p in prompts if all(tag in p.tags for tag in tags)]


def count_tags(prompts: List[Prompt]) -> List[TagSummary]:
    """Count how many of the given prompts carry each tag.

    A tag no prompt carries does not appear. Each prompt counts once per
    tag, since a prompt cannot repeat a tag.

    Args:
        prompts: The prompts to count. The list itself is not modified.

    Returns:
        A new list with one ``TagSummary`` per distinct tag, sorted by name
        in Python's string order, so ``"a-b"`` comes before ``"a1"`` and
        ``"a1"`` before ``"ab"``.
    """
    counts = {}
    for prompt in prompts:
        for tag in prompt.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return [TagSummary(name=tag, prompt_count=counts[tag]) for tag in sorted(counts)]


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


def add_version(
    versions: Dict[int, PromptVersion], content: str, created_at: datetime
) -> Dict[int, PromptVersion]:
    """Return a prompt's history with a new version added if the content changed.

    The content is compared with the latest version character for character,
    so a change of case or whitespace counts. An empty history is treated as
    holding version 0, so its first entry becomes version 1.

    Args:
        versions: The history, keyed by version number. It is not modified.
        content: The prompt's content after the edit.
        created_at: When the edit was made; the new version is dated with it.

    Returns:
        A new dict. It holds every existing version plus version n + 1 when
        ``content`` differs from version n's, and the same versions otherwise.
    """
    result = dict(versions)
    latest = max(versions, default=0)
    if latest == 0 or versions[latest].content != content:
        result[latest + 1] = PromptVersion(
            version=latest + 1, content=content, created_at=created_at
        )
    return result


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


def parse_cors_origins(value: Optional[str]) -> List[str]:
    """Turn a comma-separated list of origins into the list CORS accepts.

    Each origin is an address such as ``https://promptlab.example.com``.
    Spaces around entries and empty entries are dropped, and a trailing slash
    is removed, because the browser sends an origin without one and CORS
    compares the strings exactly. When the value is absent or holds no
    origin, ``DEFAULT_CORS_ORIGINS`` is returned.

    Args:
        value: The raw ``CORS_ORIGINS`` value, or None when it is not set.

    Returns:
        A new list of origins, in the order given.
    """
    origins = [item.strip().rstrip("/") for item in (value or "").split(",")]
    origins = [origin for origin in origins if origin]
    return origins or list(DEFAULT_CORS_ORIGINS)
