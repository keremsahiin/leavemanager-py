# Security

Her plan ve review bu tabana uyar. Bugünkü koddaki açıklar bilinen sapma **D9** ve **D12**
(`docs/domain.md`); öncelik sırası: önce D9.

## Deployment posture
- Uygulama **yalnızca şirket iç ağından / VPN'den** erişilir; internete doğrudan açılmaz.
  İç ağda da kimlik doğrulama zorunludur — "iç ağ" bir yetki değildir.
- Kişisel veri işlenir (ad, birim, işe giriş tarihi, izin tarihleri, neden notu): KVKK geçerlidir.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- `SECRET_KEY` ve SSO istemci bilgileri ortam değişkeninden okunur; kodda varsayılan değer yoktur.
  `.env.example`, bu değişkenleri ilk okuyan iş (D9 düzeltmesi) tarafından eklenir.

## Input & output
- HTML yalnızca **Jinja şablon dosyalarından**, otomatik kaçışlama (autoescape) açıkken üretilir.
  `render_template_string`, string birleştirerek HTML üretmek ve kullanıcı verisiyle `|safe` /
  `Markup` **yasak** (stored XSS).
- Her POST formunda CSRF koruması: **Flask-WTF `CSRFProtect`** (onaylı; D9 düzeltmesi ekler).
- Girdi doğrulaması sınırda (`web`) tip dönüşümüyle, iş kuralı doğrulaması `domain`'de yapılır;
  geçersiz girdi kullanıcıya anlaşılır hata olarak döner (`docs/conventions.md`, Error handling).
- Kullanıcıya traceback, dahili hata kodu, sunucu/kişi bilgisi gösterilmez.
- `debug=True` kodda **yasak** (Werkzeug debugger = uzaktan kod çalıştırma; ruff `S201`).
  Debug yalnızca yerelde `FLASK_DEBUG=1` ortam değişkeniyle açılır.
- Log'a kişisel veri ve neden metni yazılmaz; log'larda yalnızca kayıt ID'leri bulunur.

## AuthN / AuthZ
- Kimlik doğrulama: **şirket hesabıyla SSO** (Active Directory / Microsoft Entra ID). Uygulama
  şifre saklamaz. Yöntem (OIDC mi LDAP mı) giriş özelliği geldiğinde ADR ile seçilir.
- Roller: Çalışan, Yönetici, İK (`docs/domain.md`). Rol kontrolü **servis katmanında** yapılır;
  route'taki gizleme yetki sayılmaz.
- **Varsayılan red:** açıkça izin verilmeyen her işlem reddedilir. Kimliği doğrulanmamış istek
  hiçbir sayfayı göremez.
- Neden alanını (BR-9) yalnızca Yönetici ve İK görür.

## Dependencies
- Yeni bir uygulama bağımlılığı, gerekçesiyle **plana** yazılır ve **plan onayıyla** kabul edilir.
- Kontrol listesi: izin verici lisans (MIT, BSD, Apache, PSF); aktif bakım (son 12 ayda sürüm);
  standart kütüphanede karşılığı yok.
- Bilinen açıklar (CVE): CI'da ayrı `audit` job'ı, `pip-audit -r requirements.txt`. Ağ
  gerektirdiği için `scripts/check`'e girmez.
- Onaylı ama henüz eklenmemiş: Flask-WTF (CSRF).

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
