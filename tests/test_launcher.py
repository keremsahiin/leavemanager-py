"""`python app.py` başlatıcısı — docs/security.md, Input & output.

`app.py` script olarak çalıştırılır; Flask'in kendi `run` mantığı (ortam değişkenleri dahil) işler,
yalnızca Werkzeug'un gerçek sunucusu yerine `run_simple` çağrısı yakalanır.
"""

import runpy
from pathlib import Path

import pytest
import werkzeug.serving

APP_PY = Path(__file__).resolve().parent.parent / "app.py"


@pytest.mark.parametrize(
    ("flask_debug", "debug"),
    [(None, False), ("1", True)],
    ids=["default", "flask-debug"],
)
def test_security_launcher_enables_debug_only_with_flask_debug(
    monkeypatch: pytest.MonkeyPatch, flask_debug: str | None, debug: bool
) -> None:
    """Debug (Werkzeug debugger, yeniden yükleyici) kodda açılmaz, yalnızca `FLASK_DEBUG=1` ile."""
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(werkzeug.serving, "run_simple", lambda *a, **kw: calls.append((a, kw)))
    if flask_debug is not None:
        monkeypatch.setenv("FLASK_DEBUG", flask_debug)
    namespace = runpy.run_path(str(APP_PY), run_name="__main__")
    assert len(calls) == 1
    args, options = calls[0]
    assert args[:2] == ("127.0.0.1", 5000)
    assert namespace["app"].debug is debug
    assert options["use_debugger"] is debug
    assert options["use_reloader"] is debug


@pytest.mark.parametrize("secret_key", [None, ""], ids=["unset", "empty"])
def test_security_launcher_requires_secret_key(
    monkeypatch: pytest.MonkeyPatch, secret_key: str | None
) -> None:
    """`SECRET_KEY` kodda varsayılan değer taşımaz: ortamda yoksa ya da boşsa (`.env.example`
    olduğu gibi kullanılmışsa) uygulama başlamaz."""
    calls: list[object] = []
    monkeypatch.setattr(werkzeug.serving, "run_simple", lambda *a, **kw: calls.append(a))
    if secret_key is None:
        monkeypatch.delenv("SECRET_KEY")
    else:
        monkeypatch.setenv("SECRET_KEY", secret_key)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        runpy.run_path(str(APP_PY), run_name="__main__")
    assert calls == []
