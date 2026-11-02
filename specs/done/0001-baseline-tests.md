# Spec 0001 — Mevcut davranış için baseline (karakterizasyon) testleri (mini)

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0001-plan.md`
- Source: Kullanıcı isteği, 2026-10-25 — `/new-feature "mevcut projedeki kodlar için baseline testleri"` (ticket sistemi yok)
- Design: none — no user interface change
- Supersedes: —

## Intent
Kodu değiştirmeye başlamadan önce LeaveManager'ın bugün kullanıcıya gösterdiği davranışı,
kusurlarıyla birlikte, otomatik testlerle sabitliyoruz. Başarı: sonraki refactor ve bug
düzeltmelerinde bir davranış değişirse `./scripts/check` kırmızıya döner ve değişen davranış test
adından okunur. Bu iş hiçbir davranışı değiştirmez ve bilinen sapmaları (D1–D13,
`docs/domain.md`) düzeltmez; yalnızca kayıt altına alır.

## Changed behavior
- none — no observable behavior change

## Preserved behavior
Aşağıdaki değerler 2026-10-25'te uygulama çalıştırılarak **gözlendi**; seed verisi `app.py`'deki
haliyle. Aksi yazılmadıkça "bugün" = 2026-10-25. Bir kriter bilinen bir sapmayı sabitliyorsa
D-numarası parantez içinde.

**Ana sayfa (`/`)**
- [x] PB-1 — Sayaçlar: Bekleyen 4, Onaylanan 1, Reddedilen 3.
- [x] PB-2 — Bakiye tablosu her personel için Ad, Birim, Hak, Kullanılan, Kalan gösterir:
  Ayse Yilmaz · IT · 26 · 12 · 14 — Mehmet Demir · Muhasebe · 20 · 0 · 20 — Zeynep Kaya · IK ·
  14 · 0 · 14 — Ahmet Celik · IT · 20 · 0 · 20 — Elif Sahin · Satis · 0 · 0 · 0.
- [x] PB-3 — Hak, kıdem = (bugünün yılı − işe giriş yılı) ile belirlenir: 1'den küçük → 0,
  1–5 → 14, 6–15 → 20, 16 ve üzeri → 26 (D1, D2, D3). Ayse Yilmaz (giriş 2008-03-15) için:
  bugün 2008-12-31 → 0 · 2009-01-01 → 14 · 2013-06-01 → 14 · 2014-01-01 → 20 · 2023-12-31 → 20 ·
  2024-01-01 → 26. Zeynep Kaya (giriş 2024-11-10) için bugün 2025-01-02 → 14.
- [x] PB-4 — Kullanılan, onaylı tüm taleplerin takvim günü toplamıdır: yıl ayrımı yoktur ve
  bugünden sonraki onaylı talepler de sayılır (D4, D11). Kalan = Hak − Kullanılan; bekleyen
  talepler düşülmez (D5) ve Kalan negatif olabilir: bugün 2008-12-31 iken Ayse Yilmaz için
  Hak 0, Kullanılan 12, Kalan −12.

**Talep listesi (`/requests`)**
- [x] PB-5 — Tüm talepler kayıt sırasıyla Personel, Başlangıç, Bitiş, Gün, Neden, Durum
  sütunlarıyla listelenir; seed ile 8 satır, ilki `Ayse Yilmaz · 2026-07-06 · 2026-07-17 · 12 ·
  Yaz tatili · Onaylandi`, sonuncusu `Mehmet Demir · 2026-08-03 · 2026-08-03 · 1 · Ozel is ·
  Reddedildi`. Gün = bitiş − başlangıç + 1 takvim günü; Cuma–Pazartesi talebi
  (2026-11-13 → 2026-11-16) 4 gün (D4).
- [x] PB-6 — Durum kayıttaki metniyle gösterilir ve renklidir: `Onaylandi` yeşil, `Beklemede`
  turuncu, `Reddedildi` kırmızı (D13).
- [x] PB-7 — Neden metni HTML kaçışlaması yapılmadan sayfaya yazılır (`<script>alert(1)</script>`
  aynen yer alır) (D9) ve listeyi açan herkes görür (D12).

**Yeni talep (`/new`)**
- [x] PB-8 — Form beş personeli (Ayse Yilmaz, Mehmet Demir, Zeynep Kaya, Ahmet Celik, Elif
  Sahin) seçenek olarak sunar; alanlar: personel, başlangıç, bitiş, neden.
- [x] PB-9 — Geçerli talep (ör. Mehmet Demir, 2026-11-16 → 2026-11-18, 3 gün) `Beklemede` olarak
  listenin sonuna eklenir ve kullanıcı talep listesine yönlendirilir (HTTP 302 → `/requests`).
  Ana sayfada Bekleyen 1 artar; personelin Kalan'ı değişmez (D5). Neden gönderilmezse boş kaydedilir.
- [x] PB-10 — Talep günü Kalan'dan büyükse kayıt oluşmaz; aynı sayfa (HTTP 200)
  `HATA: ERR-412 NullReferenceGibi - bakiye yetersiz. IT'ye bildirin: dahili 4127` metnini
  gösterir (D9). Ör. Zeynep Kaya (Kalan 14) için 15 gün; Elif Sahin (Kalan 0) için 1 gün.
- [x] PB-11 — Talep günü Kalan'a **eşitse** kayıt oluşmaz ve hata gösterilmez; kullanıcı talep
  listesine yönlendirilir (D6). Ör. Zeynep Kaya için 14 gün reddedilir, 13 gün kaydedilir.
- [x] PB-12 — Bitişi başlangıçtan önce olan talep kaydedilir ve negatif gün gösterir
  (2026-11-10 → 2026-11-05: −4 gün) (D7).
- [x] PB-13 — Olmayan personel (ör. 99), geçersiz tarih (ör. `abc`) ya da eksik alan
  (personel, bitiş veya boş form): kayıt oluşmaz, hata gösterilmez, kullanıcı talep listesine
  yönlendirilir (D7).
- [x] PB-14 — Başlangıcı bugünden önce olan talep (ör. 2026-01-05 → 2026-01-06) kabul edilir (D8).

**Adresler ve gezinme**
- [x] PB-15 — Uygulama yalnızca `/` ve `/requests` (GET) ile `/new` (GET, POST) adreslerini
  sunar: bilinmeyen adres ve sonunda `/` olan biçimler (`/new/`, `/requests/`) 404, `/requests`'e
  POST ve `/new`'e PUT 405 döner. Her sayfada (PB-10'daki hata sayfası dahil) Ana Sayfa (`/`),
  Talepler (`/requests`), Yeni Talep (`/new`) bağlantıları bulunur.

## Constraints
- Testler uygulamaya **yalnızca dışarıdan, sayfalar ve form üzerinden** bakar. Uygulamanın iç
  yapısı değiştiğinde testler değişmek zorunda kalmamalı: sonraki refactor "testlerde sıfır
  değişiklik" kuralıyla ilerleyecek (`workflows/refactor.md`).
- Sonuç gerçek tarihe bağlı olmaz: her test "bugün"ü sabit bir tarih olarak belirler.
- Her test seed verisiyle temiz başlar; bir testin oluşturduğu talep diğerine ulaşmaz.
- Bir sapmayı sabitleyen testin adı sapma numarasıyla başlar (`test_d6_…`) ve açıklaması
  `docs/domain.md`'deki satıra referans verir. Sapmanın düzeltmesi bu testi açıkça ve review'dan
  geçerek değiştirir; bu, testi zayıflatmak sayılmaz.
- Testler `./scripts/check`'in parçası olur (`docs/testing.md`, "Check'e bağlanma").
- Split: önerildi (0001 ana sayfa + liste / 0002 form); tek tutuldu — Kerem Şahin, 2026-10-25:
  yeni yetenek yok, kriterler aynı türden (sabitleme), refactor tek parça bir güvenlik ağı ister.
- Renk (PB-6) belirli bir HTML etiketine değil, durum metninin o renkle gösterilmesine göre
  doğrulanır (öz-eleştiri G3; plan bunu şart koşar).

## Out of scope
- `app.py`'de herhangi bir değişiklik — bu iş yalnızca test ekler.
- Sapmaların (D1–D13) düzeltilmesi.
- `debug=True` (D9): yalnızca `python app.py` ile başlatınca etkili, sayfalar üzerinden gözlenemez.
- Görsel düzen (CSS, yerleşim), tarayıcı/e2e testleri, performans.

## Evidence
Kriter ↔ kanıt (VERIFY, QA). Tekrar: `./scripts/check` (tam profil); tek test:
`sh scripts/py -m pytest -p no:cacheprovider -v <test>`. Son kod değişikliği `c7a68f8` için
`CHECK GREEN (full, 3 steps, 3 s)` — 48 passed (QA'nın kendi koşusu). Her kriter için testin,
davranış bozulunca kırmızıya döndüğü bellek içi mutasyonla gösterildi (diske yazmadan).

| Acceptance criterion | Evidence | Status |
|---|---|---|
| CB — none | `git diff main..HEAD -- app.py` boş | Pass |
| PB-1 | `tests/test_dashboard.py::test_counters_with_seed_data` | Pass |
| PB-2 | `test_dashboard.py::test_balance_table_with_seed_data` (başlıklar + 5 satır) | Pass |
| PB-3 | `test_dashboard.py::test_entitlement_by_calendar_year_seniority` · `::test_d2_15_years_gives_20_days` · `::test_d3_seniority_counts_calendar_years_only` | Pass |
| PB-4 | `test_dashboard.py::test_d11_used_days_include_future_approved_requests` · `::test_d5_pending_days_not_deducted` · `::test_d14_remaining_can_go_negative` | Pass |
| PB-5 | `tests/test_requests_list.py::test_lists_seed_requests_in_order` (başlıklar + 8 satır) · `::test_d4_days_are_calendar_days` | Pass |
| PB-6 | `test_requests_list.py::test_d13_status_text_and_color` | Pass |
| PB-7 | `test_requests_list.py::test_d9_reason_rendered_unescaped` · `::test_d12_reason_visible_to_everyone` | Pass |
| PB-8 | `tests/test_new_request.py::test_form_offers_five_employees_and_fields` (seçenekler, alanlar, etiketler) | Pass |
| PB-9 | `test_new_request.py::test_valid_request_is_pending_and_redirects` · `::test_d5_valid_request_does_not_change_remaining` · `::test_missing_reason_saved_empty` | Pass |
| PB-10 | `test_new_request.py::test_d9_insufficient_balance_shows_internal_error_text` | Pass |
| PB-11 | `test_new_request.py::test_d6_equal_to_remaining_is_silently_dropped` (liste sayfası değişmez) · `::test_one_below_remaining_is_saved` | Pass |
| PB-12 | `test_new_request.py::test_d7_end_before_start_saved_with_negative_days` | Pass |
| PB-13 | `test_new_request.py::test_d7_invalid_input_silently_redirects` (5 durum; liste sayfası değişmez) | Pass |
| PB-14 | `test_new_request.py::test_d8_past_dated_request_accepted` | Pass |
| PB-15 | `tests/test_routes.py::test_only_known_routes_respond` (12 durum) · `::test_every_page_has_navigation` | Pass |

## Review & triage record
Bağımsız review (read-only reviewer alt ajanı) ve VERIFY (QA alt ajanı); triage Kerem Şahin,
2026-10-25/26. Fix commit'leri bulguları adıyla anar.
- Review 1: **F1** (orta, başlık/etiket sabitlenmemiş) real → fix-1 · **F2** (düşük, sapmaya duyarlı
  değerler D-adı taşımayan testlerde) real → fix-1 · **F3** (düşük, plan dışı `AGENTS.md`) real →
  plan eki A2.
- Review 2: **B1** (düşük, `test_d14` docstring'inde D11 eksik) real → fix-2. Review 3: temiz.
- VERIFY 1: **G1** (orta, PB-11/PB-13 "hata gösterilmez" kanıtsız) real → fix-3 · **G2** (düşük,
  PB-15 405 örnekleri) real → fix-3, kalan kısım bilinen sınır · **I1** (düşük, renk metin olarak
  karşılaştırılıyor) **kabul**: gözlenen renk olduğu gibi sabitlenir, refactor aynı biçimde korur
  (plan R3).
- Review 4: temiz; **O1** (bilgi) **noise**: `test_d6`'dan kaldırılan `"HATA" not in response.text`
  yalnızca tarayıcının hiç göstermediği 302 gövdesine bakıyordu; yerine gelen assert kullanıcının
  yönlendirildiği sayfayı karşılaştırır ve eskisinin kaçırdığı flash senaryosunu yakalar.
- Fix turu: 3 (R-06 sınırına ulaşılmadı). Plan sırasında D14 bulundu ve `docs/domain.md`'ye
  kaydedildi (plan R6).

## Known limitations
- PB-15 "yalnızca bu adresler" HTTP üzerinden örneklenir; yeni bir adres eklenmesi yakalanmaz
  (adres listesini saymak iç yapıya bağlanmak olur — Constraints).
- PB-6 rengi satır içi `style` değeri olarak karşılaştırır (`orange` ≠ `#ffa500`) — I1.
- PB-4 "toplam": seed'de personel başına tek onaylı talep var ve HTTP üzerinden onay yok; birden
  fazla onaylı talebin toplanması gözlenemez.
- Testlerin `app.py`'ye tek bağlantısı fixture sözleşmesidir (`docs/testing.md`, plan R1);
  refactor bunu korumalıdır.

## Definition of Done
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale
- [x] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [x] Spec moved to `specs/done/` (immutable there)
