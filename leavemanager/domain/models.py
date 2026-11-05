"""Kayıtlar (docs/conventions.md, Data rules). Durum metinleri kayıtta Türkçe: bilinen sapma D13."""

from dataclasses import dataclass
from datetime import date

STATUS_APPROVED = "Onaylandi"
STATUS_PENDING = "Beklemede"
STATUS_REJECTED = "Reddedildi"


@dataclass(frozen=True)
class Employee:
    id: int
    name: str
    department: str
    hire_date: date


@dataclass(frozen=True)
class LeaveRequest:
    id: int
    employee_id: int
    start: date
    end: date
    reason: str
    status: str
