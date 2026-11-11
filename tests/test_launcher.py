"""`python app.py` başlatıcısı — docs/security.md, Input & output.

`app.py` script olarak çalıştırılır; Flask'in gerçek sunucusu yerine `run` çağrısı yakalanır.
"""

import runpy
from pathlib import Path

import pytest
from flask import Flask

APP_PY = Path(__file__).resolve().parent.parent / "app.py"


def test_security_launcher_does_not_force_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    """Debug kodda açılmaz: `debug` verilmediğinde Flask yalnızca `FLASK_DEBUG`'a uyar."""
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(Flask, "run", lambda self, *args, **kwargs: calls.append(kwargs))
    runpy.run_path(str(APP_PY), run_name="__main__")
    assert len(calls) == 1
    assert "debug" not in calls[0]
    assert calls[0]["port"] == 5000
