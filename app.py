# -*- coding: utf-8 -*-
# LeaveManager - Personel Izin Takip Sistemi
# (c) 2015 - Ic gelistirme. Sorumlu: Ahmet
# NOT: Bu dosyaya dokunmadan once Ahmet'e sor. (Ahmet 2019'da ayrildi)
from flask import Flask, request, redirect, render_template_string
from datetime import date
from html import escape
from leavemanager.domain.errors import DomainError, EmployeeNotFound, InsufficientBalance, InvalidDate, InvalidDateRange, NoLeaveDays
from leavemanager.services import LeaveService
from leavemanager.storage import InMemoryRepository

app = Flask(__name__)
svc = LeaveService(InMemoryRepository())

def status_badge(status):
    colors = {"Onaylandi": "green", "Beklemede": "orange", "Reddedildi": "red"}
    return "<b style='color:%s'>%s</b>" % (colors.get(status, "#999"), status)

PAGE = """
<html><head><meta charset="utf-8"><title>LeaveManager</title>
<style>body{font-family:Arial;margin:30px} table{border-collapse:collapse}
td,th{border:1px solid #ccc;padding:6px 10px} .kutu{display:inline-block;border:1px solid #ccc;padding:10px 20px;margin-right:10px}</style>
</head><body>
<h2>LeaveManager</h2>
<p><a href="/">Ana Sayfa</a> | <a href="/requests">Talepler</a> | <a href="/new">Yeni Talep</a></p>
{{ body|safe }}
</body></html>
"""

@app.route("/")
def dashboard():
    counts = svc.status_counts()
    body = "<div class='kutu'>Bekleyen: <b>%d</b></div><div class='kutu'>Onaylanan: <b>%d</b></div><div class='kutu'>Reddedilen: <b>%d</b></div>" % (counts.pending, counts.approved, counts.rejected)
    body += "<h3>Personel Bakiyeleri</h3><table><tr><th>Ad</th><th>Birim</th><th>Hak</th><th>Devir</th><th>Kullanilan</th><th>Bekleyen</th><th>Kalan</th></tr>"
    for row in svc.balance_rows():
        balance = row.balance
        body += "<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
            row.employee.name, row.employee.department, balance.entitlement, balance.carried_over, balance.used, balance.pending, balance.remaining)
    body += "</table>"
    return render_template_string(PAGE, body=body)

@app.route("/requests")
def list_requests():
    body = "<h3>Izin Talepleri</h3><table><tr><th>Personel</th><th>Baslangic</th><th>Bitis</th><th>Gun</th><th>Neden</th><th>Durum</th></tr>"
    for r in svc.request_rows():
        body += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            r.employee_name, r.start, r.end, r.days, escape(r.reason), status_badge(r.status))
    body += "</table>"
    return render_template_string(PAGE, body=body)

ERROR_MESSAGES = {
    EmployeeNotFound: "Personel bulunamadı.",
    InvalidDate: "Başlangıç ve bitiş tarihi geçerli olmalı.",
    InvalidDateRange: "Bitiş tarihi başlangıç tarihinden önce olamaz.",
    NoLeaveDays: "Seçilen aralıkta izin günü yok.",
}

def read_employee_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise EmployeeNotFound from None

def read_date(value):
    try:
        return date.fromisoformat(value or "")
    except ValueError:
        raise InvalidDate from None

@app.route("/new", methods=["GET", "POST"])
def new_request():
    if request.method == "POST":
        try:
            emp_id = read_employee_id(request.form.get("employee_id"))
            start = read_date(request.form.get("start"))
            end = read_date(request.form.get("end"))
            svc.create_request(emp_id, start, end, request.form.get("reason", ""))
        except InsufficientBalance:
            return render_template_string(PAGE, body="<p style='color:red'>HATA: ERR-412 NullReferenceGibi - bakiye yetersiz. IT'ye bildirin: dahili 4127</p>")
        except DomainError as error:
            return render_template_string(PAGE, body="<p style='color:red'>%s</p>" % ERROR_MESSAGES[type(error)]), 400
        return redirect("/requests")
    options = "".join("<option value='%d'>%s</option>" % (e.id, e.name) for e in svc.employees())
    body = """<h3>Yeni Talep</h3><form method="post">
    Personel: <select name="employee_id">%s</select><br><br>
    Baslangic: <input type="date" name="start"><br><br>
    Bitis: <input type="date" name="end"><br><br>
    Neden: <input type="text" name="reason"><br><br>
    <input type="submit" value="Kaydet"></form>""" % options
    return render_template_string(PAGE, body=body)

if __name__ == "__main__":
    app.run(port=5000, debug=True)  # debug acik kalsin, kolay oluyor
