"""Yeni talep (`/new`) karakterizasyonu — spec 0001, PB-8…PB-14. Bugün = 2026-10-25.

`test_d<n>_` ile başlayan testler bilinen bir sapmanın BUGÜNKÜ davranışını sabitler
(docs/domain.md, Known deviations). O sapmanın düzeltmesi testi bilinçli olarak değiştirir.
"""

import pytest
from flask.testing import FlaskClient
from pages import counter, parse

ERROR_TEXT = "HATA: ERR-412 NullReferenceGibi - bakiye yetersiz. IT'ye bildirin: dahili 4127"
SEED_REQUEST_COUNT = 8


def request_rows(client: FlaskClient) -> list[list[str]]:
    return parse(client.get("/requests").text).rows


def list_text(client: FlaskClient) -> str:
    """Kullanıcının yönlendirildiği talep listesinin görünen metni."""
    return parse(client.get("/requests").text).text


def assert_redirects_to_list(response) -> None:
    assert response.status_code == 302
    assert response.headers["Location"] == "/requests"


def test_form_offers_five_employees_and_fields(client: FlaskClient) -> None:
    """PB-8."""
    response = client.get("/new")
    assert response.status_code == 200
    page = parse(response.text)
    assert page.options == [
        ("1", "Ayse Yilmaz"),
        ("2", "Mehmet Demir"),
        ("3", "Zeynep Kaya"),
        ("4", "Ahmet Celik"),
        ("5", "Elif Sahin"),
    ]
    assert page.fields == ["employee_id", "start", "end", "reason"]
    assert page.labels == [
        ("Personel:", "employee_id"),
        ("Baslangic:", "start"),
        ("Bitis:", "end"),
        ("Neden:", "reason"),
    ]


def test_valid_request_is_pending_and_redirects(client: FlaskClient) -> None:
    """PB-9."""
    form = {"employee_id": "2", "start": "2026-11-16", "end": "2026-11-18", "reason": "Test"}
    assert_redirects_to_list(client.post("/new", data=form))
    rows = request_rows(client)
    assert len(rows) == SEED_REQUEST_COUNT + 1
    assert rows[-1] == ["Mehmet Demir", "2026-11-16", "2026-11-18", "3", "Test", "Beklemede"]
    assert counter(parse(client.get("/").text), "Bekleyen") == 5


def test_d5_valid_request_does_not_change_remaining(client: FlaskClient) -> None:
    """PB-9 — bilinen sapma D5 (docs/domain.md): yeni (bekleyen) talep Kalan'ı düşürmez.

    Bugünkü davranışı sabitler; D5 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    form = {"employee_id": "2", "start": "2026-11-16", "end": "2026-11-18", "reason": "Test"}
    client.post("/new", data=form)
    mehmet = next(r for r in parse(client.get("/").text).rows if r[0] == "Mehmet Demir")
    assert mehmet[2:] == ["20", "0", "20"]


def test_missing_reason_saved_empty(client: FlaskClient) -> None:
    """PB-9 — neden gönderilmezse boş kaydedilir."""
    form = {"employee_id": "2", "start": "2026-11-10", "end": "2026-11-11"}
    assert_redirects_to_list(client.post("/new", data=form))
    assert request_rows(client)[-1] == [
        "Mehmet Demir",
        "2026-11-10",
        "2026-11-11",
        "2",
        "",
        "Beklemede",
    ]


@pytest.mark.parametrize(
    ("employee_id", "start", "end"),
    [
        ("3", "2026-12-01", "2026-12-15"),  # Zeynep, Kalan 14, 15 gün
        ("5", "2026-11-16", "2026-11-16"),  # Elif, Kalan 0, 1 gün
    ],
)
def test_d9_insufficient_balance_shows_internal_error_text(
    client: FlaskClient, employee_id: str, start: str, end: str
) -> None:
    """PB-10 — bilinen sapma D9 (docs/domain.md, docs/security.md): hata mesajı dahili kod ve
    dahili telefon numarası içerir.

    Bugünkü davranışı sabitler; D9 düzeltmesi bu testi bilinçli olarak değiştirir. Zeynep
    durumu ayrıca D4'e bağlıdır (15 takvim günü = 11 iş günü, Kalan 14'e sığar).
    """
    form = {"employee_id": employee_id, "start": start, "end": end, "reason": "x"}
    response = client.post("/new", data=form)
    assert response.status_code == 200
    assert ERROR_TEXT in parse(response.text).text
    assert len(request_rows(client)) == SEED_REQUEST_COUNT


def test_d6_equal_to_remaining_is_silently_dropped(client: FlaskClient) -> None:
    """PB-11 — bilinen sapma D6 (docs/domain.md): talep günü Kalan'a eşitse (Zeynep, 14 gün)
    kayıt oluşmaz ve hata gösterilmez (BR-5: kabul edilmeli).

    Bugünkü davranışı sabitler; D6, D4 (takvim günü) ve D5 (Kalan'dan bekleyen düşülmez)
    düzeltmeleri bu testi bilinçli olarak değiştirir. "Hata gösterilmez": yönlendirilen liste
    sayfası POST'tan önceki haliyle aynıdır — ne yeni kayıt ne mesaj (VERIFY G1).
    """
    before = list_text(client)
    form = {"employee_id": "3", "start": "2026-12-01", "end": "2026-12-14", "reason": "Esit"}
    assert_redirects_to_list(client.post("/new", data=form))
    assert list_text(client) == before
    assert len(request_rows(client)) == SEED_REQUEST_COUNT


def test_one_below_remaining_is_saved(client: FlaskClient) -> None:
    """PB-11 — Kalan − 1 gün (Zeynep, 13 gün) kaydedilir. Değerler D4 (takvim günü) ve D5'e
    (Kalan'dan bekleyen düşülmez) bağlıdır; o düzeltmeler bu beklentiyi de bilinçli olarak
    değiştirir (docs/domain.md)."""
    form = {"employee_id": "3", "start": "2026-12-01", "end": "2026-12-13", "reason": "Bir eksik"}
    assert_redirects_to_list(client.post("/new", data=form))
    rows = request_rows(client)
    assert len(rows) == SEED_REQUEST_COUNT + 1
    assert rows[-1][:4] == ["Zeynep Kaya", "2026-12-01", "2026-12-13", "13"]


def test_d7_end_before_start_saved_with_negative_days(client: FlaskClient) -> None:
    """PB-12 — bilinen sapma D7 (docs/domain.md): bitiş başlangıçtan önceyse talep negatif
    günle kaydedilir (BR-6: reddedilmeli).

    Bugünkü davranışı sabitler; D7 ve D4 (gün sayımı) düzeltmeleri bu testi bilinçli olarak
    değiştirir.
    """
    form = {"employee_id": "2", "start": "2026-11-10", "end": "2026-11-05", "reason": "Ters"}
    assert_redirects_to_list(client.post("/new", data=form))
    assert request_rows(client)[-1] == [
        "Mehmet Demir",
        "2026-11-10",
        "2026-11-05",
        "-4",
        "Ters",
        "Beklemede",
    ]


@pytest.mark.parametrize(
    "form",
    [
        {"employee_id": "99", "start": "2026-11-10", "end": "2026-11-11", "reason": "Yok"},
        {"employee_id": "2", "start": "abc", "end": "2026-11-11", "reason": "Bozuk"},
        {"start": "2026-11-10", "end": "2026-11-11"},
        {"employee_id": "2", "start": "2026-11-10"},
        {},
    ],
    ids=["unknown-employee", "invalid-date", "missing-employee", "missing-end", "empty-form"],
)
def test_d7_invalid_input_silently_redirects(client: FlaskClient, form: dict[str, str]) -> None:
    """PB-13 — bilinen sapma D7 (docs/domain.md): geçersiz girdi kayıt oluşturmaz ama hata da
    göstermez; kullanıcı talep listesine yönlendirilir (BR-6: hata gösterilmeli).

    Bugünkü davranışı sabitler; D7 düzeltmesi bu testi bilinçli olarak değiştirir. "Hata
    göstermez": yönlendirilen liste sayfası POST'tan önceki haliyle aynıdır (VERIFY G1).
    """
    before = list_text(client)
    assert_redirects_to_list(client.post("/new", data=form))
    assert list_text(client) == before
    assert len(request_rows(client)) == SEED_REQUEST_COUNT


def test_d8_past_dated_request_accepted(client: FlaskClient) -> None:
    """PB-14 — bilinen sapma D8 (docs/domain.md): başlangıcı bugünden önce olan talebi herkes
    girebilir (BR-7: yalnızca İK).

    Bugünkü davranışı sabitler; D8 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    form = {"employee_id": "2", "start": "2026-01-05", "end": "2026-01-06", "reason": "Gecmis"}
    assert_redirects_to_list(client.post("/new", data=form))
    assert request_rows(client)[-1][:4] == ["Mehmet Demir", "2026-01-05", "2026-01-06", "2"]
