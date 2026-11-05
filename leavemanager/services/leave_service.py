"""İzin senaryoları. "Bugün" `clock`'tan alınıp domain'e parametre olarak verilir."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from leavemanager import clock
from leavemanager.domain.errors import EmployeeNotFound
from leavemanager.domain.leave_rules import (
    LeaveBalance,
    leave_balance,
    validate_request,
    working_days,
)
from leavemanager.domain.models import (
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
    Employee,
)
from leavemanager.storage import LeaveRepository


@dataclass(frozen=True)
class StatusCounts:
    pending: int
    approved: int
    rejected: int


@dataclass(frozen=True)
class BalanceRow:
    employee: Employee
    balance: LeaveBalance


@dataclass(frozen=True)
class RequestRow:
    employee_name: str
    start: date
    end: date
    days: int
    reason: str
    status: str


class LeaveService:
    def __init__(
        self, repository: LeaveRepository, today: Callable[[], date] = clock.today
    ) -> None:
        self._repository = repository
        self._today = today

    def employees(self) -> list[Employee]:
        return self._repository.employees()

    def status_counts(self) -> StatusCounts:
        statuses = [request.status for request in self._repository.requests()]
        return StatusCounts(
            pending=statuses.count(STATUS_PENDING),
            approved=statuses.count(STATUS_APPROVED),
            rejected=statuses.count(STATUS_REJECTED),
        )

    def balance_rows(self) -> list[BalanceRow]:
        today = self._today()
        return [
            BalanceRow(employee, self._balance(employee, today))
            for employee in self._repository.employees()
        ]

    def request_rows(self) -> list[RequestRow]:
        names = {employee.id: employee.name for employee in self._repository.employees()}
        return [
            RequestRow(
                employee_name=names[request.employee_id],
                start=request.start,
                end=request.end,
                days=working_days(request.start, request.end),
                reason=request.reason,
                status=request.status,
            )
            for request in self._repository.requests()
        ]

    def create_request(self, employee_id: int, start: date, end: date, reason: str) -> None:
        employee = self._repository.find_employee(employee_id)
        if employee is None:
            raise EmployeeNotFound
        validate_request(start, end, self._balance(employee, self._today()).remaining)
        self._repository.add_request(employee_id, start, end, reason, STATUS_PENDING)

    def _balance(self, employee: Employee, today: date) -> LeaveBalance:
        approved = []
        pending = 0
        for request in self._repository.requests():
            if request.employee_id != employee.id:
                continue
            days = working_days(request.start, request.end)
            if request.status == STATUS_APPROVED:
                approved.append((request.start, days))
            elif request.status == STATUS_PENDING:
                pending += days
        return leave_balance(employee.hire_date, today, approved, pending)
