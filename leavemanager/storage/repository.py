"""Servislerin gördüğü depo arayüzü; bugün bellekte, sonra SQL (docs/architecture.md)."""

from datetime import date
from typing import Protocol

from leavemanager.domain.models import Employee, LeaveRequest


class LeaveRepository(Protocol):
    def employees(self) -> list[Employee]: ...

    def find_employee(self, employee_id: int) -> Employee | None: ...

    def requests(self) -> list[LeaveRequest]: ...

    def add_request(
        self, employee_id: int, start: date, end: date, reason: str, status: str
    ) -> LeaveRequest: ...
