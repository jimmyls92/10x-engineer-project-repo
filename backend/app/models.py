"""Pydantic models for PromptLab.

Defines the request bodies the API accepts, the stored records it returns,
and the list and health responses. Validation constraints declared here are
enforced by FastAPI before an endpoint runs; a body that breaks one is
rejected with status 422.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
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
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


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
    testing for ``None`` -- that keeps an explicit ``null`` (clear the field)
    distinct from an absent key (leave the field alone). The validation
    constraints are repeated from ``PromptBase`` so a partial update cannot
    store a value that ``POST`` or ``PUT`` would have rejected.

    Attributes:
        title: Optional. If sent as text, between 1 and 200 characters.
            An explicit ``null`` is accepted by this model, although a
            prompt cannot store it; ``PATCH`` then fails with status 500.
        content: Optional. If sent as text, at least 1 character. An
            explicit ``null`` is accepted here and fails the same way.
        description: Optional. If sent, at most 500 characters, or ``null``
            to clear it.
        collection_id: Optional. If sent, a collection identifier, or
            ``null`` to unfile the prompt.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class Prompt(PromptBase):
    """A stored prompt, as kept in storage and returned by the API.

    Adds the server-assigned fields to ``PromptBase``. Each default factory
    runs separately, so on a newly created prompt ``created_at`` and
    ``updated_at`` differ by a few microseconds rather than being equal.

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
