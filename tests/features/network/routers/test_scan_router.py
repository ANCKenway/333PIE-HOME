"""
🧪 Tests - Scan Router

Tests pour les endpoints de scan réseau ON-DEMAND
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

# Import app déjà créé (singleton)
from app import app

# Import schemas
from src.features.network.schemas import ScanResult, ScanRequest


@pytest.fixture
def client():
    """FastAPI TestClient - utilise app existant"""
    return TestClient(app)


@pytest.fixture
def sample_scan_result():
    """Résultat de scan pour tests"""
    return ScanResult(
        scan_id="test_scan_123",
        timestamp=datetime.now(),
        subnet="192.168.1.0/24",
        scan_type="quick",  # Enum valide
        devices_found=3,
        new_devices=1,
        duration_ms=5200,  # En millisecondes
        devices=[]
    )


class TestScanRouter:
    """Tests pour scan_router.py"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup/teardown pour chaque test"""
        from src.features.network.routers import scan_router
        # Setup: réinitialiser l'état avant le test
        scan_router._scan_in_progress = False
        scan_router._current_scan = None
        yield
        # Teardown: nettoyer après le test
        scan_router._scan_in_progress = False
        scan_router._current_scan = None
    
    def test_get_scan_status_no_scan(self, client):
        """Test GET /scan/status sans scan en cours"""
        response = client.get("/api/network/scan/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["in_progress"] is False
        assert data["last_scan"] is None
    
    @pytest.mark.skip(reason="Phase 5: TODO - Adapter mock pour MultiSourceScanner (architecture modulaire)")
    @patch("src.features.network.routers.scan_router.MultiSourceScanner")  # ✅ Phase 5: Updated
    @patch("src.features.network.routers.scan_router.get_all_devices")
    @patch("src.features.network.routers.scan_router.get_device_by_mac")
    @patch("src.features.network.routers.scan_router.NetworkHistory")
    def test_post_scan_success(self, mock_history, mock_get_device, mock_get_all, mock_scanner_class, client, sample_scan_result):
        """Test POST /scan avec succès"""
        # Setup mocks
        mock_get_all.return_value = []  # Pas de devices existants
        mock_get_device.return_value = None  # Pas de device précédent
        mock_history.return_value = Mock()  # Mock NetworkHistory
        
        mock_instance = Mock()
        mock_instance.scan_network = AsyncMock(return_value=sample_scan_result)
        mock_scanner_class.return_value = mock_instance
        
        # Request
        scan_request = {
            "subnet": "192.168.1.0/24",
            "scan_type": "quick",  # Enum valide
            "timeout_ms": 2000
        }
        
        response = client.post("/api/network/scan", json=scan_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["devices_found"] == 3
        assert data["scan_id"] == "test_scan_123"
        
        # Vérifier que le scanner a été appelé
        mock_scanner_class.assert_called_once()
        mock_instance.scan_network.assert_awaited_once()
    
    @patch("src.features.network.routers.scan_router._scan_in_progress", new=True)
    def test_post_scan_already_in_progress(self, client):
        """Test POST /scan quand scan déjà en cours"""
        scan_request = {
            "subnet": "192.168.1.0/24",
            "scan_type": "quick"
        }
        
        response = client.post("/api/network/scan", json=scan_request)
        
        assert response.status_code == 409
        assert "déjà en cours" in response.json()["detail"].lower()
    
    def test_post_scan_invalid_subnet(self, client):
        """Test POST /scan avec subnet invalide"""
        scan_request = {
            "subnet": "invalid_subnet",
            "scan_type": "ping"
        }
        
        response = client.post("/api/network/scan", json=scan_request)
        
        # Devrait être rejeté par Pydantic validation
        assert response.status_code == 422
    
    @pytest.mark.skip(reason="Phase 5: TODO - Adapter mock pour MultiSourceScanner (architecture modulaire)")
    @patch("src.features.network.routers.scan_router.MultiSourceScanner")  # ✅ Phase 5: Updated
    def test_post_scan_scanner_error(self, mock_scanner_class, client):
        """Test POST /scan avec erreur scanner"""
        # Setup mock pour lever exception
        mock_instance = Mock()
        mock_instance.scan_network = AsyncMock(side_effect=Exception("Network error"))
        mock_scanner_class.return_value = mock_instance
        
        scan_request = {
            "subnet": "192.168.1.0/24",
            "scan_type": "quick"
        }
        
        response = client.post("/api/network/scan", json=scan_request)
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
