"""Unit tests for the models and helpers in ``app.models``.

These call the models directly, without HTTP. Each class covers one function
or model, with its cases grouped as the Module 3 brief names them for this
file: validation, defaults and serialization, plus edge cases.
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models import (
    Collection,
    CollectionBase,
    CollectionCreate,
    CollectionList,
    Prompt,
    PromptBase,
    PromptCreate,
    PromptList,
    PromptPatch,
    PromptUpdate,
    generate_id,
    get_current_time,
)


class TestGenerateId:
    """Tests for ``generate_id``."""

    # --- serialization ---

    def test_generate_id_canonical_string(self):
        """Verify the id is a 36-character string in canonical UUID form."""
        value = generate_id()

        assert isinstance(value, str)
        assert len(value) == 36
        assert str(uuid.UUID(value)) == value

    def test_generate_id_is_version_4(self):
        """Verify the id parses as a version 4 (random) UUID."""
        assert uuid.UUID(generate_id()).version == 4

    # --- edge cases ---

    def test_generate_id_unique(self):
        """Verify 1,000 calls give 1,000 distinct ids."""
        ids = {generate_id() for _ in range(1000)}

        assert len(ids) == 1000


class TestGetCurrentTime:
    """Tests for ``get_current_time``."""

    # --- serialization ---

    def test_get_current_time_is_naive_datetime(self):
        """Verify the value is a ``datetime`` carrying no timezone."""
        value = get_current_time()

        assert isinstance(value, datetime)
        assert value.tzinfo is None

    def test_get_current_time_iso_round_trip(self):
        """Verify the value survives the ISO round trip the API uses for timestamps."""
        value = get_current_time()

        assert datetime.fromisoformat(value.isoformat()) == value

    # --- edge cases ---

    def test_get_current_time_is_utc(self):
        """Verify the value is UTC, not local time.

        Compared with an aware UTC "now" stripped of its zone, so the test does
        not call the deprecated ``utcnow()`` itself.
        """
        expected = datetime.now(timezone.utc).replace(tzinfo=None)

        assert abs(get_current_time() - expected) < timedelta(seconds=2)

    def test_get_current_time_never_goes_backwards(self):
        """Verify two calls in a row give non-decreasing values."""
        first = get_current_time()
        second = get_current_time()

        assert second >= first


class TestPromptBase:
    """Tests for ``PromptBase``, the client fields of a prompt and their constraints."""

    # --- validation ---

    def test_prompt_base_requires_title_and_content(self):
        """Verify both required fields are reported when neither is given."""
        with pytest.raises(ValidationError) as exc:
            PromptBase()

        errors = [(e["loc"], e["msg"]) for e in exc.value.errors()]
        assert errors == [(("title",), "Field required"), (("content",), "Field required")]

    @pytest.mark.parametrize(
        "field, value, msg",
        [
            ("title", "", "String should have at least 1 character"),
            ("title", "a" * 201, "String should have at most 200 characters"),
            ("content", "", "String should have at least 1 character"),
            ("description", "d" * 501, "String should have at most 500 characters"),
        ],
    )
    def test_prompt_base_length_rule_broken(self, field, value, msg):
        """Verify each length constraint raises a ``ValidationError`` on its field.

        Args:
            field: The field given an out-of-range value.
            value: The value that breaks the constraint.
            msg: The message Pydantic reports for it.
        """
        data = {"title": "T", "content": "Text.", field: value}

        with pytest.raises(ValidationError) as exc:
            PromptBase(**data)

        error = exc.value.errors()[0]
        assert error["loc"] == (field,)
        assert error["msg"] == msg

    def test_prompt_base_collection_id_must_be_string(self):
        """Verify a non-string ``collection_id`` is rejected, not coerced."""
        with pytest.raises(ValidationError) as exc:
            PromptBase(title="T", content="Text.", collection_id=5)

        error = exc.value.errors()[0]
        assert error["loc"] == ("collection_id",)
        assert error["msg"] == "Input should be a valid string"

    # --- defaults ---

    def test_prompt_base_optional_fields_default_to_none(self):
        """Verify ``description`` and ``collection_id`` default to ``None``."""
        prompt = PromptBase(title="T", content="Text.")

        assert prompt.description is None
        assert prompt.collection_id is None

    # --- serialization ---

    def test_prompt_base_dump_has_client_fields(self):
        """Verify ``model_dump`` gives exactly the four client fields."""
        dumped = PromptBase(title="T", content="Text.").model_dump()

        assert dumped == {
            "title": "T",
            "content": "Text.",
            "description": None,
            "collection_id": None,
        }

    def test_prompt_base_drops_undeclared_keys(self):
        """Verify a key the model does not declare is dropped, not stored."""
        prompt = PromptBase(title="T", content="Text.", extra="x")

        assert "extra" not in prompt.model_dump()
        assert not hasattr(prompt, "extra")

    # --- edge cases ---

    def test_prompt_base_length_limits_inclusive(self):
        """Verify a title of exactly 200 and a description of exactly 500 are accepted."""
        prompt = PromptBase(title="a" * 200, content="Text.", description="d" * 500)

        assert len(prompt.title) == 200
        assert len(prompt.description) == 500

    def test_prompt_base_empty_description_accepted(self):
        """Verify an empty description is valid, since only a maximum is set."""
        assert PromptBase(title="T", content="Text.", description="").description == ""

    def test_prompt_base_values_not_stripped(self):
        """Verify a title of spaces passes ``min_length=1`` and is kept as sent."""
        assert PromptBase(title="   ", content="Text.").title == "   "


class TestPromptCreate:
    """Tests for ``PromptCreate``, the body of ``POST /prompts``."""

    # --- validation ---

    def test_prompt_create_inherits_base_rules(self):
        """Verify a missing ``title`` is still rejected, so the base rules apply."""
        with pytest.raises(ValidationError) as exc:
            PromptCreate(content="Text.")

        error = exc.value.errors()[0]
        assert error["loc"] == ("title",)
        assert error["msg"] == "Field required"

    # --- serialization ---

    def test_prompt_create_drops_server_fields(self):
        """Verify a client-sent ``id`` or ``created_at`` is dropped from the body."""
        body = PromptCreate(
            title="T", content="Text.", id="mine", created_at="2000-01-01T00:00:00"
        )

        dumped = body.model_dump()
        assert "id" not in dumped
        assert "created_at" not in dumped

    # --- edge cases ---

    def test_prompt_create_same_fields_as_base(self):
        """Verify the create body adds no field of its own to ``PromptBase``."""
        assert issubclass(PromptCreate, PromptBase)
        assert set(PromptCreate.model_fields) == set(PromptBase.model_fields)


class TestPromptUpdate:
    """Tests for ``PromptUpdate``, the full-replacement body of ``PUT /prompts/{id}``."""

    # --- validation ---

    def test_prompt_update_requires_full_body(self):
        """Verify a body without ``content`` is rejected: PUT is not a partial update."""
        with pytest.raises(ValidationError) as exc:
            PromptUpdate(title="T")

        error = exc.value.errors()[0]
        assert error["loc"] == ("content",)
        assert error["msg"] == "Field required"

    # --- defaults ---

    def test_prompt_update_omitted_fields_are_none(self):
        """Verify optional fields left out are ``None``, which is why PUT resets them."""
        body = PromptUpdate(title="T", content="Text.")

        assert body.description is None
        assert body.collection_id is None

    # --- serialization ---

    def test_prompt_update_drops_id(self):
        """Verify a client-sent ``id`` is dropped from the body."""
        assert "id" not in PromptUpdate(title="T", content="Text.", id="mine").model_dump()

    # --- edge cases ---

    def test_prompt_update_same_fields_as_base(self):
        """Verify the replacement body adds no field of its own to ``PromptBase``."""
        assert issubclass(PromptUpdate, PromptBase)
        assert set(PromptUpdate.model_fields) == set(PromptBase.model_fields)


class TestPromptPatch:
    """Tests for ``PromptPatch``, the partial-update body of ``PATCH /prompts/{id}``."""

    # --- validation ---

    @pytest.mark.parametrize("field", ["title", "content"])
    def test_prompt_patch_rejects_null_required_field(self, field):
        """Verify ``reject_null`` refuses an explicit null ``title`` or ``content``.

        Args:
            field: The required field sent as null.
        """
        with pytest.raises(ValidationError) as exc:
            PromptPatch(**{field: None})

        error = exc.value.errors()[0]
        assert error["loc"] == (field,)
        assert error["msg"] == (
            f"Value error, {field} cannot be null; send a value or omit the field "
            "to keep the current one"
        )

    @pytest.mark.parametrize(
        "field, value, msg",
        [
            ("title", "", "String should have at least 1 character"),
            ("title", "a" * 201, "String should have at most 200 characters"),
            ("content", "", "String should have at least 1 character"),
            ("description", "d" * 501, "String should have at most 500 characters"),
        ],
    )
    def test_prompt_patch_length_rule_broken(self, field, value, msg):
        """Verify a sent value is held to the same length rules as ``PromptBase``.

        Args:
            field: The field given an out-of-range value.
            value: The value that breaks the constraint.
            msg: The message Pydantic reports for it.
        """
        with pytest.raises(ValidationError) as exc:
            PromptPatch(**{field: value})

        error = exc.value.errors()[0]
        assert error["loc"] == (field,)
        assert error["msg"] == msg

    # --- defaults ---

    def test_prompt_patch_empty_body_valid(self):
        """Verify an empty body is valid, with every field ``None``."""
        body = PromptPatch()

        assert body.model_dump() == {
            "title": None,
            "content": None,
            "description": None,
            "collection_id": None,
        }

    # --- serialization ---

    def test_prompt_patch_unset_fields_excluded(self):
        """Verify ``exclude_unset`` gives an empty dict for an empty body."""
        assert PromptPatch().model_dump(exclude_unset=True) == {}

    def test_prompt_patch_explicit_null_kept(self):
        """Verify an explicit null is kept by ``exclude_unset``, unlike an absent key.

        This is how ``patch_prompt`` tells "clear this field" from "leave it".
        """
        body = PromptPatch(description=None, collection_id=None)

        assert body.model_dump(exclude_unset=True) == {
            "description": None,
            "collection_id": None,
        }

    def test_prompt_patch_drops_undeclared_keys(self):
        """Verify a key the model does not declare, such as ``id``, is dropped."""
        assert PromptPatch(title="T", id="x").model_dump(exclude_unset=True) == {"title": "T"}

    # --- edge cases ---

    def test_prompt_patch_null_optional_fields_accepted(self):
        """Verify a null ``description`` or ``collection_id`` is valid, unlike a null title."""
        body = PromptPatch(description=None, collection_id=None)

        assert body.description is None
        assert body.collection_id is None


class TestPrompt:
    """Tests for ``Prompt``, the stored record with its server-assigned fields."""

    # --- validation ---

    def test_prompt_inherits_base_rules(self):
        """Verify a missing ``title`` is rejected, so the base rules apply."""
        with pytest.raises(ValidationError) as exc:
            Prompt(content="Text.")

        error = exc.value.errors()[0]
        assert error["loc"] == ("title",)
        assert error["msg"] == "Field required"

    def test_prompt_created_at_must_be_datetime(self):
        """Verify a ``created_at`` that is not a datetime is rejected."""
        with pytest.raises(ValidationError) as exc:
            Prompt(title="T", content="Text.", created_at="nope")

        error = exc.value.errors()[0]
        assert error["loc"] == ("created_at",)
        assert error["msg"] == "Input should be a valid datetime, input is too short"

    # --- defaults ---

    def test_prompt_default_ids_distinct_uuid4(self):
        """Verify each new prompt gets its own version 4 UUID."""
        first = Prompt(title="T", content="Text.")
        second = Prompt(title="T", content="Text.")

        assert first.id != second.id
        assert uuid.UUID(first.id).version == 4

    def test_prompt_default_timestamps(self, ticking_clock):
        """Verify ``created_at`` and ``updated_at`` come from ``get_current_time()``.

        The factories run in field order, so with the ticking clock
        ``created_at`` is its first value and ``updated_at`` the next.

        Args:
            ticking_clock: Makes the clock start at 2026-01-01 and advance
                1 µs per call.
        """
        prompt = Prompt(title="T", content="Text.")

        assert prompt.created_at == datetime(2026, 1, 1)
        assert prompt.updated_at == datetime(2026, 1, 1, 0, 0, 0, 1)

    # --- serialization ---

    def test_prompt_json_timestamps_have_no_timezone(self, ticking_clock):
        """Verify timestamps are written as ISO 8601 with no timezone suffix.

        Args:
            ticking_clock: Makes the timestamps known in advance.
        """
        data = json.loads(Prompt(title="T", content="Text.").model_dump_json())

        assert data["created_at"] == "2026-01-01T00:00:00"
        assert data["updated_at"] == "2026-01-01T00:00:00.000001"

    def test_prompt_dump_round_trip(self):
        """Verify a prompt rebuilt from its own dump is equal to it."""
        prompt = Prompt(title="T", content="Text.", description="D")

        assert Prompt.model_validate(prompt.model_dump()) == prompt

    # --- edge cases ---

    def test_prompt_keeps_given_server_fields(self):
        """Verify a given ``id`` and ``created_at`` are kept, as PUT and PATCH rely on."""
        created_at = datetime(2000, 1, 1)

        prompt = Prompt(title="T", content="Text.", id="given", created_at=created_at)

        assert prompt.id == "given"
        assert prompt.created_at == created_at

    def test_prompt_from_attributes(self):
        """Verify ``model_validate`` builds a prompt from any object with the attributes."""
        source = SimpleNamespace(
            title="T",
            content="Text.",
            description=None,
            collection_id=None,
            id="x",
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )

        prompt = Prompt.model_validate(source)

        assert prompt.id == "x"
        assert prompt.title == "T"


class TestCollectionBase:
    """Tests for ``CollectionBase``, the client fields of a collection."""

    # --- validation ---

    def test_collection_base_requires_name(self):
        """Verify an empty body is rejected for its missing ``name``."""
        with pytest.raises(ValidationError) as exc:
            CollectionBase()

        errors = [(e["loc"], e["msg"]) for e in exc.value.errors()]
        assert errors == [(("name",), "Field required")]

    @pytest.mark.parametrize(
        "field, value, msg",
        [
            ("name", "", "String should have at least 1 character"),
            ("name", "n" * 101, "String should have at most 100 characters"),
            ("description", "d" * 501, "String should have at most 500 characters"),
        ],
    )
    def test_collection_base_length_rule_broken(self, field, value, msg):
        """Verify each length constraint raises a ``ValidationError`` on its field.

        Args:
            field: The field given an out-of-range value.
            value: The value that breaks the constraint.
            msg: The message Pydantic reports for it.
        """
        with pytest.raises(ValidationError) as exc:
            CollectionBase(**{"name": "N", field: value})

        error = exc.value.errors()[0]
        assert error["loc"] == (field,)
        assert error["msg"] == msg

    def test_collection_base_null_name_rejected(self):
        """Verify a null ``name`` is rejected rather than stored."""
        with pytest.raises(ValidationError) as exc:
            CollectionBase(name=None)

        error = exc.value.errors()[0]
        assert error["loc"] == ("name",)
        assert error["msg"] == "Input should be a valid string"

    # --- defaults ---

    def test_collection_base_description_defaults_to_none(self):
        """Verify ``description`` defaults to ``None``."""
        assert CollectionBase(name="N").description is None

    # --- serialization ---

    def test_collection_base_dump_has_client_fields(self):
        """Verify ``model_dump`` gives exactly ``name`` and ``description``."""
        assert CollectionBase(name="N").model_dump() == {"name": "N", "description": None}

    def test_collection_base_drops_undeclared_keys(self):
        """Verify a key the model does not declare is dropped, not stored."""
        assert "extra" not in CollectionBase(name="N", extra="x").model_dump()

    # --- edge cases ---

    def test_collection_base_length_limits_inclusive(self):
        """Verify a name of exactly 100 and a description of exactly 500 are accepted."""
        collection = CollectionBase(name="n" * 100, description="d" * 500)

        assert len(collection.name) == 100
        assert len(collection.description) == 500

    def test_collection_base_empty_description_accepted(self):
        """Verify an empty description is valid, since only a maximum is set."""
        assert CollectionBase(name="N", description="").description == ""


class TestCollectionCreate:
    """Tests for ``CollectionCreate``, the body of ``POST /collections``."""

    # --- validation ---

    def test_collection_create_inherits_base_rules(self):
        """Verify a missing ``name`` is still rejected, so the base rules apply."""
        with pytest.raises(ValidationError) as exc:
            CollectionCreate()

        error = exc.value.errors()[0]
        assert error["loc"] == ("name",)
        assert error["msg"] == "Field required"

    # --- serialization ---

    def test_collection_create_drops_server_fields(self):
        """Verify a client-sent ``id`` or ``created_at`` is dropped from the body."""
        body = CollectionCreate(name="N", id="mine", created_at="2000-01-01T00:00:00")

        dumped = body.model_dump()
        assert "id" not in dumped
        assert "created_at" not in dumped

    # --- edge cases ---

    def test_collection_create_same_fields_as_base(self):
        """Verify the create body adds no field of its own to ``CollectionBase``."""
        assert issubclass(CollectionCreate, CollectionBase)
        assert set(CollectionCreate.model_fields) == set(CollectionBase.model_fields)


class TestCollection:
    """Tests for ``Collection``, the stored collection with its server-assigned fields."""

    # --- validation ---

    def test_collection_inherits_base_rules(self):
        """Verify a missing ``name`` is rejected, so the base rules apply."""
        with pytest.raises(ValidationError) as exc:
            Collection()

        error = exc.value.errors()[0]
        assert error["loc"] == ("name",)
        assert error["msg"] == "Field required"

    def test_collection_created_at_must_be_datetime(self):
        """Verify a ``created_at`` that is not a datetime is rejected."""
        with pytest.raises(ValidationError) as exc:
            Collection(name="N", created_at="nope")

        error = exc.value.errors()[0]
        assert error["loc"] == ("created_at",)
        assert error["msg"] == "Input should be a valid datetime, input is too short"

    # --- defaults ---

    def test_collection_default_ids_distinct_uuid4(self):
        """Verify each new collection gets its own version 4 UUID."""
        first = Collection(name="N")
        second = Collection(name="N")

        assert first.id != second.id
        assert uuid.UUID(first.id).version == 4

    def test_collection_default_created_at(self, ticking_clock):
        """Verify ``created_at`` comes from ``get_current_time()``.

        Args:
            ticking_clock: Makes the clock start at 2026-01-01 and advance
                1 µs per call.
        """
        assert Collection(name="N").created_at == datetime(2026, 1, 1)

    # --- serialization ---

    def test_collection_dump_has_no_updated_at(self):
        """Verify ``model_dump`` gives the client fields plus ``id`` and ``created_at`` only."""
        dumped = Collection(name="N").model_dump()

        assert set(dumped) == {"name", "description", "id", "created_at"}

    def test_collection_dump_round_trip(self):
        """Verify a collection rebuilt from its own dump is equal to it."""
        collection = Collection(name="N", description="D")

        assert Collection.model_validate(collection.model_dump()) == collection

    # --- edge cases ---

    def test_collection_keeps_given_server_fields(self):
        """Verify a given ``id`` and ``created_at`` are kept rather than replaced."""
        created_at = datetime(2000, 1, 1)

        collection = Collection(name="N", id="given", created_at=created_at)

        assert collection.id == "given"
        assert collection.created_at == created_at

    def test_collection_from_attributes(self):
        """Verify ``model_validate`` builds a collection from any object with the attributes."""
        source = SimpleNamespace(
            name="N",
            description=None,
            id="x",
            created_at=datetime(2026, 1, 1),
        )

        collection = Collection.model_validate(source)

        assert collection.id == "x"
        assert collection.name == "N"


class TestPromptList:
    """Tests for ``PromptList``, the response body of ``GET /prompts``."""

    # --- validation ---

    def test_prompt_list_requires_total(self):
        """Verify a list without ``total`` is rejected."""
        with pytest.raises(ValidationError) as exc:
            PromptList(prompts=[])

        errors = [(e["loc"], e["msg"]) for e in exc.value.errors()]
        assert errors == [(("total",), "Field required")]

    def test_prompt_list_invalid_item_rejected(self):
        """Verify an item that is not a valid prompt is rejected at its index."""
        with pytest.raises(ValidationError) as exc:
            PromptList(prompts=[{"content": "Text."}], total=1)

        error = exc.value.errors()[0]
        assert error["loc"] == ("prompts", 0, "title")
        assert error["msg"] == "Field required"

    # --- serialization ---

    def test_prompt_list_dump_nests_full_prompts(self):
        """Verify ``model_dump`` gives ``prompts`` and ``total``, each prompt dumped in full."""
        prompt = Prompt(title="T", content="Text.")

        dumped = PromptList(prompts=[prompt], total=1).model_dump()

        assert dumped == {"prompts": [prompt.model_dump()], "total": 1}

    def test_prompt_list_json_timestamps_have_no_timezone(self, ticking_clock):
        """Verify nested prompt timestamps are written with no timezone suffix.

        Args:
            ticking_clock: Makes the timestamps known in advance.
        """
        body = PromptList(prompts=[Prompt(title="T", content="Text.")], total=1)

        item = json.loads(body.model_dump_json())["prompts"][0]
        assert item["created_at"] == "2026-01-01T00:00:00"
        assert item["updated_at"] == "2026-01-01T00:00:00.000001"

    # --- edge cases ---

    def test_prompt_list_empty(self):
        """Verify an empty list with ``total`` 0 is valid, as a filter matching nothing returns."""
        body = PromptList(prompts=[], total=0)

        assert body.prompts == []
        assert body.total == 0

    def test_prompt_list_total_not_checked(self):
        """Verify a ``total`` that differs from the number of prompts is accepted.

        The model does not compare the two; keeping them equal is left to
        ``list_prompts`` in ``api.py``.
        """
        body = PromptList(prompts=[], total=5)

        assert body.total == 5


class TestCollectionList:
    """Tests for ``CollectionList``, the response body of ``GET /collections``."""

    # --- validation ---

    def test_collection_list_requires_total(self):
        """Verify a list without ``total`` is rejected."""
        with pytest.raises(ValidationError) as exc:
            CollectionList(collections=[])

        errors = [(e["loc"], e["msg"]) for e in exc.value.errors()]
        assert errors == [(("total",), "Field required")]

    def test_collection_list_invalid_item_rejected(self):
        """Verify an item that is not a valid collection is rejected at its index."""
        with pytest.raises(ValidationError) as exc:
            CollectionList(collections=[{"description": "D"}], total=1)

        error = exc.value.errors()[0]
        assert error["loc"] == ("collections", 0, "name")
        assert error["msg"] == "Field required"

    # --- serialization ---

    def test_collection_list_dump_nests_full_collections(self):
        """Verify ``model_dump`` gives ``collections`` and ``total``, each collection in full."""
        collection = Collection(name="N")

        dumped = CollectionList(collections=[collection], total=1).model_dump()

        assert dumped == {"collections": [collection.model_dump()], "total": 1}

    def test_collection_list_json_timestamp_has_no_timezone(self, ticking_clock):
        """Verify a nested ``created_at`` is written with no timezone suffix.

        Args:
            ticking_clock: Makes the timestamp known in advance.
        """
        body = CollectionList(collections=[Collection(name="N")], total=1)

        item = json.loads(body.model_dump_json())["collections"][0]
        assert item["created_at"] == "2026-01-01T00:00:00"

    # --- edge cases ---

    def test_collection_list_empty(self):
        """Verify an empty list with ``total`` 0 is valid, as with no collections stored."""
        body = CollectionList(collections=[], total=0)

        assert body.collections == []
        assert body.total == 0

    def test_collection_list_total_not_checked(self):
        """Verify a ``total`` that differs from the number of collections is accepted.

        The model does not compare the two; keeping them equal is left to
        ``list_collections`` in ``api.py``.
        """
        body = CollectionList(collections=[], total=5)

        assert body.total == 5
