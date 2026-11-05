# Spec 0004 — `app.py`'yi katmanlı yapıya taşıma (mini)

- Status: In progress
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

- [ ] PB-1 — Mevcut testler değişmeden yeşil: `tests/` altındaki mevcut dosyalarda sıfır değişiklik,
  yalnızca yeni dosya eklenebilir.
- [ ] PB-2 — `/`, `/requests`, `/new` ve dört hata sayfasının yanıtları bayt bayt aynıdır. Tek
  istisna kaçışlama yazımıdır: `'` için `&#x27;` yerine `&#39;`, `"` için `&quot;` yerine `&#34;`;
  yetersiz bakiye metnindeki `'` de `&#39;` olarak çıkar. Tarayıcıda görünen metin aynıdır.
- [ ] PB-3 — HTTP davranışı aynıdır: durum kodları, yönlendirmeler, adresler ve yöntemler (0001/PB-15),
  hata kodları (400; yetersiz bakiye 200) ve beklenmeyen hatada 500.
- [ ] PB-4 — Fixture sözleşmesi korunur: `app.py` modül düzeyinde `app` sunar, her yüklemede temiz
  seed verisiyle başlar; `tests/conftest.py` değişmez.
- [ ] PB-5 — Kapsam dışı sapmalar aynen sürer: D8, D9'un kalanı, D12, D13, D14, D15.

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

## Definition of Done
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [ ] Spec moved to `specs/done/` (immutable there)
