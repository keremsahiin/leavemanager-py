"""LeaveManager başlatıcısı: katmanları birleştirir (docs/architecture.md)."""

from leavemanager.services import LeaveService
from leavemanager.storage import InMemoryRepository
from leavemanager.web import create_app

app = create_app(LeaveService(InMemoryRepository()))

if __name__ == "__main__":
    app.run(port=5000)  # debug yalnızca FLASK_DEBUG=1 ile (docs/security.md)
