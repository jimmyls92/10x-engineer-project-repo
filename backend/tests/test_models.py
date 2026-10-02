"""Unit tests for the models and helpers in ``app.models``.

These call the models directly, without HTTP. Each class covers one function
or model, with its cases grouped as the Module 3 brief names them for this
file: validation, defaults and serialization, plus edge cases.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.models import (
    PromptBase,
    PromptCreate,
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
