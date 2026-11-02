# Spec 0002 — Kıdem yıldönümü ve iş günü sayımı (mini)

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0002-plan.md`
- Source: İyileştirme listesi, satır 7–8 (listede BR-2, BR-3) — kullanıcı isteği, 2026-11-02,
  `/change "B2-B3-B4-B5 tek kalemde yap"`. Ticket sistemi yok. Satır 9–10: spec 0003.
- Design: Tasarım dosyası yok. Sayfa düzeni değişmez; değişen yalnızca gösterilen sayılar
  (Hak, Kullanılan, Kalan, Gün). Kanıt: önce / sonra ekran görüntüsü (VERIFY).
- Supersedes: 0001/PB-2 ve 0001/PB-4 (değerler), 0001/PB-3, 0001/PB-5 (Gün sütunu),
  0001/PB-10 ve 0001/PB-11 (örnek değerler), 0001/PB-12 (−4 gün)

## Intent
Kıdem ve izin günü yasal kurala uygun hesaplansın: kıdem işe giriş yıldönümünde dolsun
(29 Şubat dahil), izin günü yalnızca hafta içi günlerden sayılsın. Personel, İK ve yönetici
ekranlarda doğru hak ve gün sayısını görür. Bu iş `docs/domain.md`'deki D3 ve D4 sapmalarını
kapatır; bakiye modeli (bekleyen düşümü, izin yılı, devir) spec 0003'ün işidir.

| Listedeki madde | `docs/domain.md` | Kapanan sapma |
|---|---|---|
| BR-2 kıdem yıldönümü, 29 Şubat | BR-2 | D3 |
| BR-3 iş günü (hafta sonu hariç) | BR-3 (resmî tatiller hariç, bkz. Out of scope) | D4 |

## Changed behavior
Aksi yazılmadıkça "bugün" = 2026-10-25 ve veri seed'dir. Değerler kurala göre hesaplandı.

- [x] CB-1 — **Kıdem (BR-2).** Kıdem, işe giriş yıldönümünde dolan tam yıl sayısıdır;
  yıldönümü günü yıl dolmuş sayılır. 29 Şubat'ta işe girenin yılı artık olmayan yıllarda
  28 Şubat'ta, artık yıllarda 29 Şubat'ta dolar. Hak, kıdeme göre bugünkü tablodan gelir (D2
  sürer). Ana sayfada Hak: Ayşe Yılmaz (giriş 2008-03-15) bugün 2009-03-14 → 0 · 2009-03-15 →
  14 · 2014-03-14 → 14 · 2014-03-15 → 20 · 2024-03-14 → 20 · 2024-03-15 → 26. Ahmet Çelik
  (giriş 2020-02-29): 2021-02-27 → 0 · 2021-02-28 → 14 · 2026-02-27 → 14 · 2026-02-28 → 20 ·
  artık yılda 2036-02-28 → 20 · 2036-02-29 → 26. Zeynep Kaya (giriş 2024-11-10): 2025-11-09 →
  0 · 2025-11-10 → 14.
- [x] CB-2 — **İzin günü (BR-3).** Bir talebin izin günü, başlangıç ve bitiş dahil aralıktaki
  Pazartesi–Cuma günlerinin sayısıdır; aynı sayı talep listesinin Gün sütununda, ana sayfadaki
  Kullanılan'da ve yeni talep kontrolünde kullanılır (I-3). Cuma–Pazartesi talebi
  (2026-11-13 → 2026-11-16) 2 gün; yalnızca hafta sonu (2026-11-14 → 2026-11-15) 0 gün. Seed
  talep listesinin Gün sütunu sırasıyla: 10, 3, 1, 5, 3, 3, 10, 1. Ana sayfa seed ile: Ayse
  Yilmaz · IT · 26 · 10 · 16; diğer dört satır değişmez (Mehmet 20 · 0 · 20, Zeynep 14 · 0 · 14,
  Ahmet 20 · 0 · 20, Elif 0 · 0 · 0).
- [x] CB-3 — **Yeni talep kontrolü.** Bakiye kontrolü CB-2'deki gün sayısıyla yapılır; eşitlik
  davranışı (D6) olduğu gibi kalır. Zeynep Kaya (Kalan 14): 15 gün (2026-12-01 → 2026-12-21) →
  yetersiz bakiye hata sayfası · 14 gün (2026-12-01 → 2026-12-18) → kayıt oluşmaz, hata
  gösterilmez (D6) · 13 gün (2026-12-01 → 2026-12-17) → kaydedilir · 2026-12-01 → 2026-12-15
  (15 takvim, 11 iş günü; bugün hata sayfası) → kaydedilir. Elif Şahin (Kalan 0): 1 gün
  (2026-11-16) → hata sayfası.

## Preserved behavior
Spec 0001'in sabitlediği ve bu işin değiştirmediği davranış; değerler 0001 testlerinde gözlendi.

- [x] PB-1 — Ana sayfa sayaçları değişmez: Bekleyen 4, Onaylanan 1, Reddedilen 3.
- [x] PB-2 — Bakiye modeli değişmez (spec 0003'e kadar): sütunlar Ad, Birim, Hak, Kullanilan,
  Kalan; Kalan = Hak − Kullanılan; bekleyen talepler düşülmez, yeni talep Kalan'ı değiştirmez
  (D5; Mehmet Demir 3 günlük talep sonrası Kalan 20); Kullanılan yıl ayrımı olmadan tüm onaylı
  talepleri, gelecektekiler dahil, sayar (D11; Ayşe bugün 2009-01-01 ve 2027-01-01 → 10);
  Kalan negatif olabilir (D14; Ayşe bugün 2008-12-31 → Hak 0, Kullanılan 10, Kalan −10).
- [x] PB-3 — Talep listesi: kayıt sırası, sütunlar (Personel, Baslangic, Bitis, Gun, Neden,
  Durum), durum metni ve rengi (D13), neden metninin kaçışlanmadan yazılması (D9) ve herkese
  görünmesi (D12) değişmez. D9'un XSS düzeltmesi bu işten önce ship edilirse o düzeltmenin
  davranışı korunur.
- [x] PB-4 — Yeni talep: beş personel seçeneği, alanlar ve etiketler; geçerli talep `Beklemede`
  olarak listenin sonuna eklenir, kullanıcı `/requests`'e yönlendirilir (HTTP 302); neden
  gönderilmezse boş kaydedilir; yetersiz bakiye hata metni aynen (D9); olmayan personel,
  geçersiz tarih ve eksik alan için kayıt oluşmaz, hata gösterilmez (D7); bitişi başlangıçtan
  önce olan ve yalnızca hafta sonunu kapsayan talep kaydedilir, Gün 0 (D7); geçmiş tarihli
  talep kabul edilir (D8).
- [x] PB-5 — Adresler ve gezinme 0001/PB-15'teki gibidir.

## Out of scope
- Bekleyen talebin bakiyeden düşülmesi, izin yılı, devir ve ana sayfa tablosunun yeni
  sütunları: spec 0003 (listede satır 9–10; D5, D10, D11).
- Resmî tatil ve bayram günleri (BR-3'ün tatil kısmı): takvim kaynağı açık karar.
- D2 (ayrı `/fix-bug`), D6, D7, D8, D9, D12, D13, D14; BR-1 tablosu; yaş kuralı; iznin bölünmesi.
- `app.py`'nin katmanlı yapıya taşınması (refactor). Yeni yazılan kod `docs/architecture.md`
  kurallarına uyar; yeri planın kararıdır.

## Constraints
- Split: proposed 0002 (BR-2, BR-3) → 0003 (BR-4 bekleyen, izin yılı ve devir, tablo); split
  accepted — Kerem Şahin, 2026-11-02 (boyut kuralı: tek kalemde 11 kriter).
- Testler yalnızca HTTP üzerinden, sabit "bugün" ile (`docs/testing.md`). D3 ve D4'ü sabitleyen
  testler ve bu değerlere bağlı testler bilinçli olarak değişir; her test değişikliği planda
  listelenir (kural 5 ihlali değildir: `docs/testing.md`).
- Yeni bağımlılık yok.
- Ship'te `docs/domain.md` güncellenir: D3 ve D4 satırları bu spec'e referansla silinir; BR-2 ve
  BR-3'ün kod durumu güncellenir.

## Evidence
Kriter ↔ kanıt (VERIFY, QA alt ajanı, 2026-11-02). Tekrar: `./scripts/check` (tam profil); tek
test: `sh scripts/py -m pytest -p no:cacheprovider -v <test>`. HEAD `4eefca9` için QA'nın kendi
koşusu: `CHECK GREEN (full, 3 steps, 3 s)` — 60 passed. Spec'teki sayılar uygulamadan bağımsız bir
hesapla yeniden üretildi (iş günü 56.900 aralık, kıdem 133.844 çift; 0 fark). Eski davranış ve 10
mutasyon bellekte geri getirildi (diske yazmadan); her biri en az bir testi kırmızıya çevirdi.

| Acceptance criterion | Evidence | Status |
|---|---|---|
| CB-1 | `tests/test_dashboard.py::test_br2_seniority_completes_on_hire_anniversary` (7) · `::test_br2_feb29_hire_anniversary` (5) · `::test_d2_15_years_gives_20_days` (3; plan A1) · `::test_br1_entitlement_by_seniority` (4) | Pass |
| CB-2 | `tests/test_requests_list.py::test_br3_counts_weekdays_only` · `tests/test_new_request.py::test_d7_weekend_only_request_saved_with_zero_days` (plan A2) · `test_requests_list.py::test_lists_seed_requests_in_order` · `test_dashboard.py::test_balance_table_with_seed_data`; I-3: Kullanılan, liste, `/new` ve servis aynı `working_days` yolundan | Pass |
| CB-3 | `test_new_request.py::test_d9_insufficient_balance_shows_internal_error_text` (Zeynep 15, Elif 1) · `::test_d6_equal_to_remaining_is_silently_dropped` (14) · `::test_one_below_remaining_is_saved` (13) · `::test_br3_balance_check_counts_weekdays` (11 iş / 15 takvim) | Pass |
| PB-1 | `test_dashboard.py::test_counters_with_seed_data` | Pass |
| PB-2 | `test_dashboard.py::test_d5_pending_days_not_deducted` · `::test_d11_used_days_include_future_approved_requests` (2) · `::test_d14_remaining_can_go_negative` · `test_new_request.py::test_d5_valid_request_does_not_change_remaining` | Pass |
| PB-3 | `test_requests_list.py::test_lists_seed_requests_in_order` · `::test_d13_status_text_and_color` · `::test_d9_reason_rendered_unescaped` · `::test_d12_reason_visible_to_everyone` | Pass |
| PB-4 | `test_new_request.py` — form, geçerli talep, boş neden, D9 hata metni (2), D7 geçersiz girdi (5), ters aralık 0 gün, yalnız hafta sonu 0 gün, D8 (13 test) | Pass |
| PB-5 | `tests/test_routes.py::test_only_known_routes_respond` (12) · `::test_every_page_has_navigation` | Pass |
| Design (UI) | `/` ve `/requests`, bugün 2026-10-25, seed: önce (`main`) / sonra (`4eefca9`) ekran görüntüleri PR'da. Fark yalnızca Ayşe satırı 26·12·14 → 26·10·16 ve listede satır 1 ile 7'nin Gün'ü 12 → 10; düzen, sayaçlar, renkler ve `/new` aynı | Pass |

## Review & triage record
Bağımsız review (read-only reviewer alt ajanı) ve VERIFY (QA alt ajanı); triage Kerem Şahin,
2026-11-02. Fix commit'leri bulguları adıyla anar.
- BUILD sırasında plan ekleri: **A1** (D2'ye bağlı iki nokta `test_d2_`'de) ve **A2** (yalnız
  hafta sonu örneği D7 testinde) — sapmaya bağlı değer D-adlı testte durur.
- Review 1: **R1-1** (düşük, `working_days` aralık uzunluğuyla büyüyordu; `/new` ile istek başına
  ~1 sn CPU) real → fix-1 · **R1-2** (düşük, tatil ifadesi ters okunabiliyordu; tatil kısmının
  sapma kaydı yoktu) real → fix-1, D15 kaydedildi · **R1-3** (düşük, Zeynep örneğinde yanlış D5
  notu) real → fix-1 · **R1-4** (bilgi, D7 satırı plan dışı) → plan eki A3 · **R1-5** (bilgi,
  `pyproject.toml` yorumu yanlışlaştı) real → fix-1 (reviewer'ın "refactor'a not" önerisi yerine
  düzeltme: henüz refactor spec'i yok).
- Review 2: temiz (davranış eşitliği 21.566 aralıkta bağımsız doğrulandı).
- VERIFY: 8/8 Pass. **N1** (düşük) ve **N2** (bilgi) bilinen sınır olarak kaydedildi (aşağıda).
- Fix turu: 1 (R-06 sınırına ulaşılmadı).

## Known limitations
- CB-1'in "artık yılda 29 Şubat'ta dolar" kısmının Hak sütunundaki tek kanıtı
  `test_d2_15_years_gives_20_days[Ahmet 2036-02-28]` (VERIFY N1, plan A1): doğru BR-1 tablosuyla
  kıdem 15 → 16 geçişi 26 → 26 görünmez. D2 düzeltmesi bu kanıtı spec 0003'ün Devir sütununa
  taşımalı (Ahmet 2024-02-28 → Devir 28, 2024-02-29 → Devir 42); yoksa sınır testsiz kalır.
- Resmî tatiller izin günü sayılıyor (D15, VERIFY N2): kapsam dışı, `docs/domain.md`'de kayıtlı.
- 0 günlük talepler (ters aralık, yalnız hafta sonu) kaydediliyor: D7 sürer (PB-4).

## Definition of Done
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale
- [x] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [x] Spec moved to `specs/done/` (immutable there)
