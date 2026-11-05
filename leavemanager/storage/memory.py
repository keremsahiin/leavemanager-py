"""Bellekteki depo: her örnek temiz seed verisiyle başlar; kayıt ID'lerini yalnızca depo üretir."""

from datetime import date

from leavemanager.domain.models import (
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
    Employee,
    LeaveRequest,
)

SEED_EMPLOYEES = (
    Employee(1, "Ayse Yilmaz", "IT", date(2008, 3, 15)),
    Employee(2, "Mehmet Demir", "Muhasebe", date(2019, 6, 1)),
    Employee(3, "Zeynep Kaya", "IK", date(2024, 11, 10)),
    Employee(4, "Ahmet Celik", "IT", date(2020, 2, 29)),
    Employee(5, "Elif Sahin", "Satis", date(2026, 6, 1)),
)

SEED_REQUESTS = (
    LeaveRequest(1, 1, date(2026, 7, 6), date(2026, 7, 17), "Yaz tatili", STATUS_APPROVED),
    LeaveRequest(2, 2, date(2026, 11, 2), date(2026, 11, 4), "Aile ziyareti", STATUS_PENDING),
    LeaveRequest(3, 3, date(2026, 11, 9), date(2026, 11, 9), "Saglik", STATUS_PENDING),
    LeaveRequest(4, 4, date(2026, 12, 21), date(2026, 12, 25), "Yilbasi oncesi", STATUS_PENDING),
    LeaveRequest(5, 1, date(2026, 12, 28), date(2026, 12, 30), "Yil sonu", STATUS_PENDING),
    LeaveRequest(6, 5, date(2026, 10, 5), date(2026, 10, 7), "Tasinma", STATUS_REJECTED),
    LeaveRequest(7, 3, date(2026, 9, 14), date(2026, 9, 25), "Uzun tatil", STATUS_REJECTED),
    LeaveRequest(8, 2, date(2026, 8, 3), date(2026, 8, 3), "Ozel is", STATUS_REJECTED),
)


class InMemoryRepository:
    def __init__(self) -> None:
        self._employees = list(SEED_EMPLOYEES)
        self._requests = list(SEED_REQUESTS)
        self._next_id = len(SEED_REQUESTS) + 1

    def employees(self) -> list[Employee]:
        return list(self._employees)

    def find_employee(self, employee_id: int) -> Employee | None:
        return next((e for e in self._employees if e.id == employee_id), None)

    def requests(self) -> list[LeaveRequest]:
        return list(self._requests)

    def add_request(
        self, employee_id: int, start: date, end: date, reason: str, status: str
    ) -> LeaveRequest:
        request = LeaveRequest(self._next_id, employee_id, start, end, reason, status)
        self._requests.append(request)
        self._next_id += 1
        return request
