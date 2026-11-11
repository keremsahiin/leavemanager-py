"""HTTP ve HTML. Veriye yalnızca servis üzerinden ulaşır (F3)."""

import os

from flask import Flask
from flask_wtf.csrf import CSRFError, CSRFProtect

from leavemanager.domain.errors import DomainError
from leavemanager.services import LeaveService
from leavemanager.web.pages import (
    create_pages,
    show_csrf_error,
    show_domain_error,
    show_unexpected_error,
)


def create_app(service: LeaveService) -> Flask:
    """`SECRET_KEY` ortamdan gelir; kodda varsayılanı yoktur, yoksa uygulama başlamaz."""
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY ortam değişkeni tanımlı değil (.env.example).")
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secret_key
    CSRFProtect(app)
    app.register_blueprint(create_pages(service))
    app.register_error_handler(DomainError, show_domain_error)
    app.register_error_handler(CSRFError, show_csrf_error)
    app.register_error_handler(500, show_unexpected_error)
    return app
