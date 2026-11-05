"""İş kuralı hataları (docs/conventions.md, Error handling). Kullanıcı metni `web`'dedir."""


class DomainError(Exception):
    """Tüm iş kuralı hatalarının tabanı."""


class EmployeeNotFound(DomainError):
    """BR-6 — personel mevcut değil."""


class InvalidDate(DomainError):
    """BR-6 — tarih eksik ya da geçersiz."""


class InvalidDateRange(DomainError):
    """BR-6 — bitiş başlangıçtan önce."""


class NoLeaveDays(DomainError):
    """BR-6 — aralıkta izin günü yok."""


class InsufficientBalance(DomainError):
    """BR-5 — talep Kalan'ı aşıyor."""
