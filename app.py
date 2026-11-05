# -*- coding: utf-8 -*-
# LeaveManager - Personel Izin Takip Sistemi
# (c) 2015 - Ic gelistirme. Sorumlu: Ahmet
# NOT: Bu dosyaya dokunmadan once Ahmet'e sor. (Ahmet 2019'da ayrildi)
from flask import Flask, request, redirect, render_template_string
from datetime import datetime, date
from html import escape
from leavemanager.domain.errors import DomainError, EmployeeNotFound, InsufficientBalance, InvalidDate, InvalidDateRange, NoLeaveDays
from leavemanager.domain.leave_rules import annual_entitlement, completed_years, leave_balance, validate_request, working_days

app = Flask(__name__)

# ---------------------------------------------------------------
# "Veritabani" - simdilik memory'de, sonra SQL'e gecilecek (2016)
# ---------------------------------------------------------------
class Db:
    employees = []
    requests = []
    next_id = 1

def seed():
    Db.employees = [
        {"id": 1, "name": "Ayse Yilmaz",  "department": "IT",       "hire_date": date(2008, 3, 15)},
        {"id": 2, "name": "Mehmet Demir", "department": "Muhasebe", "hire_date": date(2019, 6, 1)},
        {"id": 3, "name": "Zeynep Kaya",  "department": "IK",       "hire_date": date(2024, 11, 10)},
        {"id": 4, "name": "Ahmet Celik",  "department": "IT",       "hire_date": date(2020, 2, 29)},  # artik yil - dikkat
        {"id": 5, "name": "Elif Sahin",   "department": "Satis",    "hire_date": date(2026, 6, 1)},
    ]
    Db.requests = [
        {"id": 1, "employee_id": 1, "start": date(2026, 7, 6),  "end": date(2026, 7, 17), "reason": "Yaz tatili",      "status": "Onaylandi"},
        {"id": 2, "employee_id": 2, "start": date(2026, 11, 2), "end": date(2026, 11, 4), "reason": "Aile ziyareti",   "status": "Beklemede"},
        {"id": 3, "employee_id": 3, "start": date(2026, 11, 9), "end": date(2026, 11, 9), "reason": "Saglik",          "status": "Beklemede"},
        {"id": 4, "employee_id": 4, "start": date(2026, 12, 21),"end": date(2026, 12, 25),"reason": "Yilbasi oncesi",  "status": "Beklemede"},
        {"id": 5, "employee_id": 1, "start": date(2026, 12, 28),"end": date(2026, 12, 30),"reason": "Yil sonu",        "status": "Beklemede"},
        {"id": 6, "employee_id": 5, "start": date(2026, 10, 5), "end": date(2026, 10, 7), "reason": "Tasinma",         "status": "Reddedildi"},
        {"id": 7, "employee_id": 3, "start": date(2026, 9, 14), "end": date(2026, 9, 25), "reason": "Uzun tatil",      "status": "Reddedildi"},
        {"id": 8, "employee_id": 2, "start": date(2026, 8, 3),  "end": date(2026, 8, 3),  "reason": "Ozel is",         "status": "Reddedildi"},
    ]
    Db.next_id = 9

seed()

# ---------------------------------------------------------------
# Servis katmani - tum is mantigi burada (ve biraz da HTML :))
# ---------------------------------------------------------------
class LeaveService:

    # Kidem -> hak edilen izin. 1-5 yil arasi 15 gun.
    # (tablo IK el kitabindan, 2014 baskisi)
    def get_entitlement(self, emp):
        return annual_entitlement(self.get_seniority_years(emp))

    def get_seniority_years(self, emp):
        today = datetime.now().date()
        return completed_years(emp["hire_date"], today)

    def calc_days(self, start, end):
        return working_days(start, end)

    def get_balance(self, emp):
        today = datetime.now().date()
        approved = []
        pending = 0
        for r in Db.requests:
            if r["employee_id"] == emp["id"]:
                days = self.calc_days(r["start"], r["end"])
                if r["status"] == "Onaylandi":
                    approved.append((r["start"], days))
                if r["status"] == "Beklemede":
                    pending += days
        return leave_balance(emp["hire_date"], today, approved, pending)

    def get_remaining(self, emp):
        return self.get_balance(emp).remaining

    def create_request(self, emp_id, start, end, reason):
        emp = None
        for e in Db.employees:
            if e["id"] == emp_id:
                emp = e
        if emp is None:
            raise EmployeeNotFound
        validate_request(start, end, self.get_remaining(emp))
        if start < datetime.now().date():
            pass  # gecmis tarih... IK bazen geriye donuk giriyor, dokunma
        Db.requests.append({"id": Db.next_id, "employee_id": emp_id, "start": start,
                            "end": end, "reason": reason, "status": "Beklemede"})
        Db.next_id += 1

    def status_badge(self, status):
        # renkler: UI isi ama burada pratik oluyor
        color = "#999"
        if status == "Onaylandi":
            color = "green"
        if status.lower() == "beklemede":
            color = "orange"
        if status == "Reddedildi":
            color = "red"
        return "<b style='color:%s'>%s</b>" % (color, status)

svc = LeaveService()

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
    bekleyen = len([r for r in Db.requests if r["status"] == "Beklemede"])
    onaylanan = len([r for r in Db.requests if r["status"] == "Onaylandi"])
    reddedilen = len([r for r in Db.requests if r["status"] == "Reddedildi"])
    body = "<div class='kutu'>Bekleyen: <b>%d</b></div><div class='kutu'>Onaylanan: <b>%d</b></div><div class='kutu'>Reddedilen: <b>%d</b></div>" % (bekleyen, onaylanan, reddedilen)
    body += "<h3>Personel Bakiyeleri</h3><table><tr><th>Ad</th><th>Birim</th><th>Hak</th><th>Devir</th><th>Kullanilan</th><th>Bekleyen</th><th>Kalan</th></tr>"
    for e in Db.employees:
        balance = svc.get_balance(e)
        body += "<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
            e["name"], e["department"], svc.get_entitlement(e), balance.carried_over, balance.used, balance.pending, balance.remaining)
    body += "</table>"
    return render_template_string(PAGE, body=body)

@app.route("/requests")
def list_requests():
    body = "<h3>Izin Talepleri</h3><table><tr><th>Personel</th><th>Baslangic</th><th>Bitis</th><th>Gun</th><th>Neden</th><th>Durum</th></tr>"
    for r in Db.requests:
        emp = [e for e in Db.employees if e["id"] == r["employee_id"]][0]
        body += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            emp["name"], r["start"], r["end"], svc.calc_days(r["start"], r["end"]), escape(r["reason"]), svc.status_badge(r["status"]))
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
        return datetime.strptime(value or "", "%Y-%m-%d").date()
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
    options = "".join("<option value='%d'>%s</option>" % (e["id"], e["name"]) for e in Db.employees)
    body = """<h3>Yeni Talep</h3><form method="post">
    Personel: <select name="employee_id">%s</select><br><br>
    Baslangic: <input type="date" name="start"><br><br>
    Bitis: <input type="date" name="end"><br><br>
    Neden: <input type="text" name="reason"><br><br>
    <input type="submit" value="Kaydet"></form>""" % options
    return render_template_string(PAGE, body=body)

if __name__ == "__main__":
    app.run(port=5000, debug=True)  # debug acik kalsin, kolay oluyor
