"""Unit tests for the models and helpers in ``app.models``.

These call the models directly, without HTTP. Each class covers one function
or model, with its cases grouped as the Module 3 brief names them for this
file: validation, defaults and serialization, plus edge cases.
"""

import uuid

from app.models import generate_id


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
