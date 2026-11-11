"""HTTP ve HTML. Veriye yalnızca servis üzerinden ulaşır (F3)."""

from flask import Flask

from leavemanager.domain.errors import DomainError
from leavemanager.services import LeaveService
from leavemanager.web.pages import create_pages, show_domain_error, show_unexpected_error


def create_app(service: LeaveService) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(create_pages(service))
    app.register_error_handler(DomainError, show_domain_error)
    app.register_error_handler(500, show_unexpected_error)
    return app
