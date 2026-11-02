"""Ana sayfa (`/`) — spec 0001 PB-1…PB-4; spec 0002 CB-1 (kıdem) ve CB-2 (iş günü).

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
AHMET = "Ahmet Celik"  # işe giriş 2020-02-29

SEED_BALANCES = [  # Ad, Birim, Hak, Kullanılan, Kalan — bugün 2026-10-25
    ["Ayse Yilmaz", "IT", "26", "10", "16"],
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
    """PB-2; spec 0002 CB-2 (Kullanılan iş günü). Değerler D5'e (Kalan'dan bekleyen düşülmez)
    bağlıdır; o düzeltme bu beklentiyi de bilinçli olarak değiştirir (docs/domain.md)."""
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
        (date(2024, 6, 1), 26),  # kıdem 16
    ],
)
def test_br1_entitlement_by_seniority(
    client_on: Callable[[date], FlaskClient], today: date, entitlement: int
) -> None:
    """BR-1 — sapmanın görünmediği noktalar: hak tablosu sınırları (0001/PB-3)."""
    assert balances(client_on(today))[AYSE][0] == entitlement


@pytest.mark.parametrize(
    ("name", "today"),
    [
        (AYSE, date(2023, 12, 31)),
        (AYSE, date(2024, 3, 14)),  # 16. yıldönümünden bir gün önce
        (AHMET, date(2036, 2, 28)),  # artık yıl: 16. yıl 29 Şubat'ta dolar
    ],
)
def test_d2_15_years_gives_20_days(
    client_on: Callable[[date], FlaskClient], name: str, today: date
) -> None:
    """Bilinen sapma D2 (docs/domain.md): 15 yıl kıdeme 20 gün (BR-1: 26). Üç noktada da
    kıdem 15.

    Bugünkü davranışı sabitler; D2 düzeltmesi bu testi bilinçli olarak değiştirir. Ahmet
    noktası, artık yıldaki 29 Şubat sınırının Hak sütunundaki tek kanıtıdır (plan 0002, A1).
    """
    assert balances(client_on(today))[name][0] == 20


@pytest.mark.parametrize(
    ("name", "today", "entitlement"),
    [
        (AYSE, date(2009, 3, 14), 0),  # 1. yıldönümünden bir gün önce: kıdem 0
        (AYSE, date(2009, 3, 15), 14),  # yıldönümü günü yıl dolar: kıdem 1
        (AYSE, date(2014, 3, 14), 14),  # kıdem 5
        (AYSE, date(2014, 3, 15), 20),  # kıdem 6
        (AYSE, date(2024, 3, 15), 26),  # kıdem 16
        (ZEYNEP, date(2025, 11, 9), 0),  # kıdem 0
        (ZEYNEP, date(2025, 11, 10), 14),  # kıdem 1
    ],
)
def test_br2_seniority_completes_on_hire_anniversary(
    client_on: Callable[[date], FlaskClient], name: str, today: date, entitlement: int
) -> None:
    """BR-2, spec 0002 CB-1 — kıdem işe giriş yıldönümünde dolan tam yıl sayısıdır."""
    assert balances(client_on(today))[name][0] == entitlement


@pytest.mark.parametrize(
    ("today", "entitlement"),
    [
        (date(2021, 2, 27), 0),  # artık olmayan yıl: 1. yıl 28 Şubat'ta dolar
        (date(2021, 2, 28), 14),
        (date(2026, 2, 27), 14),  # kıdem 5
        (date(2026, 2, 28), 20),  # kıdem 6
        (date(2036, 2, 29), 26),  # artık yıl: 16. yıl 29 Şubat'ta dolar (önceki gün: test_d2_)
    ],
)
def test_br2_feb29_hire_anniversary(
    client_on: Callable[[date], FlaskClient], today: date, entitlement: int
) -> None:
    """BR-2, spec 0002 CB-1 — 29 Şubat'ta işe girenin (Ahmet) yılı artık olmayan yıllarda
    28 Şubat'ta, artık yıllarda 29 Şubat'ta dolar."""
    assert balances(client_on(today))[AHMET][0] == entitlement


@pytest.mark.parametrize("today", [date(2009, 1, 1), date(2027, 1, 1)])
def test_d11_used_days_include_future_approved_requests(
    client_on: Callable[[date], FlaskClient], today: date
) -> None:
    """PB-4 — bilinen sapma D11 (docs/domain.md): Kullanılan, onaylı tüm taleplerin iş günü
    toplamı; yıl ayrımı yok, gelecekteki talep de sayılır. Ayse'nin onaylı talebi
    2026-07-06 → 2026-07-17: 10 iş günü (spec 0002 CB-2).

    Bugünkü davranışı sabitler; D11 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    assert balances(client_on(today))[AYSE][1] == 10


def test_d5_pending_days_not_deducted(client: FlaskClient) -> None:
    """PB-4 — bilinen sapma D5 (docs/domain.md): bekleyen talepler bakiyeden düşülmez.
    Ayse'nin 3 günlük, Mehmet'in 3 günlük bekleyen talebi var; Kalan = Hak − Kullanılan.

    Bugünkü davranışı sabitler; D5 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    table = balances(client)
    assert table[AYSE] == (26, 10, 16)
    assert table["Mehmet Demir"] == (20, 0, 20)


def test_d14_remaining_can_go_negative(client_on: Callable[[date], FlaskClient]) -> None:
    """PB-4 — bilinen sapma D14 (docs/domain.md): Kalan negatife düşebilir (I-1 ihlali).

    Bugünkü davranışı sabitler; D14, D11 (gelecekteki onaylı talep sayılır) ve D5 (bekleyen
    düşülmez) düzeltmeleri bu testi bilinçli olarak değiştirir.
    """
    assert balances(client_on(date(2008, 12, 31)))[AYSE] == (0, 10, -10)
