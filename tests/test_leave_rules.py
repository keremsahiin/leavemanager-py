"""İzin kurallarının HTTP'den görülemeyen sınırları — spec 0003 CB-1 (review F1), BR-3.

HTTP'de onay yolu yok ve seed'de tek onaylı talep var; bu sınırlar ancak `leave_balance` doğrudan
çağrılarak sınanır. Saf fonksiyon olduğu için "bugün" parametre olarak verilir, saat dondurulmaz.
"""

from datetime import date

import pytest

from leavemanager.domain.leave_rules import LeaveBalance, leave_balance, working_days

HIRE = date(2020, 3, 15)
ANNIVERSARY = date(2026, 3, 15)  # kıdem 6: Hak 20, önceki yılların hakkı toplam 70


@pytest.mark.parametrize(
    ("start", "days", "carried_over", "used"),
    [
        (date(2026, 3, 15), 5, 70, 5),  # yıldönümü günü başlayan: yeni izin yılında
        (date(2026, 3, 14), 5, 65, 0),  # bir gün önce başlayan: önceki izin yılında
        (date(2026, 3, 9), 10, 60, 0),  # yıldönümünü kapsayan: başladığı yıla tümüyle yazılır
    ],
)
def test_br4_request_belongs_to_leave_year_it_starts_in(
    start: date, days: int, carried_over: int, used: int
) -> None:
    """BR-4 — talep başladığı izin yılına yazılır; Kalan hangi yıla yazıldığından etkilenmez."""
    balance = leave_balance(HIRE, ANNIVERSARY, [(start, days)], 0)
    assert (balance.carried_over, balance.used) == (carried_over, used)
    assert balance.remaining == 90 - days


def test_br4_approved_requests_are_summed_per_leave_year() -> None:
    """BR-4 — bir izin yılındaki birden çok onaylı talep toplanır."""
    approved = [
        (date(2025, 4, 7), 4),
        (date(2025, 5, 5), 1),
        (date(2026, 4, 6), 3),
        (date(2026, 5, 4), 2),
    ]
    balance = leave_balance(HIRE, date(2026, 6, 1), approved, 0)
    assert balance == LeaveBalance(entitlement=20, carried_over=65, used=5, pending=0)


def test_br4_requests_from_older_leave_years_reduce_carry_over() -> None:
    """BR-4 — yalnızca bir önceki yılın değil, tüm geçmiş yılların onaylı talepleri düşülür."""
    balance = leave_balance(HIRE, ANNIVERSARY, [(date(2022, 4, 4), 6)], 0)
    assert balance == LeaveBalance(entitlement=20, carried_over=64, used=0, pending=0)


def test_br4_first_leave_year_starts_on_hire_date() -> None:
    """BR-4 — kıdem 0 iken izin yılı işe girişte başlar: o gün başlayan talep Kullanılan'da."""
    hire = date(2026, 6, 1)
    balance = leave_balance(hire, date(2026, 10, 25), [(hire, 2)], 0)
    assert balance == LeaveBalance(entitlement=0, carried_over=0, used=2, pending=0)


@pytest.mark.parametrize(
    ("today", "carried_over", "used"),
    [
        (date(2024, 2, 28), 28, 5),  # kıdem 3: talep bu izin yılında
        (date(2024, 2, 29), 37, 0),  # artık yıl: 4. yıl 29 Şubat'ta dolar, talep önceki yılda
    ],
)
def test_br4_feb29_hire_leave_year_boundary(today: date, carried_over: int, used: int) -> None:
    """BR-2 ve BR-4 — 29 Şubat'ta işe girenin izin yılı artık yılda 29 Şubat'ta başlar."""
    balance = leave_balance(date(2020, 2, 29), today, [(date(2024, 2, 28), 5)], 0)
    assert (balance.carried_over, balance.used) == (carried_over, used)


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (date(2026, 11, 14), date(2026, 11, 15)),  # yalnızca hafta sonu
        (date(2026, 11, 10), date(2026, 11, 5)),  # bitiş başlangıçtan önce
    ],
    ids=["weekend-only", "reversed"],
)
def test_br3_range_without_weekday_counts_zero(start: date, end: date) -> None:
    """BR-3 — aralıkta Pazartesi–Cuma yoksa izin günü 0. Böyle bir talep kaydedilmediği için
    (BR-6) sayı HTTP'den görülemez."""
    assert working_days(start, end) == 0
