"""Adresler ve gezinme karakterizasyonu — spec 0001, PB-15."""

import pytest
from flask.testing import FlaskClient
from pages import parse

NAVIGATION = {("/", "Ana Sayfa"), ("/requests", "Talepler"), ("/new", "Yeni Talep")}


@pytest.mark.parametrize(
    ("method", "path", "status"),
    [
        ("GET", "/", 200),
        ("GET", "/requests", 200),
        ("GET", "/new", 200),
        ("GET", "/yok", 404),
        ("GET", "/new/", 404),
        ("GET", "/requests/", 404),
        ("POST", "/requests", 405),
        ("PUT", "/new", 405),
        ("POST", "/", 405),
        ("PUT", "/requests", 405),
        ("DELETE", "/requests", 405),
        ("DELETE", "/new", 405),
    ],
)
def test_only_known_routes_respond(
    client: FlaskClient, method: str, path: str, status: int
) -> None:
    """PB-15 — yalnızca `/`, `/requests` (GET) ve `/new` (GET, POST) sunulur.

    "Bilinmeyen adres" kısmı HTTP üzerinden ancak örneklenebilir; adres listesini saymak iç
    yapıya bağlanmak olur (spec Constraints). Bilinen sınır (VERIFY G2).
    """
    assert client.open(path, method=method).status_code == status


def test_every_page_has_navigation(client: FlaskClient) -> None:
    """PB-15 — her sayfada, yetersiz bakiye hata sayfası (PB-10) dahil, üç bağlantı bulunur."""
    error_form = {"employee_id": "5", "start": "2026-11-16", "end": "2026-11-16", "reason": "x"}
    pages = {
        "/": client.get("/").text,
        "/requests": client.get("/requests").text,
        "/new": client.get("/new").text,
        "hata sayfası": client.post("/new", data=error_form).text,
    }
    for name, html in pages.items():
        assert NAVIGATION <= set(parse(html).links), name
