# LeaveManager (Python/Flask)

Şirket içi personel yıllık izin takip uygulaması. Proje kuralları: `AGENTS.md`.

## Kurulum (bir kez)

    python -m venv .venv
    .venv/Scripts/python -m pip install -r requirements-dev.txt     # Windows
    .venv/bin/python -m pip install -r requirements-dev.txt         # Linux/macOS

## Çalıştırma

    .venv/Scripts/python app.py      # Windows (Linux/macOS: .venv/bin/python app.py)

Adres: http://localhost:5000

## Doğrulama

    ./scripts/check          # tam profil — tek kanıt
    ./scripts/check --fast   # iç döngü
