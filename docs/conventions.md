# Conventions

Buradaki her kural ya araçla denetlenir (tercih edilen) ya da review'da kontrol edilir.
Eski `app.py` bu kurallara uymaz; bu kayıtlı ve beklenen bir durumdur, katmanlı pakete taşıyan
refactor spec'iyle kapanır (`docs/architecture.md`, Geçiş durumu). Yeni kod uyar.

## Language
<!-- Set at bootstrap (step 0) and mirrored in AGENTS.md. Changing it later is allowed — edit both
     places; existing documents are not translated retroactively. -->
- Chat language (interviews, sessions): Turkish (`tr`)
- Document language (docs/, specs, plans, ADRs, review and verify reports): Turkish (`tr`)
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: tanımlayıcılar ve branch adları İngilizce
  (branch adları ASCII); commit mesajında tip ve kapsam İngilizce, açıklama Türkçe
  (`docs/git.md`). Kod yorumları ve kullanıcıya görünen metin Türkçe, Türkçe karakterlerle (UTF-8).
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python **3.14** (yerelde `python` 3.14.x; CI `actions/setup-python` 3.14). Flask **3.1.x**.
- Bağımlılıklar `requirements.txt` (uygulama) ve `requirements-dev.txt` (araçlar) dosyalarında,
  doğrudan bağımlılıklar `==` ile sabit. Araç ayarları `pyproject.toml`'da; proje paket olarak
  kurulmaz.
- Ortam: proje kökünde `.venv` (git'e girmez). Python araçları `scripts/py` ile çağrılır.

## Naming
- Python: modül, fonksiyon ve değişkenler `snake_case`; sınıflar `PascalCase`; sabitler
  `UPPER_CASE`; tanımlayıcılar İngilizce. Domain terimlerinin Türkçe karşılıkları
  `docs/domain.md` tablosunda.
- Talep durumu: `LeaveStatus` (`StrEnum`) — kayıtta `pending` / `approved` / `rejected`. Türkçe
  etiketler (Beklemede / Onaylandı / Reddedildi) yalnızca `web` katmanında. Durumu string
  literal ile karşılaştırmak yasak.
- Testler: `tests/` altında `test_<konu>.py`; bir iş kuralını test eden fonksiyonun adı kural
  numarasıyla başlar: `test_br5_exact_balance_is_accepted`.
- Branch ve commit: `docs/git.md`.

## Error handling
- `domain` ve `services` hata durumunda `DomainError`'dan türeyen belirli bir hata fırlatır:
  `InsufficientBalance`, `InvalidDateRange`, `EmployeeNotFound`, `InvalidTransition`,
  `NotAllowed` (gerektikçe yenisi).
- `web` tek bir yerde `DomainError`'u yakalar; kullanıcıya Türkçe, anlaşılır mesaj ve uygun 4xx
  kodu döner. Hata → mesaj eşlemesi `web`'dedir.
- Beklenmeyen hata: traceback `logging` ile kaydedilir; kullanıcı yalnızca "Beklenmeyen bir hata
  oluştu" mesajını ve 500 kodunu görür.
- **Yasak:** `except Exception:` ile hatayı yutmak veya yutup "başarılı" dönmek; kullanıcıya
  traceback, dahili hata kodu, dahili telefon vb. göstermek; `print` ile log yazmak; log'a kişisel
  veri yazmak (log'larda yalnızca ID'ler — `docs/security.md`).

## Data rules
- Tarih alanları `datetime.date`. Aralıklar iki ucu da **dahil** hesaplanır.
- "Bugün" Europe/Istanbul saatine göre takvim günüdür ve yalnızca `leavemanager/clock.py`'den gelir
  (`zoneinfo`; Windows için `tzdata` paketi — onaylı, onu kullanan iş ekler). Domain "bugün"ü
  parametre olarak alır.
- Zaman damgası gerekirse saat dilimi bilgili (aware) UTC `datetime`.
- Gün sayıları her zaman `int`; `float` kullanılmaz.
- Kayıtlar `@dataclass(frozen=True)`; sözlükle kayıt taşınmaz. Kayıt ID'lerini yalnızca `storage`
  üretir.
- Formdan gelen tarih `date.fromisoformat()` ile okunur; geçersiz girdi `DomainError` /
  kullanıcı mesajına dönüşür, sessizce yok sayılmaz.

## Enforced by tooling
`./scripts/check` içinde (`scripts/check.conf`), ayarlar `pyproject.toml`'da:
- **ruff check** — `E`, `W`, `F` (temel hatalar), `I` (import sırası), `B` (olası buglar), `UP`
  (güncel sözdizimi), `S` (güvenlik, ör. `debug=True` → S201), `TID251` (F6: "bugün" yalnızca
  `clock.py`). Satır uzunluğu 100.
- **ruff format --check** — biçim tartışması review'da yapılmaz; formatlayıcı karar verir.
  Yalnızca `*.py` / `*.pyi` dosyalarına bakılır.
- **lint-imports** (import-linter) — katman kuralları F1–F5 (`docs/architecture.md`); check adımı
  refactor spec'iyle eklenir, kurallar şimdiden `pyproject.toml`'da.
- **GEÇİCİ istisna:** eski `app.py` yalnızca `E`/`W`/`F` kurallarına tabidir ve formatlanmaz.
  Katmanlı pakete taşıyan refactor spec'i istisnayı `pyproject.toml`'dan kaldırır.
- Review'da kontrol edilenler (henüz araç yok): Naming'deki domain/etiket ayrımı, Error handling
  yasakları, log'da kişisel veri.
