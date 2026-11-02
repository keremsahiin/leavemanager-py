"""Talep listesi (`/requests`) — spec 0001 PB-5…PB-7; spec 0002 CB-2 (iş günü).

`test_d<n>_` ile başlayan testler bilinen bir sapmanın BUGÜNKÜ davranışını sabitler
(docs/domain.md, Known deviations). O sapmanın düzeltmesi testi bilinçli olarak değiştirir.
"""

from flask.testing import FlaskClient
from pages import parse

SEED_REQUESTS = [  # Personel, Başlangıç, Bitiş, Gün, Neden, Durum — kayıt sırası
    ["Ayse Yilmaz", "2026-07-06", "2026-07-17", "10", "Yaz tatili", "Onaylandi"],
    ["Mehmet Demir", "2026-11-02", "2026-11-04", "3", "Aile ziyareti", "Beklemede"],
    ["Zeynep Kaya", "2026-11-09", "2026-11-09", "1", "Saglik", "Beklemede"],
    ["Ahmet Celik", "2026-12-21", "2026-12-25", "5", "Yilbasi oncesi", "Beklemede"],
    ["Ayse Yilmaz", "2026-12-28", "2026-12-30", "3", "Yil sonu", "Beklemede"],
    ["Elif Sahin", "2026-10-05", "2026-10-07", "3", "Tasinma", "Reddedildi"],
    ["Zeynep Kaya", "2026-09-14", "2026-09-25", "10", "Uzun tatil", "Reddedildi"],
    ["Mehmet Demir", "2026-08-03", "2026-08-03", "1", "Ozel is", "Reddedildi"],
]


def test_lists_seed_requests_in_order(client: FlaskClient) -> None:
    """PB-5; spec 0002 CB-2 (Gün iş günü). Değerler D13'e (durum kayıttaki metniyle) bağlıdır;
    o düzeltme bu beklentiyi de bilinçli olarak değiştirir (docs/domain.md)."""
    response = client.get("/requests")
    assert response.status_code == 200
    page = parse(response.text)
    assert page.headers == [["Personel", "Baslangic", "Bitis", "Gun", "Neden", "Durum"]]
    assert page.rows == SEED_REQUESTS


def test_br3_counts_weekdays_only(client: FlaskClient) -> None:
    """BR-3, spec 0002 CB-2 — izin günü, başlangıç ve bitiş dahil Pazartesi–Cuma günleridir:
    Cuma 2026-11-13 → Pazartesi 2026-11-16 talebi 2 gün. Yalnızca hafta sonu = 0 örneği D7'ye
    bağlı olduğu için `test_new_request.py::test_d7_weekend_only_…`'de (plan 0002, A2)."""
    form = {"employee_id": "2", "start": "2026-11-13", "end": "2026-11-16", "reason": "Hafta sonu"}
    client.post("/new", data=form)
    last = parse(client.get("/requests").text).rows[-1]
    assert last[:4] == ["Mehmet Demir", "2026-11-13", "2026-11-16", "2"]


def test_d13_status_text_and_color(client: FlaskClient) -> None:
    """PB-6 — bilinen sapma D13 (docs/domain.md): durum kayıttaki Türkçe metniyle gösterilir.
    Renk etikete değil, metni taşıyan öğenin satır içi rengine göre okunur (plan 0001, R3).

    Bugünkü davranışı sabitler; D13 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    page = parse(client.get("/requests").text)
    assert {row[5] for row in page.rows} == {"Onaylandi", "Beklemede", "Reddedildi"}
    colors = {text: color for text, color in page.colored}
    assert colors["Onaylandi"] == "green"
    assert colors["Beklemede"] == "orange"
    assert colors["Reddedildi"] == "red"


def test_d9_reason_rendered_unescaped(client: FlaskClient) -> None:
    """PB-7 — bilinen sapma D9 (docs/domain.md, docs/security.md): neden metni HTML kaçışlaması
    yapılmadan sayfaya yazılır (stored XSS).

    Bugünkü davranışı sabitler; D9 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    form = {"employee_id": "2", "start": "2026-11-10", "end": "2026-11-10"}
    client.post("/new", data={**form, "reason": "<script>alert(1)</script>"})
    html = client.get("/requests").text
    assert "<script>alert(1)</script>" in html
    assert "&lt;script&gt;" not in html


def test_d12_reason_visible_to_everyone(client: FlaskClient) -> None:
    """PB-7 — bilinen sapma D12 (docs/domain.md): neden metni, kimlik sorulmadan listeyi açan
    herkese görünür (BR-9: yalnızca Yönetici ve İK).

    Bugünkü davranışı sabitler; D12 düzeltmesi bu testi bilinçli olarak değiştirir.
    """
    response = client.get("/requests")
    assert response.status_code == 200
    assert "Saglik" in [row[4] for row in parse(response.text).rows]
