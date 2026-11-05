"""Ana sayfa (`/`) — spec 0001 PB-1…PB-4; spec 0002 CB-1, CB-2; spec 0003 CB-1, CB-2 (bakiye).

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

SEED_BALANCES = [  # Ad, Birim, Hak, Devir, Kullanılan, Bekleyen, Kalan — bugün 2026-10-25
    ["Ayse Yilmaz", "IT", "26", "328", "10", "3", "341"],
    ["Mehmet Demir", "Muhasebe", "20", "90", "0", "3", "107"],
    ["Zeynep Kaya", "IK", "14", "0", "0", "1", "13"],
    ["Ahmet Celik", "IT", "20", "70", "0", "5", "85"],
    ["Elif Sahin", "Satis", "0", "0", "0", "0", "0"],
]


def balances(client: FlaskClient) -> dict[str, tuple[int, ...]]:
    """Bakiye tablosu: ad -> (Hak, Devir, Kullanılan, Bekleyen, Kalan)."""
    rows = parse(client.get("/").text).rows
    return {row[0]: tuple(int(cell) for cell in row[2:]) for row in rows}


def test_counters_with_seed_data(client: FlaskClient) -> None:
    """PB-1."""
    page = parse(client.get("/").text)
    assert counter(page, "Bekleyen") == 4
    assert counter(page, "Onaylanan") == 1
    assert counter(page, "Reddedilen") == 3


def test_balance_table_with_seed_data(client: FlaskClient) -> None:
    """Spec 0003 CB-2; reddedilen talepler hiçbir sütunu etkilemez (CB-1). Ayşe'nin satırı D15'e
    (talebi 15 Temmuz'u kapsıyor) bağlıdır; o düzeltme bu beklentiyi de bilinçli olarak
    değiştirir (docs/domain.md). Devir 328 = 5×14 + 9×20 + 3×26 (BR-1)."""
    response = client.get("/")
    assert response.status_code == 200
    page = parse(response.text)
    assert page.headers == [["Ad", "Birim", "Hak", "Devir", "Kullanilan", "Bekleyen", "Kalan"]]
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
    ("name", "today", "entitlement"),
    [
        (AYSE, date(2023, 3, 14), 20),  # kıdem 14
        (AYSE, date(2023, 3, 15), 26),  # kıdem 15: yıldönümü günü
        (AYSE, date(2023, 12, 31), 26),
        (AYSE, date(2024, 3, 14), 26),  # 16. yıldönümünden bir gün önce
        (AHMET, date(2035, 2, 27), 20),  # kıdem 14
        (AHMET, date(2035, 2, 28), 26),  # kıdem 15: artık olmayan yılda 28 Şubat
        (AHMET, date(2036, 2, 28), 26),  # hâlâ kıdem 15
    ],
)
def test_br1_15_years_gives_26_days(
    client_on: Callable[[date], FlaskClient], name: str, today: date, entitlement: int
) -> None:
    """BR-1 (D2 düzeltmesi) — kıdem 14'te 20 gün, 15 yıl ve üzerinde 26 gün."""
    assert balances(client_on(today))[name][0] == entitlement


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
        (date(2036, 2, 29), 26),  # artık yıl: 16. yıl 29 Şubat'ta dolar
    ],
)
def test_br2_feb29_hire_anniversary(
    client_on: Callable[[date], FlaskClient], today: date, entitlement: int
) -> None:
    """BR-2, spec 0002 CB-1 — 29 Şubat'ta işe girenin (Ahmet) yılı artık olmayan yıllarda
    28 Şubat'ta, artık yıllarda 29 Şubat'ta dolar."""
    assert balances(client_on(today))[AHMET][0] == entitlement


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2027, 1, 1), (26, 328, 10, 3, 341)),  # izin yılı 2026-03-15'te başladı
        (date(2027, 3, 15), (26, 344, 0, 3, 367)),  # yeni izin yılı: 10 gün devirden düşülür
    ],
)
def test_br4_used_counts_from_current_leave_year(
    client_on: Callable[[date], FlaskClient], today: date, expected: tuple[int, ...]
) -> None:
    """BR-4, spec 0003 CB-1 — her yıldönümünde yeni hak eklenir, kullanılmayan gün devreder;
    Kullanılan bu izin yılında başlayan onaylı talepleri sayar. Ayşe'nin onaylı talebi
    2026-07-06 → 2026-07-17: 10 iş günü. Değerler D15'e bağlıdır (docs/domain.md)."""
    assert balances(client_on(today))[AYSE] == expected


@pytest.mark.parametrize(
    ("today", "carried_over"),
    [
        (date(2024, 2, 28), 28),  # kıdem 3
        (date(2024, 2, 29), 42),  # artık yıl: 4. yıl 29 Şubat'ta dolar
    ],
)
def test_br4_carry_over_feb29_anniversary(
    client_on: Callable[[date], FlaskClient], today: date, carried_over: int
) -> None:
    """BR-2 ve BR-4, spec 0003 CB-1 — 29 Şubat'ta işe girenin (Ahmet) yılı artık yılda 29
    Şubat'ta dolar ve önceki izin yılının hakkı devre geçer. Artık yıl sınırının ekrandaki kanıtı
    budur: Hak aynı kaldığı için Hak sütununda görünmez."""
    assert balances(client_on(today))[AHMET][1] == carried_over


def test_br4_pending_days_deducted(client: FlaskClient) -> None:
    """BR-4, spec 0003 CB-1 — bekleyen talepler Bekleyen'de görünür ve Kalan'dan düşülür."""
    table = balances(client)
    assert table[AYSE][3] == 3
    assert table["Mehmet Demir"] == (20, 90, 0, 3, 107)


@pytest.mark.parametrize("today", [date(2026, 10, 25), date(2027, 3, 15)])
def test_br4_row_arithmetic(client_on: Callable[[date], FlaskClient], today: date) -> None:
    """Spec 0003 CB-2 — her satırda Kalan = Devir + Hak − Kullanılan − Bekleyen."""
    for entitlement, carried, used, pending, remaining in balances(client_on(today)).values():
        assert remaining == carried + entitlement - used - pending


def test_d14_remaining_can_go_negative(client_on: Callable[[date], FlaskClient]) -> None:
    """Bilinen sapma D14 (docs/domain.md): Kalan negatife düşebilir (I-1 ihlali). Kıdem 0 iken
    gelecekteki onaylı (10) ve bekleyen (3) talepler düşülür.

    Bugünkü davranışı sabitler; D14 ve D15 (talep 15 Temmuz'u kapsıyor) düzeltmeleri bu testi
    bilinçli olarak değiştirir.
    """
    assert balances(client_on(date(2009, 1, 1)))[AYSE] == (0, 0, 10, 3, -13)
