"""Unit tests for ``backend/main.py``, the ``python main.py`` entry point.

The server is never started: ``uvicorn.run`` is replaced, so the tests check
only what ``main.py`` asks uvicorn to do.
"""

import runpy
from pathlib import Path

import uvicorn

MAIN = Path(__file__).resolve().parent.parent / "main.py"


class TestMain:
    """Tests for running ``main.py`` as a script."""

    def test_main_passes_app_as_import_string(self, monkeypatch):
        """Verify ``python main.py`` gives uvicorn the app as an import string.

        With ``reload=True``, uvicorn accepts only an import string; given the
        app object it logs an error and exits with code 1.

        Args:
            monkeypatch: pytest's monkeypatch fixture, used to replace
                ``uvicorn.run`` so no server starts.
        """
        calls = []
        monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

        runpy.run_path(str(MAIN), run_name="__main__")

        assert len(calls) == 1
        args, kwargs = calls[0]
        assert args == ("app.api:app",)
        assert kwargs == {"host": "0.0.0.0", "port": 8000, "reload": True}
