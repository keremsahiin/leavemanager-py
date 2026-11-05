# Domain

Kapsam: yalnızca **yıllık ücretli izin**. Kanun atıfları (4857 sayılı İş Kanunu) bootstrap
görüşmesinde kabul edildi; **İK / hukuk teyidi henüz yapılmadı** (bkz. Open decisions).

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Personel (`employee`) | İzin hakkı olan çalışan kaydı: ad, birim, işe giriş tarihi. | "Çalışan" rolüyle karıştırma: rol, sisteme giren kişinin yetkisidir. |
| Birim (`department`) | Personelin bağlı olduğu birim (IT, Muhasebe, IK, Satis). | |
| İşe giriş tarihi (`hire_date`) | Kıdemin başladığı gün. | |
| Kıdem (seniority) | İşe girişten bugüne **tamamlanmış** tam hizmet yılı (BR-2). | Takvim yılı farkı değildir. |
| Yıllık izin hakkı (entitlement) | Bir hizmet yılı için kazanılan izin günü (BR-1). | Bakiye değildir. |
| İzin talebi (`request`) | Bir tarih aralığı için izin isteği; başlangıç ve bitiş **dahil**. | Onaylanana kadar "izin" değildir. |
| Talep durumu (`LeaveStatus`) | `pending` (Beklemede), `approved` (Onaylandı), `rejected` (Reddedildi). | Kayıtta İngilizce kod, ekranda Türkçe etiket (`docs/conventions.md`). |
| İzin günü | Bir talepte bakiyeden düşülen gün sayısı (BR-3). | Takvim günü değildir. |
| Kullanılan izin (used) | Onaylanmış taleplerdeki izin günlerinin toplamı. | Ana sayfada bu izin yılından itibaren başlayanlar; öncekiler Devir'den düşülür. |
| İzin yılı (leave year) | Son yıldönümünde başlayan bir yıllık dönem; kıdem 0 iken işe giriş gününde başlar. | Takvim yılı değildir. |
| Devir (carried over) | Önceki izin yıllarından kullanılmadan kalan gün (BR-4). | Yanmaz, tavanı yoktur. |
| Kalan izin / bakiye (remaining) | BR-4'e göre hesaplanan, talep edilebilir gün. | |
| Neden (`reason`) | Talebe eklenen isteğe bağlı serbest metin not (BR-9). | Kişisel veri; sağlık bilgisi yazılmaz. |
| Çalışan (rol) | Kendi taleplerini girer ve görür. | |
| Yönetici (rol) | Talepleri onaylar veya reddeder. | Hangi personelin yöneticisi olduğu: açık karar. |
| İK (rol) | Tüm personel ve talepleri görür ve yönetir; geçmiş tarihli talep girebilir. | |

## Business rules
Her kuralın yanında bugünkü kodun durumu var. "Sapıyor" = kayıtlı bir bilinen sapma (aşağıdaki
tablo); uygulama canlıda olmadığı için her sapma bir **bug**'dır (`/fix-bug`), kural belirsizliği
değil. Belge–kod çelişkisi yalnızca bu listede olmayan bir sapma için ramp gerektirir (R-10,
`prompts/recovery/ambiguity.md`).

- **BR-1 — Yıllık izin hakkı.** Kıdem 1 yıldan az: 0 gün · 1–5 yıl (5 dahil): 14 gün · 6–14 yıl:
  20 gün · 15 yıl ve üzeri: 26 gün (İş K. md. 53). — Kod: **uyuyor**.
- **BR-2 — Kıdem.** İşe giriş yıldönümünde tamamlanan tam yıl sayılır. 29 Şubat'ta işe girenin
  yılı, artık olmayan yıllarda 28 Şubat'ta dolar. — Kod: **uyuyor** (spec 0002).
- **BR-3 — İzin günü.** Başlangıç ve bitiş dahil aralıktaki Pazartesi–Cuma günleri sayılır;
  hafta sonu, ulusal bayram ve genel tatil günleri sayılmaz (md. 56). Cumartesi iş günü değildir.
  — Kod: hafta sonu kısmı **uyuyor** (spec 0002); resmî tatil kısmı **sapıyor** (D15). Takvimin
  kaynağı açık karar.
- **BR-4 — Bakiye.** Bakiye = kazanılmış hakların toplamı − onaylanan izin günleri − bekleyen
  izin günleri. Her tamamlanan hizmet yılının yıldönümünde o yılın BR-1 hakkı eklenir.
  Kullanılmayan izin yanmaz, devir tavanı yoktur (md. 53: hakkından vazgeçilemez). Reddedilen
  talep bakiyeyi etkilemez. — Kod: **uyuyor** (spec 0003).
- **BR-5 — Bakiye kontrolü.** Talebin izin günü kalan bakiyeye eşit veya azsa talep kabul edilir.
  Kontrol yalnızca servis katmanında yapılır. — Kod: **uyuyor**.
- **BR-6 — Geçerlilik.** Bitiş başlangıçtan önce olamaz; izin günü en az 1 olmalı; personel
  mevcut olmalı. İhlalde kayıt oluşmaz, kullanıcıya hata gösterilir. — Kod: **uyuyor**.
- **BR-7 — Geçmiş tarih.** Başlangıcı bugünden önce olan talebi yalnızca İK girebilir.
  — Kod: **sapıyor** (D8; rol yok, herkese açık).
- **BR-8 — Durum geçişi.** Yalnızca Yönetici veya İK, `pending` bir talebi `approved` ya da
  `rejected` yapabilir. Bu iki sonuç kesindir. — Kod: **yok** (onay ekranı yok). İptal: açık karar.
- **BR-9 — Neden alanı (KVKK).** İsteğe bağlıdır; formda "sağlık bilgisi yazmayın" uyarısı
  bulunur; yalnızca Yönetici ve İK görür; log'a yazılmaz. — Kod: **sapıyor** (D12).

## Key domain invariants
- **I-1** Hiçbir işlem bakiyeyi negatife düşüremez.
- **I-2** `approved` veya `rejected` durumundaki bir talep değiştirilemez.
- **I-3** İzin günü tek bir fonksiyonda hesaplanır; her ekran aynı sayıyı gösterir.

## Known deviations
Bootstrap incelemesinde (2026-10-25) bulunan, koddaki bilinen sapmalar. Kapanan sapma, onu
düzelten işin spec'ine / raporuna referansla buradan silinir.
Kapananlar: **D3, D4** — spec 0002 (kıdem yıldönümü ve iş günü sayımı) · **D5, D10, D11** —
spec 0003 (bekleyen düşümü, izin yılı ve devir) · **D9'un stored XSS kısmı** — `fix/D9-reason-xss` · **D2** —
`fix/D2-entitlement-15-years` · **D6, D7** — `fix/D6-D7-request-validation` · **D1** — spec 0004
(yorum kalktı) · **D9'un `body\|safe` kısmı** — spec 0004 (HTML şablon dosyalarından;
`test_security_stored_html_is_escaped_on_output`).

| # | Yer | Gözlem | Kural |
|---|---|---|---|
| D8 | `LeaveService.create_request` | Geçmiş tarihli talep herkese açık. | BR-7 |
| D9 | genel | Güvenlik açıkları: kimlik doğrulama yok, CSRF yok, `debug=True` (`app.py`), hata mesajında dahili kod ve telefon (`leavemanager/web/pages.py`; yetersiz bakiye sayfası ayrıca HTTP 200 döner: düzeltme onu da 4xx yapmalı). Beklenmeyen hatada Flask'in İngilizce 500 sayfası çıkar, `debug=True` ile traceback de görünür: `debug=True` kalkarken Türkçe 500 sayfası eklenmeli (`docs/conventions.md`). Ayrıntı: `docs/security.md`. | — |
| D12 | `/requests`, `/new` | Neden alanı herkese görünüyor, uyarı yok. | BR-9 |
| D13 | `leavemanager/domain/models.py`, `leavemanager/storage/memory.py` (seed), `LeaveService`, `leavemanager/web/pages.py` | Durum kayıtta Türkçe metin (`"Onaylandi"` …). Kural: kayıtta `pending`/`approved`/`rejected`, `LeaveStatus` enum'u. | `docs/conventions.md` Naming |
| D14 | `leave_balance` (`leavemanager/domain/leave_rules.py`) | Kalan = Devir + Hak − Kullanılan − Bekleyen, alt sınır yok: Kalan negatife düşebiliyor (ör. kıdem 0 iken onaylı talep varsa). Spec 0001 / plan 0001 R6'da bulundu. | I-1 |
| D15 | `working_days` (`leavemanager/domain/leave_rules.py`) | Hafta içine denk gelen resmî tatil ve bayram günleri izin günü sayılıyor (ör. 2026-10-29 Perşembe, Cumhuriyet Bayramı: 1 gün). Seed'de Ayşe'nin 2026-07-06 → 2026-07-17 talebi 15 Temmuz Çarşamba'yı kapsıyor ve 10 gün sayılıyor (tatil listesi İK teyidi ister). Gün sayısı BR-5 ve BR-6'yı da etkiler: yalnızca tatile denk gelen talep bugün 1 gün sayılıp kabul ediliyor, düzeltme bunu da test etmeli. Takvimin kaynağı açık karar. Spec 0002 review'unda (R1-2) bulundu. | BR-3 |

## Open decisions
- Kanun atıflarının (BR-1, BR-3, BR-4) İK / hukuk tarafından teyidi.
- Yöneticinin hangi personelin taleplerini onaylayacağı (birim bazlı mı?).
- Talep iptali (kim, hangi durumdayken).
- Resmî tatil takviminin kaynağı (BR-3).
- Gerçek açılış bakiyeleri: geçmiş yılların kullanım verisi yok. Spec 0003 kararı: hesap işe
  girişten başlar, açılış devri 0; bu yüzden devirler gerçeğinden büyük çıkar. Canlıya geçmeden
  önce İK'nın gerçek devirleri yüklenmeli (ayrı iş).

## Out of scope (şimdilik)
- Yaşa bağlı kural (18 yaş ve altı, 50 yaş ve üstü en az 20 gün) — doğum tarihi verisi yok.
- Mazeret, ücretsiz izin, rapor gibi diğer izin türleri.
- İznin bölünmesi (bir parçası en az 10 gün, en fazla üç parça).
