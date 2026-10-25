"""Ana sayfa (`/`) karakterizasyonu — spec 0001, PB-1…PB-4.

`test_d<n>_` ile başlayan testler bilinen bir sapmanın BUGÜNKÜ davranışını sabitler
(docs/domain.md, Known deviations). O sapmanın düzeltmesi testi bilinçli olarak değiştirir.
"""

from collections.abc import Callable
from datetime import date

import pytest
from flask.testing import FlaskClient
from pages import counter, parse

AYSE = "Ayse Yilmaz"  # işe giriş 2008-03-15
ZEYNEP = "Zeynep Kaya"  # işe giriş 2024-11-10

SEED_BALANCES = [  # Ad, Birim, Hak, Kullanılan, Kalan — bugün 2026-10-25
    ["Ayse Yilmaz", "IT", "26", "12", "14"],
    ["Mehmet Demir", "Muhasebe", "20", "0", "20"],
    ["Zeynep Kaya", "IK", "14", "0", "14"],
    ["Ahmet Celik", "IT", "20", "0", "20"],
    ["Elif Sahin", "Satis", "0", "0", "0"],
]


def balances(client: FlaskClient) -> dict[str, tuple[int, int, int]]:
    """Bakiye tablosu: ad -> (Hak, Kullanılan, Kalan)."""
    rows = parse(client.get("/").text).rows
    return {row[0]: (int(row[2]), int(row[3]), int(row[4])) for row in rows}


def test_counters_with_seed_data(client: FlaskClient) -> None:
    """PB-1."""
    page = parse(client.get("/").text)
    assert counter(page, "Bekleyen") == 4
    assert counter(page, "Onaylanan") == 1
    assert counter(page, "Reddedilen") == 3


def test_balance_table_with_seed_data(client: FlaskClient) -> None:
    """PB-2."""
    response = client.get("/")
    assert response.status_code == 200
    page = parse(response.text)
    assert page.headers == [["Ad", "Birim", "Hak", "Kullanilan", "Kalan"]]
    assert page.rows == SEED_BALANCES


@pytest.mark.parametrize(
    ("today", "entitlement"),
    [
        (date(2008, 12, 31), 0),  # kıdem 0
        (date(2013, 6, 1), 14),  # kıdem 5
        (date(2014, 6, 1), 20),  # kıdem 6
        (date(2024, 1, 1), 26),  # yıl farkı 16
        (date(2024, 6, 1), 26),  # kıdem 16
    ],
)
def test_entitlement_by_calendar_year_seniority(
    client_on: Callable[[date], FlaskClient], today: date, entitlement: int
) -> None:
    """PB-3 — sapmanın görünmediği noktalar: hak tablosu sınırları."""
    assert balances(client_on(today))[AYSE][0] == entitlement


def test_d2_15_years_gives_20_days(client_on: Callable[[date], FlaskClient]) -> None:
    """PB-3 — bilinen sapma D2 (docs/domain.md): 15 yıl kıdeme 20 gün (BR-1: 26).

    Bugünkü davranışı sabitler; D2 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    assert balances(client_on(date(2023, 12, 31)))[AYSE][0] == 20


@pytest.mark.parametrize(
    ("name", "today", "entitlement"),
    [
        (AYSE, date(2009, 1, 1), 14),  # yıl farkı 1, tamamlanan yıl 0
        (AYSE, date(2014, 1, 1), 20),  # yıl farkı 6, tamamlanan yıl 5
        (ZEYNEP, date(2025, 1, 2), 14),  # yıl farkı 1, tamamlanan yıl 0
    ],
)
def test_d3_seniority_counts_calendar_years_only(
    client_on: Callable[[date], FlaskClient], name: str, today: date, entitlement: int
) -> None:
    """PB-3 — bilinen sapma D3 (docs/domain.md): kıdem takvim yılı farkı (BR-2: yıldönümü).

    Bugünkü davranışı sabitler; D3 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    assert balances(client_on(today))[name][0] == entitlement


@pytest.mark.parametrize("today", [date(2009, 1, 1), date(2027, 1, 1)])
def test_d11_used_days_include_future_approved_requests(
    client_on: Callable[[date], FlaskClient], today: date
) -> None:
    """PB-4 — bilinen sapmalar D11 ve D4 (docs/domain.md): Kullanılan, onaylı tüm taleplerin
    takvim günü toplamı; yıl ayrımı yok, gelecekteki talep de sayılır. Ayse'nin onaylı talebi
    2026-07-06 → 2026-07-17: 12 takvim günü (10 iş günü).

    Bugünkü davranışı sabitler; D11 / D4 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    assert balances(client_on(today))[AYSE][1] == 12


def test_d5_pending_days_not_deducted(client: FlaskClient) -> None:
    """PB-4 — bilinen sapma D5 (docs/domain.md): bekleyen talepler bakiyeden düşülmez.
    Ayse'nin 3 günlük, Mehmet'in 3 günlük bekleyen talebi var; Kalan = Hak − Kullanılan.

    Bugünkü davranışı sabitler; D5 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    table = balances(client)
    assert table[AYSE] == (26, 12, 14)
    assert table["Mehmet Demir"] == (20, 0, 20)


def test_d14_remaining_can_go_negative(client_on: Callable[[date], FlaskClient]) -> None:
    """PB-4 — bilinen sapma D14 (docs/domain.md): Kalan negatife düşebilir (I-1 ihlali).

    Bugünkü davranışı sabitler; D14 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    assert balances(client_on(date(2008, 12, 31)))[AYSE] == (0, 12, -12)
