# ADR 0002 — Kalıcı veri MongoDB'de; izin talepleri personel belgesinin içinde

- Status: Accepted
- Date: 2026-11-11

## Context
- Veri bugün bellekte (`InMemoryRepository`) ve her başlatmada seed'e döner. Yol haritasında
  sıradaki iş kalıcı veri. [ADR 0001](0001-katmanli-monolit.md) kalıcılığı `storage` katmanına,
  bir repository arayüzünün (`LeaveRepository`) arkasına koydu ve seçimi bir ADR'a bıraktı.
  0001 "bellekten SQL'e geçiş" diye yazdı; bu ADR o ifadeyi MongoDB olarak netleştirir. 0001'in
  kararı (katmanlar ve çağrı yönü) değişmez.
- Hedef: uygulama MongoDB üzerinde çalışacak (proje sahibinin kararı, 2026-11-11).
- Veri küçük ve ilişkisel biçimli: personel (seed'de 5, canlıda en fazla yüzler) ve personele
  bağlı izin talepleri. Bakiye (BR-4) her seferinde o personelin talepleri üzerinden hesaplanır.
- BR-5: `LeaveService.create_request` önce bakiyeyi okur, sonra yazar. Aynı personel için aynı
  anda gelen iki talep ikisi de kontrolü geçip Kalan'ı aşabilir. Bellekte bu yarış görünmüyordu;
  kalıcı ve aynı anda birden çok isteğe hizmet eden bir uygulamada gerçek olur. Model, bakiye
  kontrolüyle yazmayı atomik kılmalı.
- MongoDB'de çok belgeli transaction replica set ister ve snapshot izolasyonuyla çalışır: iki
  eşzamanlı transaction farklı belgelere talep eklerse çakışmaz. Yani transaction tek başına BR-5
  yarışını kapatmaz.
- Testler ağsız, ~0,6 s ve `scripts/check` içinde. Geliştirme makinesinde Docker da MongoDB de
  yok. ANEW-0007: check geride çalışan bir şey bırakmaz, bir koşunun yazdığı veri sonrakine
  ulaşmaz.
- Personel verisi kişisel veridir (KVKK). Üretim barındırması henüz belli değil. Ekip tek kişi,
  uygulama canlıda değil.

## Decision
Kalıcı veri MongoDB'de, resmî sürücü PyMongo ile tutulur. Her personel tek bir belgedir ve izin
taleplerini bir dizi olarak içerir; yeni talep, belgenin `version` alanına koşullu tek bir
güncellemeyle eklenir, böylece BR-5 bakiye kontrolü ile yazma atomik olur.

Bu kararın parçası olan ayrıntılar:
- Koleksiyonlar: `employees` (personel bilgisi, `requests` dizisi, `version`) ve `counters`
  (talep ID sayacı).
- ID'ler tamsayıdır: personelin `_id`'si bugünkü ID'sidir; talep ID'si `counters` üzerinden
  atomik `$inc` ile üretilir.
- Tarihler ISO 8601 takvim günü metnidir (`"2026-11-16"`): domain Europe/Istanbul takvim günüyle
  çalışır, BSON Date ise bir UTC anıdır.
- Talep ekleyen ya da değiştiren her yazma, personel belgesini okuduğu `version` ile koşullar ve
  `version`'ı artırır. Koşul tutmazsa (araya başka bir yazma girmişse) işlem yeniden okuyup dener
  ya da hata döner; hangisi olduğu kalıcı veri spec'inde belirlenir.
- Bağlantı yalnızca `MONGODB_URI` ortam değişkeniyle kurulur; kodda varsayılan yoktur
  (`docs/security.md`, Secrets). Replica set gerekmez, tek bir `mongod` yeter.
- ODM ve Flask eklentisi kullanılmaz: depo, belgeleri domain'in dataclass'larına kendisi çevirir.
  `pymongo` ve `bson` yalnızca `storage`'da kullanılır (F5).
- Kullanıcı girdisi sorguya yalnızca tipli değer (int, ISO tarih, str) olarak girer; istekten
  gelen bir sözlük asla sorguya verilmez (NoSQL operatör enjeksiyonu).
- Test: HTTP ve servis testleri `InMemoryRepository` ile ağsız olarak `scripts/check`'te kalır.
  Depo sözleşme testleri aynı davranışı hem bellekteki depoda hem gerçek MongoDB'de sınar. Mongo
  kısmı CI'da ayrı bir job'da, bir MongoDB service container'ına karşı koşar; yerelde
  `MONGODB_URI` verilirse istenince çalıştırılır. Her test kendi geçici veritabanını açar ve
  sonunda siler.
- Üretim barındırması (şirket içi ya da yönetilen bulut) canlıya geçişte kararlaştırılır. O
  kararda verinin hangi ülkede tutulduğu (KVKK) açıkça yazılır.

## Consequences
Kazanç:
- BR-5 yarışı veritabanı düzeyinde kapanır; transaction, replica set ya da kilit gerekmez. Tek bir
  `mongod` yettiği için geliştirme ve CI kurulumu hafif kalır.
- Bir personelin bakiyesi tek belge okumasıyla hesaplanır: hesabın birimi (personel) belgenin
  birimiyle aynıdır.
- Tamsayı ID'ler ve ISO tarihler sayesinde formlar, URL'ler, seed ve mevcut testler değişmez;
  değişiklik yalnızca `storage` ve `app.py`'de kalır (ADR 0001'in vaadi).
- PyMongo resmî sürücüdür ve aktif bakılıyor (4.19.0, 2026-10-14, Apache-2.0); bağımlılık
  kontrol listesini (`docs/security.md`, Dependencies) geçer.
- Hızlı, ağsız test döngüsü korunur; Mongo davranışı yine de her push ve PR'da gerçek sunucuda
  sınanır.

Maliyet:
- Veri ilişkisel biçimli ama foreign key, şema ve tekillik kısıtlarını veritabanı değil kod
  korur (domain doğrulaması; istenirse koleksiyona JSON Schema doğrulayıcısı eklenir).
- Tüm talepleri listelemek (`/requests`, sayaçlar, ileride onay ekranı) `$unwind` aggregation
  ister. Bir talebi ID'siyle bulmak personel belgelerinin içinde aramak demektir; dizi alanına
  index gerekir.
- Talep ID'si ayrı bir sayaçtan gelir; sayaç arttıktan sonra ekleme başarısız olursa ID dizisinde
  boşluk kalır.
- `version` çakışmasında ne yapılacağı (yeniden deneme ya da hata) depo ve servis sözleşmesine
  girer ve test edilmesi gereken yeni bir yoldur.
- "Bütün test paketi `scripts/check`'te" sözleşmesinin bilinçli bir istisnası doğar: Mongo
  sözleşme testleri yerel check'te değil, CI job'ında koşar (`audit` job'ı emsal). Mongo'ya özgü
  bir hata yerelde değil, CI'da görünebilir.
- Uygulamayı yerelde çalıştırmak için bir MongoDB gerekir (Windows'a Community Server ya da
  erişilebilir bir sunucu); bugün `python app.py` tek başına çalışıyor.
- İşletme yükü: yedekleme (`mongodump` ya da yönetilen hizmet), kimlik doğrulama, TLS ve sürüm
  güncellemesi.
- Yeni bağımlılıklar: `pymongo` ve onun bağımlılığı `dnspython` (son sürümü 2.9.2,
  2026-11-03); hangi sürümlerin sabitleneceği plan kararıdır.
- MongoDB sunucusunun lisansı (Community Server, SSPL) izin verici değil. Kontrol listemiz Python
  bağımlılıkları içindir; sunucu ayrı bir hizmet olarak kullanılır. SSPL'in yükümlülüğü
  MongoDB'nin kendisini başkalarına hizmet olarak sunmakla ilgilidir, şirket içi kullanımı
  etkilemez.
- `docs/architecture.md`'deki "SQL" ifadeleri ve F5 kuralının sürücü listesi (`sqlite3`) bu
  kararla eskir. ADR 0001 kabul edilmiş olduğu için değişmez; `docs/architecture.md` ve F5'in
  import-linter ayarı kalıcı veri spec'inde birlikte güncellenir.

## Alternatives considered
- **MongoDB, ayrı `leave_requests` koleksiyonu ve çok belgeli transaction:** listeler ve talebi
  ID'siyle bulmak daha basit, SQL'e en yakın şekil. Ama transaction replica set ister (geliştirme
  ve CI kurulumu ağırlaşır) ve snapshot izolasyonu iki eşzamanlı eklemeyi çakıştırmaz; BR-5 için
  personel belgesine ayrıca bir "kilit" yazımı gerekir. Aynı atomikliği daha çok parçayla verir.
  Reddedildi.
- **PostgreSQL:** bu veri şekline en doğal uyan seçenek; foreign key, kısıtlar ve
  `SELECT … FOR UPDATE` ile BR-5 hazır çözülür, raporlama SQL ile kolaydır. Hedef MongoDB olduğu
  için seçilmedi; hedef değişirse ilk aday.
- **SQLite (standart kütüphane):** sunucusuz, yeni bağımlılık yok, testler bir dosya üzerinde
  koşar. Tek dosya ve tek sunucu sınırı, eşzamanlı yazma ve yedekleme kısıtları var; hedefle de
  uyuşmuyor. Reddedildi.
- **ODM (MongoEngine vb.) ya da Flask-PyMongo:** ODM'in model katmanı domain'in dataclass'larını
  kopyalar; Flask eklentisi depoyu Flask'e bağlar ve katman sınırını bulanıklaştırır. Küçük bir
  depo için PyMongo ile elle eşleme daha az parça. Reddedildi.
- **mongomock ile check içinde test:** sunucu gerekmez, tek komut korunur. Son sürümü 2024-11-16
  tarihli, yani "son 12 ayda sürüm" bakım kontrolünü geçmiyor. Ayrıca MongoDB'nin yeniden
  yazılmış bir taklidi olduğu için orada geçen test gerçek MongoDB'yi kanıtlamaz. Reddedildi.
- **Her check'te geçici bir MongoDB (container):** tek komut ile gerçek sunucuyu birleştirir. Ama
  her geliştirici makinesinde Docker gerektirir (bugün yok), check'i yavaşlatır ve ANEW-0007
  açısından kalıntı riski taşır. Reddedildi.

## Revisit triggers
- Birden çok personeli aynı anda atomik olarak değiştiren bir kural (ekip kotası, izin devri) →
  transaction (replica set) ya da ilişkisel veritabanı.
- Ağır raporlama ya da bordro/İK sistemiyle SQL tabanlı entegrasyon ihtiyacı.
- Personel başına talep sayısının çok büyümesi (ör. saatlik izin kaydı) → talepler ayrı
  koleksiyona taşınır.
- Şirketin MongoDB hedefinden vazgeçmesi ya da üretimde MongoDB sağlanamaması → PostgreSQL ilk
  aday.
- `version` çakışmalarının pratikte sık görülmesi → yazma modeli yeniden değerlendirilir.
- Gerçek MongoDB'ye sadık, bakımlı bir yerel test aracının ya da geliştirici makinelerinde
  Docker'ın bulunması → Mongo sözleşme testleri `scripts/check`'e alınır.
