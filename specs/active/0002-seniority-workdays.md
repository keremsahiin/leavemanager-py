# Spec 0002 — Kıdem yıldönümü ve iş günü sayımı (mini)

- Status: In progress
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

- [ ] CB-1 — **Kıdem (BR-2).** Kıdem, işe giriş yıldönümünde dolan tam yıl sayısıdır;
  yıldönümü günü yıl dolmuş sayılır. 29 Şubat'ta işe girenin yılı artık olmayan yıllarda
  28 Şubat'ta, artık yıllarda 29 Şubat'ta dolar. Hak, kıdeme göre bugünkü tablodan gelir (D2
  sürer). Ana sayfada Hak: Ayşe Yılmaz (giriş 2008-03-15) bugün 2009-03-14 → 0 · 2009-03-15 →
  14 · 2014-03-14 → 14 · 2014-03-15 → 20 · 2024-03-14 → 20 · 2024-03-15 → 26. Ahmet Çelik
  (giriş 2020-02-29): 2021-02-27 → 0 · 2021-02-28 → 14 · 2026-02-27 → 14 · 2026-02-28 → 20 ·
  artık yılda 2036-02-28 → 20 · 2036-02-29 → 26. Zeynep Kaya (giriş 2024-11-10): 2025-11-09 →
  0 · 2025-11-10 → 14.
- [ ] CB-2 — **İzin günü (BR-3).** Bir talebin izin günü, başlangıç ve bitiş dahil aralıktaki
  Pazartesi–Cuma günlerinin sayısıdır; aynı sayı talep listesinin Gün sütununda, ana sayfadaki
  Kullanılan'da ve yeni talep kontrolünde kullanılır (I-3). Cuma–Pazartesi talebi
  (2026-11-13 → 2026-11-16) 2 gün; yalnızca hafta sonu (2026-11-14 → 2026-11-15) 0 gün. Seed
  talep listesinin Gün sütunu sırasıyla: 10, 3, 1, 5, 3, 3, 10, 1. Ana sayfa seed ile: Ayse
  Yilmaz · IT · 26 · 10 · 16; diğer dört satır değişmez (Mehmet 20 · 0 · 20, Zeynep 14 · 0 · 14,
  Ahmet 20 · 0 · 20, Elif 0 · 0 · 0).
- [ ] CB-3 — **Yeni talep kontrolü.** Bakiye kontrolü CB-2'deki gün sayısıyla yapılır; eşitlik
  davranışı (D6) olduğu gibi kalır. Zeynep Kaya (Kalan 14): 15 gün (2026-12-01 → 2026-12-21) →
  yetersiz bakiye hata sayfası · 14 gün (2026-12-01 → 2026-12-18) → kayıt oluşmaz, hata
  gösterilmez (D6) · 13 gün (2026-12-01 → 2026-12-17) → kaydedilir · 2026-12-01 → 2026-12-15
  (15 takvim, 11 iş günü; bugün hata sayfası) → kaydedilir. Elif Şahin (Kalan 0): 1 gün
  (2026-11-16) → hata sayfası.

## Preserved behavior
Spec 0001'in sabitlediği ve bu işin değiştirmediği davranış; değerler 0001 testlerinde gözlendi.

- [ ] PB-1 — Ana sayfa sayaçları değişmez: Bekleyen 4, Onaylanan 1, Reddedilen 3.
- [ ] PB-2 — Bakiye modeli değişmez (spec 0003'e kadar): sütunlar Ad, Birim, Hak, Kullanilan,
  Kalan; Kalan = Hak − Kullanılan; bekleyen talepler düşülmez, yeni talep Kalan'ı değiştirmez
  (D5; Mehmet Demir 3 günlük talep sonrası Kalan 20); Kullanılan yıl ayrımı olmadan tüm onaylı
  talepleri, gelecektekiler dahil, sayar (D11; Ayşe bugün 2009-01-01 ve 2027-01-01 → 10);
  Kalan negatif olabilir (D14; Ayşe bugün 2008-12-31 → Hak 0, Kullanılan 10, Kalan −10).
- [ ] PB-3 — Talep listesi: kayıt sırası, sütunlar (Personel, Baslangic, Bitis, Gun, Neden,
  Durum), durum metni ve rengi (D13), neden metninin kaçışlanmadan yazılması (D9) ve herkese
  görünmesi (D12) değişmez. D9'un XSS düzeltmesi bu işten önce ship edilirse o düzeltmenin
  davranışı korunur.
- [ ] PB-4 — Yeni talep: beş personel seçeneği, alanlar ve etiketler; geçerli talep `Beklemede`
  olarak listenin sonuna eklenir, kullanıcı `/requests`'e yönlendirilir (HTTP 302); neden
  gönderilmezse boş kaydedilir; yetersiz bakiye hata metni aynen (D9); olmayan personel,
  geçersiz tarih ve eksik alan için kayıt oluşmaz, hata gösterilmez (D7); bitişi başlangıçtan
  önce olan ve yalnızca hafta sonunu kapsayan talep kaydedilir, Gün 0 (D7); geçmiş tarihli
  talep kabul edilir (D8).
- [ ] PB-5 — Adresler ve gezinme 0001/PB-15'teki gibidir.

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

## Definition of Done
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale
- [ ] Criterion ↔ evidence table complete for CB-* **and** PB-* (UI: before/after screenshots)
- [ ] Spec moved to `specs/done/` (immutable there)
