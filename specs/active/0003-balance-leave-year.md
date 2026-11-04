# Spec 0003 — Bekleyen düşümü, izin yılı ve devir (mini)

- Status: In progress
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

- [ ] CB-1 — **Bakiye ve izin yılı (BR-4).** İzin yılı, son yıldönümünden (kıdem 0 iken işe
  giriş gününden) başlar. Hak = bu izin yılının hakkı. Devir = önceki izin yıllarında kazanılan
  hakların toplamı − bu izin yılından önce başlayan onaylı taleplerin günleri. Kullanılan = bu
  izin yılında veya sonrasında başlayan onaylı taleplerin günleri. Bekleyen = tüm bekleyen
  taleplerin günleri. Kalan = Devir + Hak − Kullanılan − Bekleyen. Reddedilen talep hiçbir
  sütunu etkilemez. Ayşe Yılmaz: bugün 2027-01-01 → 26 · 322 · 10 · 3 · 335; yıldönümü geçince
  2027-03-15 → 26 · 338 · 0 · 3 · 361 (Temmuz 2026'daki 10 günlük onaylı talep devirden düşülür,
  kalan devreder). Artık yılda 29 Şubat sınırı Devir'de görünür ve D2'den bağımsızdır (0002
  VERIFY N1): Ahmet Çelik bugün 2024-02-28 → Devir 28 · 2024-02-29 → Devir 42.
- [ ] CB-2 — **Ana sayfa bakiye tablosu.** Sütunlar: `Ad | Birim | Hak | Devir | Kullanilan |
  Bekleyen | Kalan`. Seed ile: Ayse Yilmaz · IT · 26 · 322 · 10 · 3 · 335 — Mehmet Demir ·
  Muhasebe · 20 · 90 · 0 · 3 · 107 — Zeynep Kaya · IK · 14 · 0 · 0 · 1 · 13 — Ahmet Celik · IT ·
  20 · 70 · 0 · 5 · 85 — Elif Sahin · Satis · 0 · 0 · 0 · 0 · 0. Her satırda Kalan = Devir + Hak
  − Kullanılan − Bekleyen.
- [ ] CB-3 — **Yeni talep ve bakiye.** Geçerli yeni talep kaydedildiği anda Bekleyen ve Kalan'a
  yansır: Mehmet Demir 2026-11-16 → 2026-11-18 (3 gün) sonrası Bekleyen 6, Kalan 104. Yeni talep
  kontrolü bu Kalan'ı kullanır; eşitlik davranışı (D6) olduğu gibi kalır. Zeynep Kaya
  (Kalan 13): 14 gün (2026-12-01 → 2026-12-18) → hata sayfası · 13 gün (→ 2026-12-17) → kayıt
  oluşmaz, hata gösterilmez (D6) · 12 gün (→ 2026-12-16) → kaydedilir. Elif Şahin (Kalan 0):
  1 gün → hata sayfası.

## Preserved behavior
- [ ] PB-1 — Ana sayfa sayaçları değişmez: Bekleyen 4, Onaylanan 1, Reddedilen 3.
- [ ] PB-2 — Talep listesi, yeni talep formu, hatalı girdi davranışı ve adresler 0002/PB-3,
  0002/PB-4 ve 0002/PB-5'teki gibidir.
- [ ] PB-3 — Kapsam dışı sapmalar sürer: kıdem 15 → Hak 20 (D2); Kalan negatif olabilir (D14;
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

## Definition of Done
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [ ] Spec moved to `specs/done/` (immutable there)
