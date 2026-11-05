"""Katmanları doğrudan kuran testler — spec 0004.

Bu senaryolar depoya doğrudan yazmayı ya da saati vermeyi gerektirir; uygulama `app.py`'nin kurduğu
gibi katmanlardan kurulur (docs/testing.md, Fixture sözleşmesi).
"""

from datetime import date

from pages import parse

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
    Mehmet'in (giriş 2019-06-01) 2026-05-29 → 2026-06-02 talebi 3 iş günü: önceki yılın devrinden
    düşülür (90 − 3), bu yılın Kullanılan'ına girmez."""
    repository = InMemoryRepository()
    repository.add_request(2, date(2026, 5, 29), date(2026, 6, 2), "Kapsayan", STATUS_APPROVED)
    rows = LeaveService(repository, today=lambda: date(2026, 10, 25)).balance_rows()
    mehmet = next(row.balance for row in rows if row.employee.id == 2)
    assert (mehmet.carried_over, mehmet.used) == (87, 0)
