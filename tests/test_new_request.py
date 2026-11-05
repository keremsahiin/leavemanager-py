"""Yeni talep (`/new`) — spec 0001 PB-8…PB-14; spec 0002 CB-3; spec 0003 CB-3 (bakiye).
Bugün = 2026-10-25.

`test_d<n>_` ile başlayan testler bilinen bir sapmanın BUGÜNKÜ davranışını sabitler
(docs/domain.md, Known deviations). O sapmanın düzeltmesi testi bilinçli olarak değiştirir.
"""

import pytest
from flask.testing import FlaskClient
from pages import counter, parse

ERROR_TEXT = "HATA: ERR-412 NullReferenceGibi - bakiye yetersiz. IT'ye bildirin: dahili 4127"
EMPLOYEE_ERROR = "Personel bulunamadı."
DATE_ERROR = "Başlangıç ve bitiş tarihi geçerli olmalı."
RANGE_ERROR = "Bitiş tarihi başlangıç tarihinden önce olamaz."
NO_LEAVE_DAY_ERROR = "Seçilen aralıkta izin günü yok."
SEED_REQUEST_COUNT = 8


def request_rows(client: FlaskClient) -> list[list[str]]:
    return parse(client.get("/requests").text).rows


def list_text(client: FlaskClient) -> str:
    """Kullanıcının yönlendirildiği talep listesinin görünen metni."""
    return parse(client.get("/requests").text).text


def assert_redirects_to_list(response) -> None:
    assert response.status_code == 302
    assert response.headers["Location"] == "/requests"


def assert_rejected(client: FlaskClient, form: dict[str, str], message: str) -> None:
    """BR-6: kayıt oluşmaz, kullanıcı hatayı görür."""
    before = list_text(client)
    response = client.post("/new", data=form)
    assert response.status_code == 400
    page = parse(response.text)
    assert message in page.text
    assert page.fields == []
    assert list_text(client) == before


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


def test_br4_new_request_reduces_remaining(client: FlaskClient) -> None:
    """BR-4, spec 0003 CB-3 — geçerli yeni talep kaydedildiği anda Bekleyen ve Kalan'a yansır."""
    form = {"employee_id": "2", "start": "2026-11-16", "end": "2026-11-18", "reason": "Test"}
    client.post("/new", data=form)
    mehmet = next(r for r in parse(client.get("/").text).rows if r[0] == "Mehmet Demir")
    assert mehmet[2:] == ["20", "90", "0", "6", "104"]


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
        ("3", "2026-12-01", "2026-12-18"),  # Zeynep, Kalan 13, 14 iş günü
        ("5", "2026-11-16", "2026-11-16"),  # Elif, Kalan 0, 1 gün
    ],
)
def test_d9_insufficient_balance_shows_internal_error_text(
    client: FlaskClient, employee_id: str, start: str, end: str
) -> None:
    """PB-10 — bilinen sapma D9 (docs/domain.md, docs/security.md): hata mesajı dahili kod ve
    dahili telefon numarası içerir.

    Bugünkü davranışı, HTTP 200 dahil, sabitler; D9 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    form = {"employee_id": employee_id, "start": start, "end": end, "reason": "x"}
    response = client.post("/new", data=form)
    assert response.status_code == 200
    assert ERROR_TEXT in parse(response.text).text
    assert len(request_rows(client)) == SEED_REQUEST_COUNT


def test_br5_equal_to_remaining_is_accepted(client: FlaskClient) -> None:
    """BR-5 (D6 düzeltmesi) — talep günü Kalan'a eşitse (Zeynep, 13 iş günü) kabul edilir."""
    form = {"employee_id": "3", "start": "2026-12-01", "end": "2026-12-17", "reason": "Esit"}
    assert_redirects_to_list(client.post("/new", data=form))
    rows = request_rows(client)
    assert len(rows) == SEED_REQUEST_COUNT + 1
    assert rows[-1][:4] == ["Zeynep Kaya", "2026-12-01", "2026-12-17", "13"]


def test_one_below_remaining_is_saved(client: FlaskClient) -> None:
    """PB-11 — Kalan − 1 gün (Zeynep, 12 iş günü) kaydedilir."""
    form = {"employee_id": "3", "start": "2026-12-01", "end": "2026-12-16", "reason": "Bir eksik"}
    assert_redirects_to_list(client.post("/new", data=form))
    rows = request_rows(client)
    assert len(rows) == SEED_REQUEST_COUNT + 1
    assert rows[-1][:4] == ["Zeynep Kaya", "2026-12-01", "2026-12-16", "12"]


def test_br3_balance_check_counts_weekdays(client: FlaskClient) -> None:
    """BR-3, spec 0002 CB-3 — bakiye kontrolü iş günüyle yapılır: Zeynep'in (Kalan 13)
    15 takvim günü süren, 11 iş günlük talebi kaydedilir."""
    form = {"employee_id": "3", "start": "2026-12-01", "end": "2026-12-15", "reason": "Is gunu"}
    assert_redirects_to_list(client.post("/new", data=form))
    rows = request_rows(client)
    assert len(rows) == SEED_REQUEST_COUNT + 1
    assert rows[-1][:4] == ["Zeynep Kaya", "2026-12-01", "2026-12-15", "11"]


def test_br6_end_before_start_is_rejected(client: FlaskClient) -> None:
    """BR-6 (D7 düzeltmesi) — bitiş başlangıçtan önce olamaz."""
    form = {"employee_id": "2", "start": "2026-11-10", "end": "2026-11-05", "reason": "Ters"}
    assert_rejected(client, form, RANGE_ERROR)


@pytest.mark.parametrize("employee_id", ["2", "5"], ids=["balance-left", "no-balance"])
def test_br6_request_without_leave_day_is_rejected(client: FlaskClient, employee_id: str) -> None:
    """BR-6 (D7 düzeltmesi) — izin günü en az 1 olmalı: yalnızca hafta sonunu kapsayan talep."""
    form = {"employee_id": employee_id, "start": "2026-11-14", "end": "2026-11-15"}
    assert_rejected(client, form, NO_LEAVE_DAY_ERROR)


@pytest.mark.parametrize(
    ("form", "message"),
    [
        ({"employee_id": "99", "start": "2026-11-10", "end": "2026-11-11"}, EMPLOYEE_ERROR),
        ({"employee_id": "abc", "start": "2026-11-10", "end": "2026-11-11"}, EMPLOYEE_ERROR),
        ({"start": "2026-11-10", "end": "2026-11-11"}, EMPLOYEE_ERROR),
        ({}, EMPLOYEE_ERROR),
        ({"employee_id": "2", "start": "abc", "end": "2026-11-11"}, DATE_ERROR),
        ({"employee_id": "2", "start": "2026-11-10", "end": "2026-13-40"}, DATE_ERROR),
        ({"employee_id": "2", "start": "2026-1-5", "end": "2026-11-11"}, DATE_ERROR),
        ({"employee_id": "2", "end": "2026-11-11"}, DATE_ERROR),
        ({"employee_id": "2", "start": "2026-11-10"}, DATE_ERROR),
    ],
    ids=[
        "unknown-employee",
        "non-numeric-employee",
        "missing-employee",
        "empty-form",
        "invalid-start",
        "invalid-end",
        "non-iso-date",
        "missing-start",
        "missing-end",
    ],
)
def test_br6_invalid_input_shows_error(
    client: FlaskClient, form: dict[str, str], message: str
) -> None:
    """BR-6 (D7 düzeltmesi) — personel mevcut olmalı; geçersiz girdi hata olarak döner."""
    assert_rejected(client, form, message)


@pytest.mark.parametrize("field", ["employee_id", "start", "end"])
def test_security_error_page_does_not_echo_input(client: FlaskClient, field: str) -> None:
    """docs/security.md, Input & output — hata sayfası girilen değeri geri yansıtmaz."""
    form = {"employee_id": "2", "start": "2026-11-10", "end": "2026-11-11"}
    response = client.post("/new", data={**form, field: "<script>alert(1)</script>"})
    assert response.status_code == 400
    assert "alert(1)" not in response.text


def test_d8_past_dated_request_accepted(client: FlaskClient) -> None:
    """PB-14 — bilinen sapma D8 (docs/domain.md): başlangıcı bugünden önce olan talebi herkes
    girebilir (BR-7: yalnızca İK).

    Bugünkü davranışı sabitler; D8 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    form = {"employee_id": "2", "start": "2026-01-05", "end": "2026-01-06", "reason": "Gecmis"}
    assert_redirects_to_list(client.post("/new", data=form))
    assert request_rows(client)[-1][:4] == ["Mehmet Demir", "2026-01-05", "2026-01-06", "2"]
