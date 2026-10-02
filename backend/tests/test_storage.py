"""Unit tests for the ``Storage`` class in ``app.storage``.

These call a fresh ``Storage`` directly, without HTTP, so no test shares a
store with the API or with another test. Each class covers one method, with
its cases grouped as the Module 3 brief names them for this file: CRUD
operations, persistence within a session, and edge cases.
"""

import pytest

from app.models import Collection, Prompt
from app.storage import Storage


@pytest.fixture
def store():
    """Give each test its own empty ``Storage``.

    Returns:
        A new ``Storage`` with no prompts and no collections.
    """
    return Storage()


class TestCreatePrompt:
    """Tests for ``Storage.create_prompt``, which stores a prompt under its id."""

    # --- CRUD operations ---

    def test_create_prompt_returns_same_object(self, store):
        """Verify the prompt returned is the very object passed in.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = Prompt(title="T", content="Text.")

        assert store.create_prompt(prompt) is prompt

    def test_create_prompt_found_by_id(self, store):
        """Verify a created prompt can be read back by its id.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))

        assert store.get_prompt(prompt.id) is prompt

    # --- persistence within a session ---

    def test_create_prompt_all_kept_in_order(self, store):
        """Verify prompts created one after another are all kept, in creation order.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompts = [Prompt(title=f"T{i}", content="Text.") for i in range(3)]
        for prompt in prompts:
            store.create_prompt(prompt)

        assert store.get_all_prompts() == prompts

    # --- edge cases ---

    def test_create_prompt_same_id_replaces(self, store):
        """Verify a second prompt with the same id replaces the first, without error.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_prompt(Prompt(id="dup", title="First", content="Text."))
        second = store.create_prompt(Prompt(id="dup", title="Second", content="Text."))

        assert store.get_all_prompts() == [second]
        assert store.get_prompt("dup").title == "Second"

    def test_create_prompt_stores_object_not_copy(self, store):
        """Verify changing the returned prompt changes the stored one.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="Before", content="Text."))

        prompt.title = "After"

        assert store.get_prompt(prompt.id).title == "After"


class TestGetPrompt:
    """Tests for ``Storage.get_prompt``, a lookup by id that never raises."""

    # --- CRUD operations ---

    def test_get_prompt_returns_stored(self, store):
        """Verify the prompt stored under an id is the one returned for it.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))
        store.create_prompt(Prompt(title="Other", content="Text."))

        assert store.get_prompt(prompt.id) is prompt

    @pytest.mark.parametrize("others", [0, 2])
    def test_get_prompt_unknown_id_none(self, store, others):
        """Verify an id that names nothing gives ``None`` rather than an error.

        Args:
            store: A fresh, empty ``Storage``.
            others: How many unrelated prompts the store holds.
        """
        for i in range(others):
            store.create_prompt(Prompt(title=f"T{i}", content="Text."))

        assert store.get_prompt("nope") is None

    # --- persistence within a session ---

    def test_get_prompt_same_object_each_time(self, store):
        """Verify repeated lookups give the same object, even after other creates.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))
        first = store.get_prompt(prompt.id)

        store.create_prompt(Prompt(title="Later", content="Text."))

        assert store.get_prompt(prompt.id) is first

    # --- edge cases ---

    def test_get_prompt_after_delete_none(self, store):
        """Verify a deleted prompt can no longer be found.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))
        store.delete_prompt(prompt.id)

        assert store.get_prompt(prompt.id) is None

    def test_get_prompt_id_case_sensitive(self, store):
        """Verify the id must match exactly, so a different case finds nothing.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_prompt(Prompt(id="abc", title="T", content="Text."))

        assert store.get_prompt("ABC") is None


class TestGetAllPrompts:
    """Tests for ``Storage.get_all_prompts``, every prompt in first-stored order."""

    # --- CRUD operations ---

    def test_get_all_prompts_empty_store(self, store):
        """Verify an empty store gives an empty list.

        Args:
            store: A fresh, empty ``Storage``.
        """
        assert store.get_all_prompts() == []

    def test_get_all_prompts_in_stored_order(self, store):
        """Verify every stored prompt is returned, in the order it was stored.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompts = [Prompt(title=t, content="Text.") for t in ("b", "c", "a")]
        for prompt in prompts:
            store.create_prompt(prompt)

        assert store.get_all_prompts() == prompts

    # --- persistence within a session ---

    def test_get_all_prompts_replaced_keeps_place(self, store):
        """Verify a prompt replaced by ``update_prompt`` stays where it was first stored.

        Args:
            store: A fresh, empty ``Storage``.
        """
        first = store.create_prompt(Prompt(title="first", content="Text."))
        second = store.create_prompt(Prompt(title="second", content="Text."))
        replacement = Prompt(id=first.id, title="replaced", content="Text.")

        store.update_prompt(first.id, replacement)

        assert store.get_all_prompts() == [replacement, second]

    def test_get_all_prompts_deleted_not_listed(self, store):
        """Verify a deleted prompt is no longer listed and the others remain.

        Args:
            store: A fresh, empty ``Storage``.
        """
        kept = store.create_prompt(Prompt(title="kept", content="Text."))
        gone = store.create_prompt(Prompt(title="gone", content="Text."))

        store.delete_prompt(gone.id)

        assert store.get_all_prompts() == [kept]

    # --- edge cases ---

    def test_get_all_prompts_list_is_new(self, store):
        """Verify adding to or removing from the returned list leaves the store unchanged.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))

        listed = store.get_all_prompts()
        listed.append(Prompt(title="Extra", content="Text."))
        listed.remove(prompt)

        assert store.get_all_prompts() == [prompt]

    def test_get_all_prompts_items_are_stored_objects(self, store):
        """Verify the listed prompts are the stored objects, not copies.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))

        assert store.get_all_prompts()[0] is prompt


class TestUpdatePrompt:
    """Tests for ``Storage.update_prompt``, which replaces an existing prompt."""

    # --- CRUD operations ---

    def test_update_prompt_replaces_existing(self, store):
        """Verify the new version is stored, returned and found by id.

        Args:
            store: A fresh, empty ``Storage``.
        """
        original = store.create_prompt(Prompt(title="Old", content="Text."))
        replacement = Prompt(id=original.id, title="New", content="Text.")

        result = store.update_prompt(original.id, replacement)

        assert result is replacement
        assert store.get_prompt(original.id) is replacement

    def test_update_prompt_unknown_id_none(self, store):
        """Verify an unknown id gives ``None`` and stores nothing.

        Args:
            store: A fresh, empty ``Storage``.
        """
        result = store.update_prompt("nope", Prompt(id="nope", title="T", content="Text."))

        assert result is None
        assert store.get_all_prompts() == []

    # --- persistence within a session ---

    def test_update_prompt_persists_without_new_record(self, store):
        """Verify the replacement stays after other creates, with no record added.

        Args:
            store: A fresh, empty ``Storage``.
        """
        original = store.create_prompt(Prompt(title="Old", content="Text."))
        replacement = Prompt(id=original.id, title="New", content="Text.")
        store.update_prompt(original.id, replacement)

        store.create_prompt(Prompt(title="Later", content="Text."))

        assert store.get_prompt(original.id) is replacement
        assert len(store.get_all_prompts()) == 2

    # --- edge cases ---

    def test_update_prompt_mismatched_id_stored_under_path_id(self, store):
        """Verify a prompt whose ``id`` differs is kept under ``prompt_id``, unchecked.

        The record then reports an id that no lookup finds. The API avoids
        this by copying ``existing.id`` into every replacement.

        Args:
            store: A fresh, empty ``Storage``.
        """
        original = store.create_prompt(Prompt(id="path-id", title="Old", content="Text."))
        mismatched = Prompt(id="other-id", title="New", content="Text.")

        result = store.update_prompt(original.id, mismatched)

        assert result is mismatched
        assert store.get_prompt("path-id") is mismatched
        assert store.get_prompt("path-id").id == "other-id"
        assert store.get_prompt("other-id") is None

    def test_update_prompt_deleted_not_restored(self, store):
        """Verify a deleted prompt is not brought back by updating it.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))
        store.delete_prompt(prompt.id)

        result = store.update_prompt(prompt.id, prompt)

        assert result is None
        assert store.get_prompt(prompt.id) is None


class TestDeletePrompt:
    """Tests for ``Storage.delete_prompt``, which reports whether it removed anything."""

    # --- CRUD operations ---

    def test_delete_prompt_existing_true(self, store):
        """Verify an existing prompt is removed and ``True`` returned.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))

        assert store.delete_prompt(prompt.id) is True
        assert store.get_prompt(prompt.id) is None

    def test_delete_prompt_unknown_false(self, store):
        """Verify an unknown id gives ``False`` rather than an error.

        Args:
            store: A fresh, empty ``Storage``.
        """
        assert store.delete_prompt("nope") is False

    # --- persistence within a session ---

    def test_delete_prompt_others_untouched(self, store):
        """Verify deleting one prompt leaves the others stored.

        Args:
            store: A fresh, empty ``Storage``.
        """
        first = store.create_prompt(Prompt(title="first", content="Text."))
        gone = store.create_prompt(Prompt(title="gone", content="Text."))
        last = store.create_prompt(Prompt(title="last", content="Text."))

        store.delete_prompt(gone.id)

        assert store.get_all_prompts() == [first, last]

    def test_delete_prompt_twice(self, store):
        """Verify a second delete of the same id finds nothing and gives ``False``.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))

        assert store.delete_prompt(prompt.id) is True
        assert store.delete_prompt(prompt.id) is False

    # --- edge cases ---

    def test_delete_prompt_id_reusable_listed_last(self, store):
        """Verify a deleted id can be created again, and the new record is listed last.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_prompt(Prompt(id="reused", title="Old", content="Text."))
        other = store.create_prompt(Prompt(title="Other", content="Text."))
        store.delete_prompt("reused")

        recreated = store.create_prompt(Prompt(id="reused", title="New", content="Text."))

        assert store.get_all_prompts() == [other, recreated]


class TestCreateCollection:
    """Tests for ``Storage.create_collection``, which stores a collection under its id."""

    # --- CRUD operations ---

    def test_create_collection_returns_same_object(self, store):
        """Verify the collection returned is the very object passed in.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = Collection(name="N")

        assert store.create_collection(collection) is collection

    def test_create_collection_found_by_id(self, store):
        """Verify a created collection can be read back by its id.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))

        assert store.get_collection(collection.id) is collection

    # --- persistence within a session ---

    def test_create_collection_all_kept_in_order(self, store):
        """Verify collections created one after another are all kept, in creation order.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collections = [Collection(name=f"N{i}") for i in range(3)]
        for collection in collections:
            store.create_collection(collection)

        assert store.get_all_collections() == collections

    # --- edge cases ---

    def test_create_collection_same_id_replaces(self, store):
        """Verify a second collection with the same id replaces the first, without error.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_collection(Collection(id="dup", name="First"))
        second = store.create_collection(Collection(id="dup", name="Second"))

        assert store.get_all_collections() == [second]
        assert store.get_collection("dup").name == "Second"

    def test_create_collection_stores_object_not_copy(self, store):
        """Verify changing the returned collection changes the stored one.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="Before"))

        collection.name = "After"

        assert store.get_collection(collection.id).name == "After"

    def test_create_collection_id_shared_with_prompt(self, store):
        """Verify a prompt and a collection with the same id are kept apart.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(id="same", title="T", content="Text."))
        collection = store.create_collection(Collection(id="same", name="N"))

        assert store.get_prompt("same") is prompt
        assert store.get_collection("same") is collection


class TestGetCollection:
    """Tests for ``Storage.get_collection``, a lookup by id that never raises."""

    # --- CRUD operations ---

    def test_get_collection_returns_stored(self, store):
        """Verify the collection stored under an id is the one returned for it.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))
        store.create_collection(Collection(name="Other"))

        assert store.get_collection(collection.id) is collection

    @pytest.mark.parametrize("others", [0, 2])
    def test_get_collection_unknown_id_none(self, store, others):
        """Verify an id that names nothing gives ``None`` rather than an error.

        Args:
            store: A fresh, empty ``Storage``.
            others: How many unrelated collections the store holds.
        """
        for i in range(others):
            store.create_collection(Collection(name=f"N{i}"))

        assert store.get_collection("nope") is None

    # --- persistence within a session ---

    def test_get_collection_same_object_each_time(self, store):
        """Verify repeated lookups give the same object, even after other creates.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))
        first = store.get_collection(collection.id)

        store.create_collection(Collection(name="Later"))

        assert store.get_collection(collection.id) is first

    # --- edge cases ---

    def test_get_collection_after_delete_none(self, store):
        """Verify a deleted collection can no longer be found.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))
        store.delete_collection(collection.id)

        assert store.get_collection(collection.id) is None

    def test_get_collection_id_case_sensitive(self, store):
        """Verify the id must match exactly, so a different case finds nothing.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_collection(Collection(id="abc", name="N"))

        assert store.get_collection("ABC") is None


class TestGetAllCollections:
    """Tests for ``Storage.get_all_collections``, every collection in stored order."""

    # --- CRUD operations ---

    def test_get_all_collections_empty_store(self, store):
        """Verify an empty store gives an empty list.

        Args:
            store: A fresh, empty ``Storage``.
        """
        assert store.get_all_collections() == []

    def test_get_all_collections_in_stored_order(self, store):
        """Verify every stored collection is returned, in the order it was stored.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collections = [Collection(name=n) for n in ("b", "c", "a")]
        for collection in collections:
            store.create_collection(collection)

        assert store.get_all_collections() == collections

    # --- persistence within a session ---

    def test_get_all_collections_deleted_not_listed(self, store):
        """Verify a deleted collection is no longer listed and the others remain.

        Args:
            store: A fresh, empty ``Storage``.
        """
        kept = store.create_collection(Collection(name="kept"))
        gone = store.create_collection(Collection(name="gone"))

        store.delete_collection(gone.id)

        assert store.get_all_collections() == [kept]

    def test_get_all_collections_excludes_prompts(self, store):
        """Verify stored prompts never appear among the collections.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))
        store.create_prompt(Prompt(title="T", content="Text."))

        assert store.get_all_collections() == [collection]

    # --- edge cases ---

    def test_get_all_collections_list_is_new(self, store):
        """Verify adding to or removing from the returned list leaves the store unchanged.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))

        listed = store.get_all_collections()
        listed.append(Collection(name="Extra"))
        listed.remove(collection)

        assert store.get_all_collections() == [collection]

    def test_get_all_collections_items_are_stored_objects(self, store):
        """Verify the listed collections are the stored objects, not copies.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))

        assert store.get_all_collections()[0] is collection


class TestDeleteCollection:
    """Tests for ``Storage.delete_collection``, which removes only the collection."""

    # --- CRUD operations ---

    def test_delete_collection_existing_true(self, store):
        """Verify an existing collection is removed and ``True`` returned.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))

        assert store.delete_collection(collection.id) is True
        assert store.get_collection(collection.id) is None

    def test_delete_collection_unknown_false(self, store):
        """Verify an unknown id gives ``False`` rather than an error.

        Args:
            store: A fresh, empty ``Storage``.
        """
        assert store.delete_collection("nope") is False

    # --- persistence within a session ---

    def test_delete_collection_others_untouched(self, store):
        """Verify deleting one collection leaves the others stored.

        Args:
            store: A fresh, empty ``Storage``.
        """
        first = store.create_collection(Collection(name="first"))
        gone = store.create_collection(Collection(name="gone"))
        last = store.create_collection(Collection(name="last"))

        store.delete_collection(gone.id)

        assert store.get_all_collections() == [first, last]

    def test_delete_collection_twice(self, store):
        """Verify a second delete of the same id finds nothing and gives ``False``.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))

        assert store.delete_collection(collection.id) is True
        assert store.delete_collection(collection.id) is False

    # --- edge cases ---

    def test_delete_collection_prompts_keep_collection_id(self, store):
        """Verify prompts filed in the collection are left as they are.

        Unfiling them is the job of ``DELETE /collections/{collection_id}``,
        which runs after this method; storage alone leaves the stale id.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))
        prompt = store.create_prompt(
            Prompt(title="T", content="Text.", collection_id=collection.id)
        )

        store.delete_collection(collection.id)

        assert store.get_prompt(prompt.id).collection_id == collection.id

    def test_delete_collection_same_id_prompt_kept(self, store):
        """Verify a prompt sharing the deleted collection's id is not removed.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(id="same", title="T", content="Text."))
        store.create_collection(Collection(id="same", name="N"))

        store.delete_collection("same")

        assert store.get_prompt("same") is prompt


class TestGetPromptsByCollection:
    """Tests for ``Storage.get_prompts_by_collection``, an exact match on ``collection_id``."""

    # --- CRUD operations ---

    def test_get_prompts_by_collection_in_stored_order(self, store):
        """Verify only the prompts in the collection are returned, in stored order.

        Args:
            store: A fresh, empty ``Storage``.
        """
        a1 = store.create_prompt(Prompt(title="a1", content="Text.", collection_id="col-a"))
        store.create_prompt(Prompt(title="b1", content="Text.", collection_id="col-b"))
        a2 = store.create_prompt(Prompt(title="a2", content="Text.", collection_id="col-a"))
        store.create_prompt(Prompt(title="none", content="Text."))

        assert store.get_prompts_by_collection("col-a") == [a1, a2]

    def test_get_prompts_by_collection_unknown_empty(self, store):
        """Verify an id that no prompt has gives an empty list.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_prompt(Prompt(title="T", content="Text.", collection_id="col-a"))

        assert store.get_prompts_by_collection("nope") == []

    # --- persistence within a session ---

    def test_get_prompts_by_collection_reflects_changes(self, store):
        """Verify the result follows prompts created and deleted since the last call.

        Args:
            store: A fresh, empty ``Storage``.
        """
        first = store.create_prompt(Prompt(title="first", content="Text.", collection_id="c"))
        assert store.get_prompts_by_collection("c") == [first]

        second = store.create_prompt(Prompt(title="second", content="Text.", collection_id="c"))
        store.delete_prompt(first.id)

        assert store.get_prompts_by_collection("c") == [second]

    def test_get_prompts_by_collection_after_collection_deleted(self, store):
        """Verify a deleted collection's prompts are still found by its id.

        ``DELETE /collections/{collection_id}`` relies on this to find the
        prompts it must unfile after the collection is gone.

        Args:
            store: A fresh, empty ``Storage``.
        """
        collection = store.create_collection(Collection(name="N"))
        prompt = store.create_prompt(
            Prompt(title="T", content="Text.", collection_id=collection.id)
        )

        store.delete_collection(collection.id)

        assert store.get_prompts_by_collection(collection.id) == [prompt]

    # --- edge cases ---

    def test_get_prompts_by_collection_none_unfiled(self, store):
        """Verify ``None`` returns the prompts that are in no collection.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_prompt(Prompt(title="filed", content="Text.", collection_id="c"))
        unfiled = store.create_prompt(Prompt(title="unfiled", content="Text."))

        assert store.get_prompts_by_collection(None) == [unfiled]

    def test_get_prompts_by_collection_empty_string_not_none(self, store):
        """Verify ``""`` matches only prompts stored with ``""``, not those with ``None``.

        Args:
            store: A fresh, empty ``Storage``.
        """
        empty = store.create_prompt(Prompt(title="empty", content="Text.", collection_id=""))
        store.create_prompt(Prompt(title="unfiled", content="Text."))

        assert store.get_prompts_by_collection("") == [empty]

    def test_get_prompts_by_collection_safe_to_update_while_looping(self, store):
        """Verify the matched prompts can be replaced while looping over the result.

        This is what ``DELETE /collections/{collection_id}`` does to unfile
        them. Each replacement reuses an existing key, so the store's size
        never changes during the loop.

        Args:
            store: A fresh, empty ``Storage``.
        """
        for i in range(3):
            store.create_prompt(Prompt(title=f"T{i}", content="Text.", collection_id="c"))

        for prompt in store.get_prompts_by_collection("c"):
            store.update_prompt(
                prompt.id, prompt.model_copy(update={"collection_id": None})
            )

        assert store.get_prompts_by_collection("c") == []
        assert len(store.get_prompts_by_collection(None)) == 3


class TestClear:
    """Tests for ``Storage.clear``, which empties both prompts and collections."""

    # --- CRUD operations ---

    def test_clear_removes_everything(self, store):
        """Verify every prompt and every collection is removed.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))
        collection = store.create_collection(Collection(name="N"))

        store.clear()

        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []
        assert store.get_prompt(prompt.id) is None
        assert store.get_collection(collection.id) is None

    # --- persistence within a session ---

    def test_clear_store_usable_after(self, store):
        """Verify records created after a clear are stored and found as usual.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.create_prompt(Prompt(title="Before", content="Text."))
        store.clear()

        prompt = store.create_prompt(Prompt(title="After", content="Text."))
        collection = store.create_collection(Collection(name="After"))

        assert store.get_all_prompts() == [prompt]
        assert store.get_all_collections() == [collection]

    # --- edge cases ---

    def test_clear_empty_store(self, store):
        """Verify clearing a store that holds nothing raises no error.

        Args:
            store: A fresh, empty ``Storage``.
        """
        store.clear()

        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []

    def test_clear_earlier_list_keeps_items(self, store):
        """Verify a list read before the clear still holds its prompts.

        Args:
            store: A fresh, empty ``Storage``.
        """
        prompt = store.create_prompt(Prompt(title="T", content="Text."))
        listed = store.get_all_prompts()

        store.clear()

        assert listed == [prompt]
