# Spec 0004 — `app.py`'yi katmanlı yapıya taşıma (mini)

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0004-plan.md`
- Source: Kullanıcı isteği, 2026-11-05 — `/refactor` (`docs/architecture.md`, Geçiş durumu). Ticket
  sistemi yok.
- Design: none — no user interface change
- Supersedes: —

## Intent
Tüm uygulama tek dosyada; sıradaki işler (giriş, roller, onay ekranı) doğru katmana yazılsın diye
kodu `docs/architecture.md`'deki `domain` / `services` / `storage` / `web` yapısına taşıyoruz.
Kullanıcı hiçbir fark görmez. Başarı: aynı testler değişmeden yeşil, sayfalar aynı, katman kuralları
artık araçla denetleniyor ve HTML yalnızca şablon dosyalarından üretiliyor.

## Changed behavior
- none — no observable behavior change

## Preserved behavior
Kanıt, baseline'ın 92 testi ve eski ile yeni kodun çıktı karşılaştırmasıdır (bugün 2026-10-25, seed).

- [x] PB-1 — Mevcut testler değişmeden yeşil: `tests/` altındaki mevcut dosyalarda sıfır değişiklik,
  yalnızca yeni dosya eklenebilir.
- [x] PB-2 — `/`, `/requests`, `/new` ve dört hata sayfasının yanıtları bayt bayt aynıdır. Tek
  istisna kaçışlama yazımıdır: `'` için `&#x27;` yerine `&#39;`, `"` için `&quot;` yerine `&#34;`;
  yetersiz bakiye metnindeki `'` de `&#39;` olarak çıkar. Tarayıcıda görünen metin aynıdır.
- [x] PB-3 — HTTP davranışı aynıdır: durum kodları, yönlendirmeler, adresler ve yöntemler (0001/PB-15),
  hata kodları (400; yetersiz bakiye 200) ve beklenmeyen hatada 500.
- [x] PB-4 — Fixture sözleşmesi korunur: `app.py` modül düzeyinde `app` sunar, her yüklemede temiz
  seed verisiyle başlar; `tests/conftest.py` değişmez.
- [x] PB-5 — Kapsam dışı sapmalar aynen sürer: D8, D9'un kalanı, D12, D13, D14, D15.

## Out of scope
- D13 (durum kayıtta Türkçe metin) ve PB-5'teki diğer sapmaların düzeltmesi.
- `debug=True`: D9'un parçası, `app.py`'de D9 notuyla kalır (plan R3, A1).
- Kalıcı veri, giriş, roller, onay ekranı.

## Constraints
- Hedef yapı `docs/architecture.md`: F1–F5 `lint-imports` ile check'te, F6 ruff'ta denetlenir;
  `pyproject.toml`'daki geçici `app.py` istisnaları kalkar; `render_template_string` ve `|safe`
  kullanılmaz.
- Kapsamdaki notlar: D1 yorumu kalkar; spec 0003 F4 (ana sayfa satırı saati iki kez okuyor) ve R2-2
  (başlangıç tarihi testsiz) kapanır; D9 satırındaki kayda yazılan ham HTML testi eklenir.
- "Bugün" `leavemanager/clock.py`'den gelir ve `docs/conventions.md`'deki gibi Europe/Istanbul'a
  göredir. Bu yüzden iki uç durum değişir, ikisi de kayda geçer: sunucunun saat dilimi farklıysa
  gün sınırı İstanbul'a göre işler; yıldönümü gecesi tam gece yarısındaki tek istekte görülebilen
  tutarsız satır (F4) artık oluşmaz.
- Yeni uygulama bağımlılığı yalnızca `tzdata` (`docs/security.md`'de önceden onaylı; Windows'ta
  saat dilimi verisi yok).

## Evidence
Kriter ↔ kanıt (VERIFY, QA alt ajanı, 2026-11-05, `65f2e7a`). Sonrasındaki iki düzeltme turu
yalnızca `tests/test_composition.py` ve planı değiştirdi; HEAD `8150ac8` için CI ve yerel check:
`CHECK GREEN (full, 4 steps, 5 s)`, 97 passed; `./scripts/doctor --strict` 0 fail, 0 warn.

| Acceptance criterion | Evidence | Status |
|---|---|---|
| PB-1 | `git diff --name-status main -- tests/` yalnızca `A tests/test_composition.py`; 7 dosyanın blob'u `main` ile aynı; 92 eski test HEAD kodunda geçti | Pass |
| PB-2 | Eski ve yeni kodun karşılaştırması, 152.092 yanıt: 142.569 bayt eşit, 9.523 yalnızca kaçışlama yazımı, 0 başka fark. Ayrıca LF şablon, farklı hash tohumu, `app.debug=True` ve gerçek sunucu koşuları | Pass |
| PB-3 | Aynı karşılaştırma: durum satırı ve tüm başlıklar; `tests/test_routes.py`, `tests/test_new_request.py`. 500 için repoda test yok, kanıt hata enjeksiyonu (Q5) | Pass |
| PB-4 | `tests/conftest.py` değişmedi; üst üste reload ve araya POST ile her seferinde temiz seed | Pass |
| PB-5 | `test_d8_…`, `test_d9_…`, `test_d12_…`, `test_d13_…`, `test_d14_…`; D15 seed değerleriyle sabit | Pass |
| Katman ve araçlar | `imports` adımı 5 kuralı denetliyor, bilinçli ihlallerin hepsi kırmızı; `datetime.now()` TID251, ölü `noqa` RUF100; `app.py` istisnaları yok; `render_template_string` ve `\|safe` kullanılmıyor (tek geçiş `base.html` yorumu) | Pass |
| Notlar | `test_security_stored_html_is_escaped_on_output`, `test_balance_rows_read_today_once` (F4), `test_br4_request_start_decides_leave_year` (R2-2), D1 yorumu kalktı | Pass |
| Europe/Istanbul | `test_today_follows_istanbul_calendar_day`: UTC ve kışın farklı komşu bölgeler kırmızı; yıl boyu İstanbul'la aynı 30 bölge ayırt edilemez | Pass |
| Gerçek başlatma | `python app.py` başka dizinden: `/`, `/requests`, `/new` 200, şablonlar bulundu, süreç kalmadı | Pass |

Sayfalar değişmediği için ekran görüntüsü gerekmedi: bayt eşitliği daha güçlü kanıttır.
Residue: full ve fast temiz (`check.conf` değişti).

## Review & triage record
Bağımsız review (read-only reviewer alt ajanı) ve VERIFY (QA alt ajanı); triage Kerem Şahin,
2026-11-05. Fix commit'leri bulguları adıyla anar.
- Review 1: **F-1** (orta, `noqa: S201` ölüydü, S201 `create_app`'te `debug=True`'yu görmüyor; R3'ün
  öncülü yanlıştı) real → fix-1, RUF100 · **F-2** (orta, yıl testi bayrama denk geliyordu) real →
  fix-1 · **F-3** (düşük, servis somut depoya bağlı) real → fix-1, `LeaveRepository` · **F-4, F-5,
  F-6** (düşük, belge ve test açıklaması) real → fix-1 · **F-7, F-8, F-9** (bilgi) kayda geçti.
- Review 2: **R2-1, R2-2, R2-3** (belge) real → fix-2. Review 3: temiz.
- VERIFY: tüm kriterler Pass. **Q1** (orta, İstanbul saatinin testi yok) real → fix-3. **Q2, Q3,
  Q5** bilinen sınır, **Q4** bu bölümle kapandı.
- Review 4: **R4-1, R4-2** (düşük) → R-06 işaretlendi. Karar: continue (plan A3), fix-4.
- Review 5: temiz; **KS-1** bilinen sınır.
- Fix turu: 4; dördüncüsü R-06 kararıyla açıldı.

## Known limitations
- HTTP'de görünmeyen farklar (F-7): her uygulama örneği artık kendi deposuna sahip (eskiden modül
  düzeyinde `Db`); `app.name`, logger ve konsol banner'ı `leavemanager.web`, endpoint adları
  `pages.*`.
- `render_template_string` ve `|safe` kullanımı araçla engellenmiyor (Q2). Bugün temiz; personel
  yazma ekranı gelince ruff `banned-api` ve şablon taraması eklenmeli.
- `LeaveRepository` uyumunu tip denetleyici denetlemiyor (Q3); SQL deposu gelince ortak sözleşme
  testi eklenmeli.
- "Beklenmeyen hatada 500"ün repoda testi yok (Q5); D9'un Türkçe 500 sayfası işi kapatır.
- `debug=True` `app.py`'de D9 notuyla duruyor ve ruff bunu görmüyor (F-1); review'da kontrol edilir.
- `status.lower()` karşılaştırması tam eşleşmeye indi (plan R6); kayıtta üç metin dışında durum
  oluşamadığı için gözlenemez.
- Plan A3'teki "ne planda" ifadesi R-06 anlamında (yanlış parçalama) okunmalı; tekil hatalar planda
  da vardı (A1, A2) (KS-1).
- README planda listeliydi, değişmesi gerekmedi (F-8).

## Definition of Done
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale
- [x] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [x] Spec moved to `specs/done/` (immutable there)
