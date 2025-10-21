"""
🧪 Tests - Device Router

Tests pour les endpoints de gestion des devices réseau
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import app
from app import app

# Import schemas
from src.features.network.schemas import (
    NetworkDevice,
    DeviceHistory,
    NetworkTimeline,
    NetworkStats,
    NetworkEvent,
    NetworkEventType,
    IPHistoryEntry,
)


@pytest.fixture
def client():
    """FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def sample_device():
    """Device réseau pour tests"""
    return NetworkDevice(
        mac="aa:bb:cc:dd:ee:ff",
        current_ip="192.168.1.100",
        current_hostname="test-device",
        vendor="Test Vendor",
        device_type="💻 Computer",
        os_detected="Linux",
        device_role=None,
        id="dev_network_aabbccddeeff",
        first_seen=datetime.now() - timedelta(days=7),
        last_seen=datetime.now(),
        total_appearances=42,
        currently_online=True,
        in_devices=False,
        tags=[],
        services=[],
    )


@pytest.fixture
def sample_device_offline():
    """Device offline pour tests"""
    return NetworkDevice(
        mac="11:22:33:44:55:66",
        current_ip="192.168.1.200",
        current_hostname="offline-device",
        vendor="Offline Vendor",
        device_type="📱 Phone",
        os_detected="Android",
        device_role=None,
        id="dev_network_112233445566",
        first_seen=datetime.now() - timedelta(days=30),
        last_seen=datetime.now() - timedelta(hours=5),
        total_appearances=10,
        currently_online=False,
        in_devices=False,
        tags=[],
        services=[],
    )


@pytest.fixture
def sample_device_history():
    """Historique device pour tests"""
    from src.features.network.schemas import DeviceStatistics, OnlinePeriod
    
    return DeviceHistory(
        mac="aa:bb:cc:dd:ee:ff",  # Pas device_mac !
        device_name="test-device",
        first_seen=datetime.now() - timedelta(days=7),
        last_seen=datetime.now(),
        total_appearances=42,
        ip_history=[
            IPHistoryEntry(
                ip="192.168.1.100",
                first_seen=datetime.now() - timedelta(days=7),
                last_seen=datetime.now(),
                total_count=42,
            )
        ],
        events=[
            NetworkEvent(
                event_id="evt_123",
                timestamp=datetime.now() - timedelta(hours=1),
                event_type=NetworkEventType.DEVICE_APPEARED,
                device_mac="aa:bb:cc:dd:ee:ff",
                device_name="test-device",
                details={},
            )
        ],
        online_periods=[
            OnlinePeriod(
                start=datetime.now() - timedelta(hours=5),
                end=datetime.now(),
                duration_hours=5.0,
            )
        ],
        statistics=DeviceStatistics(
            mac="aa:bb:cc:dd:ee:ff",
            name="test-device",
            total_appearances=42,
            uptime_percentage=85.5,
            average_connection_duration_hours=6.5,
            last_ip="192.168.1.100",
            last_seen=datetime.now(),
        ),
    )


@pytest.fixture
def sample_timeline():
    """Timeline pour tests"""
    return NetworkTimeline(
        start_time=datetime.now() - timedelta(hours=24),
        end_time=datetime.now(),
        total_events=5,
        events=[
            NetworkEvent(
                event_id=f"evt_{i}",
                timestamp=datetime.now() - timedelta(hours=i),
                event_type=NetworkEventType.DEVICE_APPEARED,
                device_mac="aa:bb:cc:dd:ee:ff",
                device_name="test-device",
                details={},
            )
            for i in range(5)
        ],
    )


@pytest.fixture
def sample_stats():
    """Stats réseau pour tests"""
    from src.features.network.schemas import DeviceStatistics
    
    return NetworkStats(
        total_devices_seen=10,  # Pas total_devices !
        currently_online=7,  # Pas online_devices !
        currently_offline=3,  # Pas offline_devices !
        average_devices_online=6.5,
        new_devices_last_24h=2,
        ip_changes_last_24h=1,
        most_stable_device=None,
        most_active_device=None,
        last_scan=datetime.now(),
    )


class TestDeviceRouter:
    """Tests pour device_router.py"""
    
    @patch("src.features.network.routers.device_router.get_all_devices")
    def test_get_devices_all(self, mock_get_all, client, sample_device, sample_device_offline):
        """Test GET /devices retourne tous les devices"""
        mock_get_all.return_value = [sample_device, sample_device_offline]
        
        response = client.get("/api/network/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["mac"] in ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66"]
        mock_get_all.assert_called_once()
    
    @patch("src.features.network.routers.device_router.get_all_devices")
    def test_get_devices_online_only(self, mock_get_all, client, sample_device, sample_device_offline):
        """Test GET /devices?online_only=true filtre online"""
        mock_get_all.return_value = [sample_device, sample_device_offline]
        
        response = client.get("/api/network/devices?online_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["mac"] == "aa:bb:cc:dd:ee:ff"
        assert data[0]["currently_online"] is True
    
    @patch("src.features.network.routers.device_router.get_all_devices")
    def test_get_devices_error(self, mock_get_all, client):
        """Test GET /devices avec erreur"""
        mock_get_all.side_effect = Exception("Database error")
        
        response = client.get("/api/network/devices")
        
        assert response.status_code == 500
        assert "erreur" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.device_router.NetworkHistory")
    def test_get_device_history_success(self, mock_history_class, client, sample_device_history):
        """Test GET /devices/history/{mac} avec succès"""
        mock_history = Mock()
        mock_history.get_device_history.return_value = sample_device_history
        mock_history_class.return_value = mock_history
        
        response = client.get("/api/network/devices/history/aa:bb:cc:dd:ee:ff")
        
        assert response.status_code == 200
        data = response.json()
        assert data["mac"] == "aa:bb:cc:dd:ee:ff"  # Pas device_mac !
        assert data["total_appearances"] == 42
        assert len(data["events"]) == 1
        assert len(data["online_periods"]) == 1
        mock_history.get_device_history.assert_called_once_with("aa:bb:cc:dd:ee:ff")
    
    @patch("src.features.network.routers.device_router.NetworkHistory")
    def test_get_device_history_not_found(self, mock_history_class, client):
        """Test GET /devices/history/{mac} device introuvable"""
        mock_history = Mock()
        mock_history.get_device_history.return_value = None
        mock_history_class.return_value = mock_history
        
        response = client.get("/api/network/devices/history/unknown:mac")
        
        assert response.status_code == 404
        assert "non trouvé" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.device_router.NetworkHistory")
    def test_get_timeline_default(self, mock_history_class, client, sample_timeline):
        """Test GET /devices/timeline avec paramètres par défaut"""
        mock_history = Mock()
        mock_history.get_timeline.return_value = sample_timeline
        mock_history_class.return_value = mock_history
        
        response = client.get("/api/network/devices/timeline")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] == 5
        assert len(data["events"]) == 5
        # Vérifier que hours=24 par défaut
        mock_history.get_timeline.assert_called_once_with(hours=24, device_mac=None)
    
    @patch("src.features.network.routers.device_router.NetworkHistory")
    def test_get_timeline_filtered(self, mock_history_class, client, sample_timeline):
        """Test GET /devices/timeline avec filtres"""
        mock_history = Mock()
        mock_history.get_timeline.return_value = sample_timeline
        mock_history_class.return_value = mock_history
        
        response = client.get(
            "/api/network/devices/timeline?hours=48&device_mac=aa:bb:cc:dd:ee:ff"
        )
        
        assert response.status_code == 200
        mock_history.get_timeline.assert_called_once_with(
            hours=48,
            device_mac="aa:bb:cc:dd:ee:ff"
        )
    
    def test_promote_device_success(self, client, sample_device):
        """Test POST /devices/{mac}/promote avec succès"""
        with patch("src.features.network.routers.device_router.get_device_by_mac") as mock_get_device, \
             patch("src.features.devices.manager.DeviceManager") as mock_manager_class, \
             patch("src.features.network.routers.device_router.NetworkHistory") as mock_history_class, \
             patch("src.features.network.routers.device_router.update_device_in_devices_flag") as mock_update_flag:
            
            # Setup mocks
            mock_get_device.return_value = sample_device
            
            mock_manager = Mock()
            mock_created_device = Mock()
            mock_created_device.id = "dev_aabbccddeeff"
            mock_manager.create_device.return_value = mock_created_device
            mock_manager_class.return_value = mock_manager
            
            mock_history = Mock()
            mock_history_class.return_value = mock_history
            
            # Request
            promote_request = {
                "name": "My Test Device",
                "type": "computer",
                "description": "Test device",
                "tags": ["test", "lab"],
            }
            
            response = client.post(
                "/api/network/devices/aa:bb:cc:dd:ee:ff/promote",
                json=promote_request,
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["device_id"] == "dev_aabbccddeeff"
            assert data["device_name"] == "My Test Device"
            
            # Vérifier appels
            mock_get_device.assert_called_once_with("aa:bb:cc:dd:ee:ff")
            mock_manager.create_device.assert_called_once()
            mock_update_flag.assert_called_once_with("aa:bb:cc:dd:ee:ff", True)
            mock_history._save_event.assert_called_once()
    
    @patch("src.features.network.routers.device_router.get_device_by_mac")
    def test_promote_device_not_found(self, mock_get_device, client):
        """Test POST /devices/{mac}/promote device introuvable"""
        mock_get_device.return_value = None
        
        promote_request = {"name": "Test"}
        
        response = client.post(
            "/api/network/devices/unknown:mac/promote",
            json=promote_request,
        )
        
        assert response.status_code == 404
        assert "non trouvé" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.device_router.NetworkHistory")
    def test_get_stats(self, mock_history_class, client, sample_stats):
        """Test GET /devices/stats"""
        mock_history = Mock()
        mock_history.get_network_stats.return_value = sample_stats
        mock_history_class.return_value = mock_history
        
        response = client.get("/api/network/devices/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_devices_seen"] == 10
        assert data["currently_online"] == 7
        assert data["currently_offline"] == 3
        assert data["average_devices_online"] == 6.5
        mock_history.get_network_stats.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
