# Architecture

## System overview
LeaveManager, şirket içinde kullanılan bir personel yıllık izin takip uygulamasıdır: İK, yöneticiler
ve çalışanlar izin hakkını, kullanılan ve kalan günleri görür; çalışan talep girer, yönetici onaylar.
Mimari: **tek bir Flask uygulaması, içeride dört katman** (`domain` / `services` / `storage` /
`web`) — katmanlı monolit. Gerekçe: iş kuralları tarihe bağlı ve test edilebilir olmalı, kalıcılık
bellekten SQL'e geçecek; ~200 satırlık bir uygulama için ayrı servisler gereksiz yük
([ADR 0001](decisions/0001-katmanli-monolit.md)).

**Geçiş durumu:** Kod henüz bu yapıda değil — her şey tek dosyada (`app.py`, 2015). Taşıma ayrı bir
refactor spec'iyle yapılır: önce karakterizasyon testleri, sonra taşıma (`workflows/refactor.md`).
Bu spec `leavemanager/` paketini, `clock.py`'yi ve `create_app()`'i oluşturur, `lint-imports`
adımını check'e ekler ve `pyproject.toml`'daki geçici `app.py` istisnasını kaldırır.
O spec'e kadar `app.py` aşağıdaki kurallara uymaz; yeni kod uyar.

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| `leavemanager/domain` | İş kurallarını hesaplamak (BR-1…BR-8). Flask, veritabanı ve sistem saatini bilmez; "bugün" parametre olarak gelir. | Kıdem, hak tablosu, izin günü hesabı, bakiye, durum geçişleri, `DomainError` hataları |
| `leavemanager/services` | Kullanım senaryosunu yürütmek: oku → kuralı uygula → yaz. Rol kontrolü (kim neyi yapabilir) burada. | İşlem sırası, yetki kararı, senaryonun hata sonucu |
| `leavemanager/storage` | Kalıcılık, bir repository arayüzü arkasında. Şimdi bellekte, sonra SQL (seçim ADR ile). | Personel ve talep kayıtları, ID üretimi |
| `leavemanager/web` | HTTP ve HTML: formu oku, servisi çağır, Jinja şablonuyla göster, `DomainError`'u kullanıcı mesajına çevir. | Blueprint'ler, şablonlar, kullanıcıya görünen metin ve etiketler |
| `leavemanager/clock.py` | "Bugün"ün tek kaynağı (Europe/Istanbul takvim günü). | Sistem saatine erişim |
| `app.py` | Yalnızca başlatıcı: `create_app()` + çalıştırma. | — |

## Communication rules
- Yalnızca doğrudan fonksiyon çağrısı; event, mesaj kuyruğu veya arka plan işi yok.
- Çağrı yönü tek: `web → services → domain` ve `services → storage`. `storage`, `domain`
  tiplerini (dataclass'lar) kullanabilir. Geriye doğru çağrı yok.
- `web`, `domain`'den yalnızca tip/enum alır (ör. `LeaveStatus`); hesaplama yapmaz.
- Servisler "bugün"ü `clock`'tan alıp domain'e parametre olarak verir; testlerde sabit bir saat
  enjekte edilir.

## Forbidden dependencies (make them testable)
Denetim `pyproject.toml`'da: F1–F5 import-linter kuralları, F6 ruff `TID251`. import-linter adımı
`scripts/check.conf`'a paketi oluşturan refactor spec'iyle eklenir.

- **F1** `domain` hiçbir katmanı (`services`, `storage`, `web`) ve `clock`'u import etmez; `flask`,
  `werkzeug`, `jinja2` ve veritabanı sürücülerini kullanmaz.
- **F2** `services`, `web`'i ve `flask`/`werkzeug`/`jinja2`'yi import etmez (doğrudan veya dolaylı).
- **F3** `web`, `storage`'ı doğrudan import etmez — veriye yalnızca servis üzerinden ulaşır.
- **F4** `storage`, `services` ve `web`'i import etmez.
- **F5** Veritabanı sürücüsü / ORM yalnızca `storage`'da. Liste şimdilik `sqlite3`; veritabanı
  ADR'ı seçilen sürücüyü bu kurala ekler.
- **F6** `datetime.now()`, `datetime.today()`, `datetime.utcnow()` ve `date.today()` yalnızca
  `leavemanager/clock.py`'de çağrılır. Geçici istisna: eski `app.py` (refactor kaldırır).
- Dış bağımlılık: uygulama yalnızca `flask` ile çalışır; onaylı ama henüz eklenmemiş: Flask-WTF
  (CSRF), `tzdata` (Windows'ta saat dilimi). Node.js/JavaScript derleme zinciri ve CDN script yok.

## Deliberately out of scope
- REST API veya tek sayfalık ön yüz (SPA); sayfalar sunucuda üretilen HTML.
- Mikroservis, birden fazla şirket (multi-tenant), e-posta/bildirim, raporlama ve dışa aktarım.
- Veritabanı seçimi: kalıcı veri özelliği başladığında ADR ile.
