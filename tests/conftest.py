"""Ortak fixture'lar (spec 0001, plan 0001).

Testlerin uygulamaya bağlandığı TEK yer burasıdır. Sözleşme (docs/testing.md): `app.py` modül
düzeyinde bir `app` (Flask) nesnesi sunar ve her yüklemede temiz seed verisiyle başlar. Testler
uygulamayla yalnızca HTTP üzerinden konuşur; `app.py`'nin başka hiçbir iç adını kullanmaz.
"""

import importlib
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime

import pytest
import time_machine
from flask.testing import FlaskClient

import app as app_module

# Spec 0001'deki değerlerin gözlendiği gün.
OBSERVED_TODAY = date(2026, 10, 25)


@pytest.fixture(autouse=True)
def no_flask_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Geliştiricinin kabuğundaki `FLASK_DEBUG` ya da `FLASK_RUN_FROM_CLI` testlere sızmasın:
    debug açık uygulama hataları işleyiciye değil teste fırlatır (docs/testing.md)."""
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)


@pytest.fixture
def client_on() -> Iterator[Callable[[date], FlaskClient]]:
    """Verilen günü "bugün" olarak dondurur ve temiz seed verisiyle bir test istemcisi döndürür."""
    travellers: list[time_machine.travel] = []

    def make(today: date) -> FlaskClient:
        # 12:00 UTC: UTC−11…UTC+11 aralığındaki her makinede (yerel UTC+3, CI UTC) aynı gün.
        traveller = time_machine.travel(
            datetime(today.year, today.month, today.day, 12, tzinfo=UTC), tick=False
        )
        traveller.start()
        travellers.append(traveller)
        importlib.reload(app_module)
        return app_module.app.test_client()

    yield make
    for traveller in reversed(travellers):
        traveller.stop()


@pytest.fixture
def client(client_on: Callable[[date], FlaskClient]) -> FlaskClient:
    """Gözlem günü (2026-10-25) için temiz test istemcisi."""
    return client_on(OBSERVED_TODAY)
