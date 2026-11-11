# LeaveManager (Python/Flask)

Şirket içi personel yıllık izin takip uygulaması. Proje kuralları: `AGENTS.md`.

## Kurulum (bir kez)

    python -m venv .venv
    .venv/Scripts/python -m pip install -r requirements-dev.txt     # Windows
    .venv/bin/python -m pip install -r requirements-dev.txt         # Linux/macOS

## Çalıştırma

    .venv/Scripts/python app.py      # Windows (Linux/macOS: .venv/bin/python app.py)

Geliştirirken debug için `FLASK_DEBUG=1` ortam değişkenini verin; kodda debug açılmaz
(`docs/security.md`).

Adres: http://localhost:5000

## Doğrulama

    ./scripts/check          # tam profil — tek kanıt
    ./scripts/check --fast   # iç döngü
