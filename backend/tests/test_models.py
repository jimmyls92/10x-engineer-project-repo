"""Unit tests for the models and helpers in ``app.models``.

These call the models directly, without HTTP. Each class covers one function
or model, with its cases grouped as the Module 3 brief names them for this
file: validation, defaults and serialization, plus edge cases.
"""

import uuid
from datetime import datetime, timedelta, timezone

from app.models import generate_id, get_current_time


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
