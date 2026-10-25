# ADR 0001 — Katmanlı monolit: tek Flask uygulaması, dört katman

- Status: Accepted
- Date: 2026-10-25

## Context
LeaveManager 2015'ten kalma, tek dosyalık (`app.py`, ~200 satır) bir Flask uygulaması. Veri, iş
kuralları, HTML ve route'lar iç içe; "bugün" doğrudan `datetime.now()` ile okunuyor; veri
bellekte. Kodun sahibi yok, testi yok. Bootstrap'te kabul edilen iş kurallarının (BR-1…BR-9)
neredeyse hepsi tarihe bağlı; kalıcı veri ikinci öncelik; güvenlik açıkları (XSS, CSRF, debug)
ilk öncelik. Uygulama canlıda değil, ekip tek kişi.

## Decision
Uygulama tek bir Flask uygulaması olarak kalır ve içi dört katmana ayrılır: `domain` (saf iş
kuralları, "bugün" parametre), `services` (senaryo + rol kontrolü), `storage` (repository
arkasında kalıcılık), `web` (HTTP, Jinja şablonları). Çağrı yönü `web → services → domain`,
`services → storage`; yasaklar F1–F6 araçla denetlenir (`docs/architecture.md`).

## Consequences
- Kazanç: tarih kuralları sabit bir "bugün" ile test edilebilir; bellekten SQL'e geçiş yalnızca
  `storage`'ı değiştirir; HTML'in şablonlara taşınması XSS düzeltmesinin zeminini hazırlar;
  katman ihlali check'te kırmızıya döner.
- Maliyet: bugünkü tek dosya taşınmalı — karakterizasyon testleri + refactor spec'i gerekir.
  Küçük bir uygulama için birkaç dosya ve bir import-linter yapılandırması fazladan yapı demek.
- Geçiş sürecinde `app.py` kurallara uymaz; `pyproject.toml`'da geçici lint istisnası taşır.

## Alternatives considered
- **Tek dosya olarak bırakmak:** en az iş, ama "bugün" enjekte edilemediği için tarih kuralları
  güvenilir test edilemez ve SQL'e geçiş tüm dosyaya dokunur. Reddedildi.
- **Ayrı REST API + ön yüz (SPA):** JavaScript derleme zinciri, iki dağıtım, iki test
  katmanı getirir; kullanıcı sayısı ve ekip (tek kişi) bunu taşımaz. Reddedildi.
- **Özellik bazlı modüller (personel/, izin/):** iki küçük alt alan için katman ayrımından daha
  az şey kazandırır; asıl risk (tarih, kalıcılık, HTML) katmanlar arası. Reddedildi.

## Revisit triggers
- Başka bir sistemin (bordro, İK yazılımı) izin verisine programatik erişim istemesi → API katmanı.
- Ekranlarda JavaScript etkileşiminin gerekmesi → ön yüz ve e2e kararı yeniden açılır.
- Ekibin büyümesi ve modüllerin farklı kişilere dağılması → özellik bazlı modüller.
