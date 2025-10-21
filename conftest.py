"""
🧪 333HOME - Tests Configuration

Fixtures et configuration globale pour pytest
"""

import pytest
import sys
from pathlib import Path
from typing import Generator

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Retourne le chemin racine du projet"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def data_dir(project_root_path: Path) -> Path:
    """Retourne le répertoire data"""
    return project_root_path / "data"


@pytest.fixture(scope="session")
def test_data_dir(project_root_path: Path) -> Path:
    """Répertoire pour données de test"""
    test_dir = project_root_path / "tests" / "test_data"
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


@pytest.fixture
def mock_scan_result():
    """Mock ScanResult pour tests"""
    from datetime import datetime
    return {
        "scan_id": "scan_test_123",
        "timestamp": datetime.now().isoformat(),
        "subnet": "192.168.1.0/24",
        "scan_type": "ping",
        "devices_found": 3,
        "new_devices": 1,
        "duration_seconds": 5.2,
        "devices": [
            {
                "mac": "AA:BB:CC:DD:EE:FF",
                "current_ip": "192.168.1.100",
                "current_hostname": "test-device",
                "vendor": "Apple",
                "device_type": "computer",
                "currently_online": True
            }
        ]
    }


@pytest.fixture
def mock_device_data():
    """Mock DeviceData pour tests"""
    return {
        "mac": "AA:BB:CC:DD:EE:FF",
        "current_ip": "192.168.1.100",
        "current_hostname": "test-laptop",
        "vendor": "Apple Inc.",
        "device_type": "computer",
        "os_guess": "macOS",
        "currently_online": True,
        "open_ports": [22, 80, 443],
        "services": []
    }


@pytest.fixture
def sample_devices_list():
    """Liste de devices pour tests"""
    return [
        {
            "mac": "AA:BB:CC:DD:EE:01",
            "current_ip": "192.168.1.10",
            "current_hostname": "device-1",
            "vendor": "Apple",
            "currently_online": True
        },
        {
            "mac": "AA:BB:CC:DD:EE:02",
            "current_ip": "192.168.1.20",
            "current_hostname": "device-2",
            "vendor": "Samsung",
            "currently_online": False
        },
        {
            "mac": "AA:BB:CC:DD:EE:03",
            "current_ip": "192.168.1.30",
            "current_hostname": "device-3",
            "vendor": "Cisco",
            "currently_online": True
        }
    ]
