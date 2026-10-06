"""Pydantic models for PromptLab.

Defines the request bodies the API accepts, the stored records it returns,
and the list and health responses. Validation constraints declared here are
enforced by FastAPI before an endpoint runs; a body that breaks one is
rejected with status 422.
"""

from datetime import datetime
from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


def generate_id() -> str:
    """Create a new random identifier for a prompt or collection.

    Used as the default factory for ``Prompt.id`` and ``Collection.id``.

    Returns:
        A random UUID4 in its 36-character string form, for example
        ``"3f2b8c1e-9a4d-4e7b-b1c2-5d6e7f8a9b0c"``.
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Return the current time in UTC, used for every timestamp.

    Used as the default factory for the ``created_at`` and ``updated_at``
    fields, and by the PUT and PATCH endpoints to refresh ``updated_at``.

    Returns:
        The current UTC time as a naive ``datetime``: its ``tzinfo`` is
        ``None``, so the value carries no timezone of its own.
    """
    return datetime.utcnow()


# ============== Prompt Models ==============

# A type of its own, not a validator on the list, so Pydantic reports each bad
# tag at its own index, ["body", "tags", <i>], with its own message.
Tag = Annotated[str, Field(min_length=1, max_length=32, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]

# One value of the ?tag= filter on GET /prompts. The Tag rule made optional,
# ( ... )?, so "" passes validation and list_prompts can drop it (AC-3.6).
TagQuery = Annotated[str, Field(max_length=32, pattern=r"^([a-z0-9]+(-[a-z0-9]+)*)?$")]


def check_tag_list(tags: List[str]) -> List[str]:
    """Apply the rules on a whole list of tags, once each tag has passed ``Tag``.

    Called by the ``tags`` validator of ``PromptBase`` and ``PromptPatch``, so
    the list rules are written in one place.

    Args:
        tags: The tags sent, each already a valid ``Tag``.

    Returns:
        The same list, unchanged and in the order sent.

    Raises:
        ValueError: If there are more than 10 tags. FastAPI reports it as
            status 422, with ``msg`` "Value error, a prompt can have at most
            10 tags; delete a tag before including another". Checked first,
            so a list that also repeats a tag gets only this message.
        ValueError: If a tag appears more than once. FastAPI reports it as
            status 422, with ``msg`` "Value error, tags must not repeat a
            tag".
    """
    if len(tags) > 10:
        raise ValueError(
            "a prompt can have at most 10 tags; delete a tag before including another"
        )
    if len(set(tags)) != len(tags):
        raise ValueError("tags must not repeat a tag")
    return tags


class PromptBase(BaseModel):
    """Fields a client supplies for a prompt, with their constraints.

    Length limits count characters as sent; values are not stripped, so a
    title made only of spaces satisfies ``min_length=1``.

    Attributes:
        title: Required. Between 1 and 200 characters.
        content: Required. The prompt text; at least 1 character.
        description: Optional note of at most 500 characters. Defaults to
            ``None``.
        collection_id: Optional identifier of the collection the prompt is
            filed in. Defaults to ``None``. The model does not check that
            the collection exists; the create and update endpoints do.
        tags: Optional list of tags, kept in the order sent. Defaults to a
            new empty list. Each tag is 1 to 32 characters of lowercase
            letters and digits, with single hyphens between them, so
            ``"code-review"`` is valid and ``"Python"`` or ``"-ai"`` is not.
            At most 10 tags, none repeated.
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: List[Tag] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def check_tags(cls, value):
        """Apply ``check_tag_list`` to the tags sent.

        Runs after every item has passed ``Tag``, so a list holding a bad tag
        is reported on that tag, not on the list.

        Args:
            value: The list of tags sent.

        Returns:
            The list unchanged, when it passes ``check_tag_list``.

        Raises:
            ValueError: If ``check_tag_list`` refuses the list.
        """
        return check_tag_list(value)


class PromptCreate(PromptBase):
    """Request body for ``POST /prompts``.

    Carries the ``PromptBase`` fields only. Keys the model does not declare,
    such as ``id`` or ``created_at``, are silently dropped, so a client
    cannot choose the identifier or timestamps of a new prompt.
    """


class PromptUpdate(PromptBase):
    """Request body for ``PUT /prompts/{prompt_id}``, a full replacement.

    Carries the ``PromptBase`` fields only. Because the whole prompt is
    replaced, an optional field left out of the body is reset to its
    default of ``None`` rather than kept; omitting ``collection_id``
    unfiles the prompt.
    """


class PromptPatch(BaseModel):
    """Body of a partial update.

    Every field is optional so that a client may omit it. Which fields were
    actually sent is read with ``model_dump(exclude_unset=True)``, not by
    testing for ``None`` -- that keeps an explicit ``null`` (clear the
    description, or unfile the prompt) distinct from an absent key (leave the
    field alone). The validation
    constraints are repeated from ``PromptBase`` so a partial update cannot
    store a value that ``POST`` or ``PUT`` would have rejected.

    Attributes:
        title: Optional. If sent, between 1 and 200 characters. An explicit
            ``null`` is rejected with status 422, since a prompt cannot store it.
        content: Optional. If sent, at least 1 character. An explicit ``null``
            is rejected the same way.
        description: Optional. If sent, at most 500 characters, or ``null``
            to clear it.
        collection_id: Optional. If sent, a collection identifier, or
            ``null`` to unfile the prompt.
        tags: Optional. If sent, a list of tags that replaces the stored
            tags, under the same rules as on create; an empty list clears
            them. An explicit ``null`` is rejected with status 422, as for
            ``title``.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: Optional[List[Tag]] = None

    @field_validator("title", "content", "tags")
    @classmethod
    def reject_null(cls, value, info):
        """Refuse an explicit null for ``title``, ``content`` or ``tags``.

        Pydantic runs this only for keys the body carries, so an omitted field
        is still left alone. It runs while the body is validated, before
        ``patch_prompt`` looks anything up.

        Args:
            value: The value sent for the field.
            info: Validation context; ``info.field_name`` names the field.

        Returns:
            The value unchanged, when it is not ``None``.

        Raises:
            ValueError: If the value is ``None``. FastAPI reports it as status
                422, with ``msg`` "Value error, <field> cannot be null; send a
                value or omit the field to keep the current one".
        """
        if value is None:
            raise ValueError(
                f"{info.field_name} cannot be null; send a value or omit the "
                "field to keep the current one"
            )
        return value

    @field_validator("tags")
    @classmethod
    def check_tags(cls, value):
        """Apply ``check_tag_list`` to the tags sent.

        Runs only when the body carries ``tags``, and after ``reject_null``,
        so the value is always a list.

        Args:
            value: The list of tags sent.

        Returns:
            The list unchanged, when it passes ``check_tag_list``.

        Raises:
            ValueError: If ``check_tag_list`` refuses the list.
        """
        # No None check: value is never None here. An absent key keeps the
        # default without running validators, and an explicit null is
        # refused by reject_null, declared above so it runs first. Moving
        # this validator above reject_null, or adding validate_default=True,
        # would let None reach len() in check_tag_list and give a 500.
        return check_tag_list(value)


class Prompt(PromptBase):
    """A stored prompt, as kept in storage and returned by the API.

    Adds the server-assigned fields to ``PromptBase``. Each default factory
    runs separately, so on a newly created prompt ``created_at`` and
    ``updated_at`` are read from the clock twice: they differ by a few
    microseconds where the clock is that fine, and are usually equal where
    it is coarser (Python 3.12 on Windows steps about every millisecond).

    Attributes:
        id: Unique identifier. Defaults to a new ``generate_id()`` value.
        created_at: When the prompt was created, as naive UTC. Defaults to
            ``get_current_time()``.
        updated_at: When the prompt was last changed, as naive UTC.
            Defaults to ``get_current_time()``.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Pydantic settings for ``Prompt``.

        ``from_attributes`` lets ``Prompt.model_validate`` build a prompt
        from any object with matching attributes, not only from a dict.
        No code in the application currently relies on it.
        """

        from_attributes = True


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    """Fields a client supplies for a collection, with their constraints.

    Attributes:
        name: Required. Between 1 and 100 characters.
        description: Optional note of at most 500 characters. Defaults to
            ``None``.
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Request body for ``POST /collections``.

    Carries the ``CollectionBase`` fields only. Undeclared keys such as
    ``id`` are silently dropped.
    """


class Collection(CollectionBase):
    """A stored collection, as kept in storage and returned by the API.

    Unlike ``Prompt``, a collection has no ``updated_at``: no endpoint
    edits a collection after it is created.

    Attributes:
        id: Unique identifier. Defaults to a new ``generate_id()`` value.
        created_at: When the collection was created, as naive UTC. Defaults
            to ``get_current_time()``.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Pydantic settings for ``Collection``.

        ``from_attributes`` lets ``Collection.model_validate`` build a
        collection from any object with matching attributes, not only from
        a dict. No code in the application currently relies on it.
        """

        from_attributes = True


# ============== Response Models ==============

class PromptList(BaseModel):
    """Response body for ``GET /prompts``.

    Attributes:
        prompts: The prompts that passed the request's collection and
            search filters, most recently created first.
        total: Number of prompts in ``prompts``, counted after filtering,
            not the number stored.
    """

    prompts: List[Prompt]
    total: int


class CollectionList(BaseModel):
    """Response body for ``GET /collections``.

    Attributes:
        collections: Every stored collection. This endpoint takes no
            filters.
        total: Number of collections in ``collections``.
    """

    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    """Response body for ``GET /health``.

    Attributes:
        status: Always ``"healthy"``. The endpoint checks nothing further,
            so the value only confirms that the app answered.
        version: The application version, taken from ``app.__version__``.
    """

    status: str
    version: str
