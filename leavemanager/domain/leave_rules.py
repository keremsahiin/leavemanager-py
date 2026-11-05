"""İzin kuralları (docs/domain.md). Saf fonksiyonlar: "bugün" parametre olarak gelir (F1, F6)."""

import calendar
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from leavemanager.domain.errors import InsufficientBalance, InvalidDateRange, NoLeaveDays


@dataclass(frozen=True)
class LeaveBalance:
    """BR-4 — bir personelin bakiyesi; gün sayıları `int`."""

    entitlement: int  # bu izin yılının hakkı
    carried_over: int  # önceki izin yıllarından devreden
    used: int  # bu izin yılında veya sonrasında başlayan onaylı talepler
    pending: int  # tüm bekleyen talepler

    @property
    def remaining(self) -> int:
        return self.carried_over + self.entitlement - self.used - self.pending


def _anniversary(hire_date: date, year: int) -> date:
    """Verilen yıldaki işe giriş yıldönümü; 29 Şubat artık olmayan yılda 28 Şubat'tır (BR-2)."""
    if (hire_date.month, hire_date.day) == (2, 29) and not calendar.isleap(year):
        return date(year, 2, 28)
    return hire_date.replace(year=year)


def completed_years(hire_date: date, today: date) -> int:
    """BR-2 — kıdem: işe giriş yıldönümünde dolan tam yıl sayısı; yıldönümü günü yıl dolmuştur.

    İşe giriş bugünden sonraysa 0.
    """
    years = today.year - hire_date.year
    if today < _anniversary(hire_date, today.year):
        years -= 1
    return max(years, 0)


def annual_entitlement(years: int) -> int:
    """BR-1 — kıdeme göre bir izin yılının hakkı."""
    if years < 1:
        return 0
    if years <= 5:
        return 14
    if years <= 14:
        return 20
    return 26


def leave_year_start(hire_date: date, today: date) -> date:
    """Bugünü içeren izin yılının ilk günü: son yıldönümü, kıdem 0 iken işe giriş günü."""
    return _anniversary(hire_date, hire_date.year + completed_years(hire_date, today))


def leave_balance(
    hire_date: date,
    today: date,
    approved: Sequence[tuple[date, int]],
    pending_days: int,
) -> LeaveBalance:
    """BR-4 — her yıldönümünde yeni hak eklenir, kullanılmayan gün devreder, tavan yoktur.

    `approved`: onaylı taleplerin (başlangıç, izin günü) çiftleri; talep, başladığı izin yılına
    tümüyle yazılır. Hesap işe girişten başlar, açılış devri 0 (spec 0003).
    """
    years = completed_years(hire_date, today)
    year_start = leave_year_start(hire_date, today)
    earned_before = sum(annual_entitlement(year) for year in range(1, years))
    used_before = sum(days for start, days in approved if start < year_start)
    return LeaveBalance(
        entitlement=annual_entitlement(years),
        carried_over=earned_before - used_before,
        used=sum(days for start, days in approved if start >= year_start),
        pending=pending_days,
    )


def working_days(start: date, end: date) -> int:
    """BR-3 — izin günü: başlangıç ve bitiş dahil aralıktaki Pazartesi–Cuma günleri.

    Resmî tatiller henüz düşülmez: hafta içine denk gelen tatil izin günü sayılır (D15; takvim
    kaynağı açık karar). Bitiş başlangıçtan önceyse 0.
    """
    days = (end - start).days + 1
    if days <= 0:
        return 0
    # Aralığın uzunluğundan bağımsız sabit süre: her tam hafta 5 gün, artan en fazla 6 gün tek tek.
    weeks, rest = divmod(days, 7)
    first = start.weekday()
    return weeks * 5 + sum(1 for offset in range(rest) if (first + offset) % 7 < 5)


def validate_request(start: date, end: date, remaining: int) -> None:
    """BR-5 ve BR-6 — kurala uymayan talepte `DomainError` fırlatır; Kalan'a eşit talep geçerli."""
    if end < start:
        raise InvalidDateRange
    days = working_days(start, end)
    if days < 1:
        raise NoLeaveDays
    if days > remaining:
        raise InsufficientBalance
