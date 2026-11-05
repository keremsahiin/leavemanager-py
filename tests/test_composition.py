"""Katmanları doğrudan kuran testler — spec 0004.

Bu senaryolar depoya doğrudan yazmayı ya da saati vermeyi gerektirir; uygulamayı ya da yalnızca
servisi `app.py`'nin kurduğu gibi katmanlardan kurar (docs/testing.md, Fixture sözleşmesi).
Kayıttaki durum sabitleri (`STATUS_*`) D13'e bağlıdır; o düzeltme bu dosyayı da bilinçli olarak
değiştirir.
"""

from datetime import UTC, date, datetime

import pytest
import time_machine
from pages import parse

from leavemanager import clock
from leavemanager.domain.models import STATUS_APPROVED, STATUS_PENDING
from leavemanager.services import LeaveService
from leavemanager.storage import InMemoryRepository
from leavemanager.web import create_app


def test_security_stored_html_is_escaped_on_output() -> None:
    """docs/security.md, Input & output — kaçışlama kayıtta değil çıktıda yapılır: depoya doğrudan
    yazılan ham HTML da sayfada düz metin görünür."""
    raw_html = "<script>alert(1)</script>"
    repository = InMemoryRepository()
    repository.add_request(2, date(2026, 11, 10), date(2026, 11, 10), raw_html, STATUS_PENDING)
    html = create_app(LeaveService(repository)).test_client().get("/requests").text
    assert raw_html not in html
    assert parse(html).rows[-1][4] == raw_html


@pytest.mark.parametrize(
    ("moment", "today"),
    [
        (datetime(2026, 1, 14, 20, 59, 59, tzinfo=UTC), date(2026, 1, 14)),  # İstanbul 23:59:59
        (datetime(2026, 1, 14, 21, 0, 0, tzinfo=UTC), date(2026, 1, 15)),  # İstanbul 00:00:00
    ],
    ids=["before-midnight", "after-midnight"],
)
def test_today_follows_istanbul_calendar_day(moment: datetime, today: date) -> None:
    """docs/conventions.md, Data rules — "bugün" Europe/Istanbul takvim günüdür. Tarih kışta: yaz
    saati kullanan komşu bölgeler o zaman UTC+2 olduğu için İstanbul'dan ayrılır."""
    with time_machine.travel(moment, tick=False):
        assert clock.today() == today


def test_balance_rows_read_today_once() -> None:
    """Spec 0003 F4 — bakiye tablosu "bugün"ü bir kez okur: gece yarısında satırlar karışmaz."""
    calls = []

    def today() -> date:
        calls.append(today)
        return date(2026, 10, 25)

    LeaveService(InMemoryRepository(), today=today).balance_rows()
    assert len(calls) == 1


def test_br4_request_start_decides_leave_year() -> None:
    """BR-4, spec 0003 R2-2 — yıldönümünü kapsayan onaylı talep başladığı izin yılına yazılır.
    Mehmet'in (giriş 2019-06-01) 2025-05-30 → 2025-06-03 talebi 3 iş günü (aralıkta resmî tatil
    yok, D15'ten bağımsız): önceki yılın devrinden düşülür (70 − 3), Kullanılan'a girmez."""
    repository = InMemoryRepository()
    repository.add_request(2, date(2025, 5, 30), date(2025, 6, 3), "Kapsayan", STATUS_APPROVED)
    rows = LeaveService(repository, today=lambda: date(2025, 10, 25)).balance_rows()
    mehmet = next(row.balance for row in rows if row.employee.id == 2)
    assert (mehmet.carried_over, mehmet.used) == (67, 0)
