"""In-memory storage for PromptLab.

This module provides simple in-memory storage for prompts and collections.
In a production environment, this would be replaced with a database.

The module-level ``storage`` instance is the single store the API uses.
Nothing is written to disk, so every prompt and collection is lost when the
process stops.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection


class Storage:
    """Holds prompts and collections in memory, keyed by their id.

    Records are stored and returned as the same objects: a caller that
    changes a returned prompt or collection changes the stored one too.
    Methods never raise for a missing record; they return ``None`` or
    ``False`` instead, and the API decides which error status to send.
    """

    def __init__(self):
        """Create an empty store with no prompts and no collections."""
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}

    # ============== Prompt Operations ==============

    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Store a prompt under its own id.

        A prompt already stored with the same id is replaced without
        warning; the store does not check for duplicates.

        Args:
            prompt: The prompt to store, with its id already assigned.

        Returns:
            The same prompt object that was stored.
        """
        self._prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Look up one prompt by id.

        Args:
            prompt_id: Identifier of the prompt to return.

        Returns:
            The stored prompt, or ``None`` if no prompt has that id.
        """
        return self._prompts.get(prompt_id)

    def get_all_prompts(self) -> List[Prompt]:
        """Return every stored prompt, in the order they were first stored.

        Returns:
            A new list, so adding to or removing from it leaves the store
            unchanged. The prompts in it are the stored objects themselves.
        """
        return list(self._prompts.values())

    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Replace an existing prompt with a new version.

        The new prompt is stored under ``prompt_id`` as given. The caller
        must pass a prompt whose ``id`` equals ``prompt_id``; this is not
        checked. If they differ, the record is kept under ``prompt_id``
        while reporting the other id, and a lookup by that id finds
        nothing.

        Args:
            prompt_id: Identifier of the prompt to replace.
            prompt: The new version of the prompt.

        Returns:
            The new prompt as stored, or ``None`` if no prompt has
            ``prompt_id``, in which case nothing is stored.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        """Remove a prompt by id.

        Args:
            prompt_id: Identifier of the prompt to remove.

        Returns:
            ``True`` if a prompt was removed, ``False`` if no prompt had
            that id.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False

    # ============== Collection Operations ==============

    def create_collection(self, collection: Collection) -> Collection:
        """Store a collection under its own id.

        A collection already stored with the same id is replaced without
        warning; the store does not check for duplicates.

        Args:
            collection: The collection to store, with its id already
                assigned.

        Returns:
            The same collection object that was stored.
        """
        self._collections[collection.id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Look up one collection by id.

        Args:
            collection_id: Identifier of the collection to return.

        Returns:
            The stored collection, or ``None`` if no collection has that id.
        """
        return self._collections.get(collection_id)

    def get_all_collections(self) -> List[Collection]:
        """Return every stored collection, in the order they were stored.

        Returns:
            A new list, so adding to or removing from it leaves the store
            unchanged. The collections in it are the stored objects
            themselves.
        """
        return list(self._collections.values())

    def delete_collection(self, collection_id: str) -> bool:
        """Remove a collection by id, leaving its prompts untouched.

        Prompts filed in the collection keep their ``collection_id``; the
        ``DELETE /collections/{collection_id}`` endpoint unfiles them
        afterwards.

        Args:
            collection_id: Identifier of the collection to remove.

        Returns:
            ``True`` if a collection was removed, ``False`` if no
            collection had that id.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False

    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Return the prompts whose ``collection_id`` equals the one given.

        The match is exact, and the collection itself need not exist.
        Passing ``None`` returns the prompts that are in no collection.

        Args:
            collection_id: Identifier of the collection to match.

        Returns:
            A new list of the matching stored prompts, in the order they
            were first stored; empty if none match.
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]

    # ============== Utility ==============

    def clear(self):
        """Remove every prompt and collection.

        Used by the test fixtures to reset the shared store between tests.
        """
        self._prompts.clear()
        self._collections.clear()


# Global storage instance
storage = Storage()
