"""İzin kuralları (docs/domain.md). Saf fonksiyonlar: "bugün" parametre olarak gelir (F1, F6)."""

import calendar
from datetime import date


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


def working_days(start: date, end: date) -> int:
    """BR-3 — izin günü: başlangıç ve bitiş dahil aralıktaki Pazartesi–Cuma günleri.

    Resmî tatiller henüz sayılmaz (takvim kaynağı açık karar). Bitiş başlangıçtan önceyse 0.
    """
    days = (end - start).days + 1
    if days <= 0:
        return 0
    # Aralığın uzunluğundan bağımsız sabit süre: her tam hafta 5 gün, artan en fazla 6 gün tek tek.
    weeks, rest = divmod(days, 7)
    first = start.weekday()
    return weeks * 5 + sum(1 for offset in range(rest) if (first + offset) % 7 < 5)
