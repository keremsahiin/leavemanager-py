# Spec 0003 — Bekleyen düşümü, izin yılı ve devir (mini)

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0003-plan.md`
- Source: İyileştirme listesi, satır 9–10 (listede BR-4, BR-5) — kullanıcı isteği, 2026-11-02,
  `/change "B2-B3-B4-B5 tek kalemde yap"`. Ticket sistemi yok. Satır 7–8: spec 0002.
- Design: Tasarım dosyası yok. Değişen görünüm ana sayfadaki bakiye tablosu (CB-2); sayfanın
  mevcut stili korunur. Kanıt: önce / sonra ekran görüntüsü (VERIFY).
- Supersedes: 0002/CB-2 (ana sayfa değerleri), 0002/CB-3 (örnek değerler), 0002/PB-2,
  0001/PB-9 (Kalan değişmez cümlesi)

## Intent
Bakiye yasal kurala uygun hesaplansın: bekleyen talepler bakiyeden düşülsün ve her izin yılında
yeni hak eklenirken kullanılmayan gün devretsin. Personel ve İK ana sayfada bakiyenin nereden
geldiğini (hak, devir, kullanılan, bekleyen) satır satır görür. Bu iş `docs/domain.md`'deki D5,
D10 ve D11 sapmalarını kapatır.

| Listedeki madde | `docs/domain.md` | Kapanan sapma |
|---|---|---|
| BR-4 bekleyen düşülsün, ana sayfada ayrı gösterilsin | BR-4 (bekleyen kısmı) | D5 |
| BR-5 izin yılı yıldönümünden başlar | BR-4 (birikim ve devir kısmı) | D10, D11 |

**Kararlar (2026-11-02, Kerem Şahin):**
- İzin yılı yorumu A: her yıldönümünde yeni hak eklenir, kullanılmayan gün yanmaz, devir tavanı
  yok (`docs/domain.md` BR-4, İş K. md. 53).
- Açılış bakiyesi: hesap işe giriş tarihinden başlar, önceki devir 0. Sistemde geçmiş talep
  olmadığı için seed devirleri büyük çıkar (Ayşe 322); gerçek devirlerin yüklenmesi canlıya
  geçişten önce ayrı bir iştir (Out of scope).
- Ana sayfa tablosu: `Ad | Birim | Hak | Devir | Kullanılan | Bekleyen | Kalan`.
- Yıldönümünü kapsayan talep, başladığı izin yılına tümüyle yazılır; tarihinden bağımsız tüm
  bekleyen talepler Bekleyen'e girer.

## Changed behavior
Aksi yazılmadıkça "bugün" = 2026-10-25 ve veri seed'dir.

- [x] CB-1 — **Bakiye ve izin yılı (BR-4).** İzin yılı, son yıldönümünden (kıdem 0 iken işe
  giriş gününden) başlar. Hak = bu izin yılının hakkı. Devir = önceki izin yıllarında kazanılan
  hakların toplamı − bu izin yılından önce başlayan onaylı taleplerin günleri. Kullanılan = bu
  izin yılında veya sonrasında başlayan onaylı taleplerin günleri. Bekleyen = tüm bekleyen
  taleplerin günleri. Kalan = Devir + Hak − Kullanılan − Bekleyen. Reddedilen talep hiçbir
  sütunu etkilemez. Ayşe Yılmaz: bugün 2027-01-01 → 26 · 322 · 10 · 3 · 335; yıldönümü geçince
  2027-03-15 → 26 · 338 · 0 · 3 · 361 (Temmuz 2026'daki 10 günlük onaylı talep devirden düşülür,
  kalan devreder). Artık yılda 29 Şubat sınırı Devir'de görünür ve D2'den bağımsızdır (0002
  VERIFY N1): Ahmet Çelik bugün 2024-02-28 → Devir 28 · 2024-02-29 → Devir 42.
- [x] CB-2 — **Ana sayfa bakiye tablosu.** Sütunlar: `Ad | Birim | Hak | Devir | Kullanilan |
  Bekleyen | Kalan`. Seed ile: Ayse Yilmaz · IT · 26 · 322 · 10 · 3 · 335 — Mehmet Demir ·
  Muhasebe · 20 · 90 · 0 · 3 · 107 — Zeynep Kaya · IK · 14 · 0 · 0 · 1 · 13 — Ahmet Celik · IT ·
  20 · 70 · 0 · 5 · 85 — Elif Sahin · Satis · 0 · 0 · 0 · 0 · 0. Her satırda Kalan = Devir + Hak
  − Kullanılan − Bekleyen.
- [x] CB-3 — **Yeni talep ve bakiye.** Geçerli yeni talep kaydedildiği anda Bekleyen ve Kalan'a
  yansır: Mehmet Demir 2026-11-16 → 2026-11-18 (3 gün) sonrası Bekleyen 6, Kalan 104. Yeni talep
  kontrolü bu Kalan'ı kullanır; eşitlik davranışı (D6) olduğu gibi kalır. Zeynep Kaya
  (Kalan 13): 14 gün (2026-12-01 → 2026-12-18) → hata sayfası · 13 gün (→ 2026-12-17) → kayıt
  oluşmaz, hata gösterilmez (D6) · 12 gün (→ 2026-12-16) → kaydedilir. Elif Şahin (Kalan 0):
  1 gün → hata sayfası.

## Preserved behavior
- [x] PB-1 — Ana sayfa sayaçları değişmez: Bekleyen 4, Onaylanan 1, Reddedilen 3.
- [x] PB-2 — Talep listesi, yeni talep formu, hatalı girdi davranışı ve adresler 0002/PB-3,
  0002/PB-4 ve 0002/PB-5'teki gibidir.
- [x] PB-3 — Kapsam dışı sapmalar sürer: kıdem 15 → Hak 20 (D2); Kalan negatif olabilir (D14;
  Ayşe, bugün 2009-01-01 → Hak 0, Devir 0, Kullanılan 10, Bekleyen 3, Kalan −13).

## Out of scope
- Gerçek açılış bakiyelerinin (İK devirleri) yüklenmesi: canlıya geçişten önce ayrı iş.
- Resmî tatiller (D15); D2, D6, D7, D8, D9, D12, D13, D14; refactor.

## Constraints
- Split: 0002 → 0003 (bkz. spec 0002 Constraints).
- D5 ve D11'i sabitleyen testler ve bu değerlere bağlı testler bilinçli olarak değişir; her
  test değişikliği planda listelenir.
- Ship'te `docs/domain.md`: D5, D10, D11 satırları bu spec'e referansla silinir; BR-4 kod
  durumu; açılış bakiyesi kararı ve canlı öncesi devir işi açık kararlara yazılır.

## Evidence
Kriter ↔ kanıt (VERIFY, QA alt ajanı, 2026-11-04). Tekrar: `./scripts/check` (tam profil); tek
test: `sh scripts/py -m pytest -p no:cacheprovider -v <test>`. HEAD `9bc64fa` için QA'nın kendi
koşusu: `CHECK GREEN (full, 3 steps, 3 s)` — 72 passed; `./scripts/doctor --strict` 0 fail, 0 warn.
Bağımsız hesapla karşılaştırma, 0 fark: 2007–2046 arasının her günü, 5 personel (73.050 satır);
`leave_balance` 150.000 rastgele durum; Kalan yalnızca yıldönümünde ve o yılın hakkı kadar artıyor.
47 mutasyonun 46'sı yakalandı (bellekte, diske yazmadan); kalan biri R2-2.

| Acceptance criterion | Evidence | Status |
|---|---|---|
| CB-1 | `tests/test_dashboard.py::test_br4_used_counts_from_current_leave_year` (2) · `::test_br4_carry_over_feb29_anniversary` (2) · `::test_br4_pending_days_deducted` · `::test_balance_table_with_seed_data` · `tests/test_leave_rules.py` (8; izin yılı sınırları, plan A1) | Pass |
| CB-2 | `test_dashboard.py::test_balance_table_with_seed_data` (başlıklar + 5 satır) · `::test_br4_row_arithmetic` (2) | Pass |
| CB-3 | `tests/test_new_request.py::test_br4_new_request_reduces_remaining` · `::test_d9_insufficient_balance_shows_internal_error_text` (Zeynep 14, Elif 1) · `::test_d6_equal_to_remaining_is_silently_dropped` (13) · `::test_one_below_remaining_is_saved` (12) | Pass |
| PB-1 | `test_dashboard.py::test_counters_with_seed_data` | Pass |
| PB-2 | `tests/test_requests_list.py` · `tests/test_routes.py` · `test_new_request.py` form, geçerli talep, boş neden, D7, D8 testleri; `/requests` ve `/new` HTML'i önce/sonra bayt eşit | Pass |
| PB-3 | `test_dashboard.py::test_d2_15_years_gives_20_days` (3) · `::test_d14_remaining_can_go_negative` | Pass |
| Design (UI) | `/` ve `/requests`, bugün 2026-10-25, seed: önce (`39bdda7`) / sonra (`9bc64fa`) ekran görüntüleri QA tarafından başsız Chrome ile alındı ve incelendi; tablo 7 sütun ve CB-2 değerleriyle, düzen bozulmamış, `/requests` görüntüleri bayt eşit. Ship anında görüntüler PR'a yüklenmedi (tarayıcı eklentisi bağlı değildi, `gh` resim yükleyemiyor): kopyaları Kerem Şahin'in masaüstünde, PR'a sonradan eklenecek; PR'da metin karşılaştırması var | Pass |

## Review & triage record
Bağımsız review (read-only reviewer alt ajanı) ve VERIFY (QA alt ajanı); triage Kerem Şahin,
2026-11-04. Fix commit'leri bulguları adıyla anar.
- Review 1: **F1** (orta, izin yılı sınırları ve çoklu talep testsiz; 6 mutant yeşil kaldı) real →
  fix-1, `tests/test_leave_rules.py` · **F2** (düşük, D1/D2/D13/D14 satırları taşınan kodu
  gösteriyordu) real → fix-1 · **F3** (düşük, D15'e bağlı değerler adlandırılmamış) real → fix-1 ·
  **F4** (düşük, ana sayfa satırı saati iki kez okuyor) **kabul**: bilinen sınır · **F5** (bilgi,
  planda listelenmeyen satırlar) → plan eki A1 · **F6** (bilgi, `Supersedes`'te 0001/PB-9 eksik)
  real → fix-1.
- Review 2: fix-1 temiz; **R2-1** (bilgi, fixture sözleşmesi metni) real → fix-2, plan eki A2 ·
  **R2-2** (bilgi, `app.py`'nin başlangıç tarihini geçmesi testsiz) **kabul**: bilinen sınır.
- Review 3: temiz.
- VERIFY: 7/7 Pass. İlk koşuda ekran görüntüsü alınamadı (**Q1**), başsız Chrome ile kapandı.
  **Q2** ship'te yapıldı, **Q3** (düşük) bilinen sınır.
- Fix turu: 2 (R-06 sınırına ulaşılmadı).

## Known limitations
- Ana sayfa satırı saati iki kez okuyor (`app.py`, F4): yıldönümü gecesi tam gece yarısındaki tek
  istekte satır hesabı tutmayabilir, yenileyince düzelir. Refactor "bugün"ü tek noktadan verince
  kapanır.
- `app.py`'nin `leave_balance`'a talebin başlangıç tarihini geçmesi testsiz (R2-2): HTTP'de onay
  yolu ve seed'de yıldönümünü kapsayan onaylı talep yok. Yanlış tarih yalnızca Devir ile
  Kullanılan arasında gün kaydırır, Kalan değişmez. Onay ekranı (BR-8) ya da refactor kapatır.
- CB-1'in "veya sonrasında" cümlesini yalnızca `test_d14_remaining_can_go_negative` koruyor (Q3):
  D14 düzeltilirken `tests/test_leave_rules.py`'ye tek bir test eklenmeli.
- Seed devirleri gerçek değil (Ayşe 322): sistemde geçmiş talep yok, açılış devri 0. Canlıya
  geçmeden önce gerçek devirler yüklenmeli (`docs/domain.md`, Open decisions).
- Aynı sayfada "Bekleyen" iki birimle görünür: sayaç talep sayısı (PB-1), sütun gün sayısı (CB-2).

## Definition of Done
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale
- [x] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [x] Spec moved to `specs/done/` (immutable there)
