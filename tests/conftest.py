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
from pages import parse

# Spec 0001'deki değerlerin gözlendiği gün.
OBSERVED_TODAY = date(2026, 10, 25)

# Yalnızca testler için; gerçek anahtar ortam değişkeninden gelir (docs/security.md).
TEST_SECRET_KEY = "yalnizca-testler-icin"  # noqa: S105 — sır değil, yalnızca test değeri


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Geliştiricinin kabuğundaki `FLASK_DEBUG` ya da `FLASK_RUN_FROM_CLI` testlere sızmasın
    (debug açık uygulama hataları işleyiciye değil teste fırlatır); `SECRET_KEY` sabit bir test
    değeridir (docs/testing.md)."""
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
    monkeypatch.setenv("SECRET_KEY", TEST_SECRET_KEY)


class FormClient(FlaskClient):
    """Tarayıcı gibi davranır: POST'tan önce formu açar ve formdaki gizli alanları (CSRF token'ı)
    gönderir. CSRF'nin kendisi `raw_client` ile sınanır.

    Sınır: token'ı her zaman `/new`'den alır. İkinci bir POST formu eklenince token o formun kendi
    sayfasından alınmalı; yoksa token'sız bir form testlerde fark edilmez."""

    def post(self, *args, **kwargs):
        hidden = parse(self.get("/new").text).hidden
        kwargs["data"] = {**hidden, **(kwargs.get("data") or {})}
        return super().post(*args, **kwargs)


@pytest.fixture
def client_on() -> Iterator[Callable[..., FlaskClient]]:
    """Verilen günü "bugün" olarak dondurur ve temiz seed verisiyle bir test istemcisi döndürür."""
    travellers: list[time_machine.travel] = []

    def make(today: date, client_class: type[FlaskClient] = FormClient) -> FlaskClient:
        # 12:00 UTC: UTC−11…UTC+11 aralığındaki her makinede (yerel UTC+3, CI UTC) aynı gün.
        traveller = time_machine.travel(
            datetime(today.year, today.month, today.day, 12, tzinfo=UTC), tick=False
        )
        traveller.start()
        travellers.append(traveller)
        # İçe aktarma fixture'da: app.py SECRET_KEY'i yüklenirken okur (clean_environment).
        app_module = importlib.reload(importlib.import_module("app"))
        app_module.app.test_client_class = client_class
        return app_module.app.test_client()

    yield make
    for traveller in reversed(travellers):
        traveller.stop()


@pytest.fixture
def client(client_on: Callable[..., FlaskClient]) -> FlaskClient:
    """Gözlem günü (2026-10-25) için temiz test istemcisi; formları tarayıcı gibi gönderir."""
    return client_on(OBSERVED_TODAY)


@pytest.fixture
def raw_client(client_on: Callable[..., FlaskClient]) -> FlaskClient:
    """Gözlem günü için yalnızca gönderileni gönderen istemci: CSRF reddini sınamak için."""
    return client_on(OBSERVED_TODAY, FlaskClient)
