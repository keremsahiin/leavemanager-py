"""Sayfalar: formu oku, servisi çağır, şablonla göster. Kullanıcıya görünen metin burada."""

from datetime import date

from flask import Blueprint, redirect, render_template, request

from leavemanager.domain.errors import (
    DomainError,
    EmployeeNotFound,
    InsufficientBalance,
    InvalidDate,
    InvalidDateRange,
    NoLeaveDays,
)
from leavemanager.domain.models import STATUS_APPROVED, STATUS_PENDING, STATUS_REJECTED
from leavemanager.services import LeaveService

STATUS_COLORS = {STATUS_APPROVED: "green", STATUS_PENDING: "orange", STATUS_REJECTED: "red"}

ERROR_RESPONSES = {
    EmployeeNotFound: ("Personel bulunamadı.", 400),
    InvalidDate: ("Başlangıç ve bitiş tarihi geçerli olmalı.", 400),
    InvalidDateRange: ("Bitiş tarihi başlangıç tarihinden önce olamaz.", 400),
    NoLeaveDays: ("Seçilen aralıkta izin günü yok.", 400),
    InsufficientBalance: ("Kalan izin bu talep için yeterli değil.", 400),
}

UNEXPECTED_ERROR = "Beklenmeyen bir hata oluştu."
CSRF_ERROR = "Form süresi doldu ya da geçersiz. Sayfayı yenileyip yeniden deneyin."


def read_employee_id(value: str | None) -> int:
    try:
        return int(value)
    except TypeError, ValueError:
        raise EmployeeNotFound from None


def read_date(value: str | None) -> date:
    try:
        return date.fromisoformat(value or "")
    except ValueError:
        raise InvalidDate from None


def show_domain_error(error: DomainError):
    message, status = ERROR_RESPONSES[type(error)]
    return render_template("error.html", message=message), status


def show_csrf_error(error: Exception):
    return render_template("error.html", message=CSRF_ERROR), 400


def show_unexpected_error(error: Exception):
    """Ayrıntı kullanıcıya gösterilmez; Flask hatayı bu işleyiciden önce log'a yazar."""
    return render_template("error.html", message=UNEXPECTED_ERROR), 500


def create_pages(service: LeaveService) -> Blueprint:
    pages = Blueprint("pages", __name__)

    @pages.route("/")
    def dashboard():
        return render_template(
            "dashboard.html", counts=service.status_counts(), rows=service.balance_rows()
        )

    @pages.route("/requests")
    def list_requests():
        return render_template("requests.html", rows=service.request_rows(), colors=STATUS_COLORS)

    @pages.route("/new", methods=["GET", "POST"])
    def new_request():
        if request.method == "POST":
            service.create_request(
                read_employee_id(request.form.get("employee_id")),
                read_date(request.form.get("start")),
                read_date(request.form.get("end")),
                request.form.get("reason", ""),
            )
            return redirect("/requests")
        return render_template("new_request.html", employees=service.employees())

    return pages
