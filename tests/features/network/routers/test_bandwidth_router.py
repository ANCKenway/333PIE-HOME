"""
🧪 Tests - Bandwidth Router

Tests pour les endpoints de monitoring de bande passante
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import app
from app import app


@pytest.fixture
def client():
    """FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def sample_device_stats():
    """Stats bandwidth device pour tests"""
    stats = Mock()
    stats.ip = "192.168.1.100"
    stats.mac = "aa:bb:cc:dd:ee:ff"
    stats.hostname = "test-device"
    stats.current_upload_bps = 5120000  # 5 Mbps
    stats.current_download_bps = 10240000  # 10 Mbps
    stats.current_mbps = 15.0
    stats.total_bytes_sent = 102400000  # 100MB
    stats.total_bytes_received = 204800000  # 200MB
    stats.total_mb = 300.0
    stats.avg_upload_bps = 4096000
    stats.avg_download_bps = 8192000
    stats.avg_mbps = 12.0
    stats.peak_mbps = 25.0
    stats.peak_timestamp = datetime.now()
    stats.uptime_seconds = 3600
    stats.sample_count = 120
    return stats


class TestBandwidthRouter:
    """Tests pour bandwidth_router.py"""
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_get_stats_global(self, mock_get_monitor, client, sample_device_stats):
        """Test GET /bandwidth/stats sans mac (global)"""
        mock_monitor = Mock()
        mock_monitor.get_all_stats.return_value = [sample_device_stats]
        mock_monitor.get_total_bandwidth.return_value = {"total_mbps": 15.0}
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/bandwidth/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "network" in data
        assert "devices_count" in data
        assert data["devices_count"] == 1
        mock_monitor.get_all_stats.assert_called_once()
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_get_stats_device(self, mock_get_monitor, client, sample_device_stats):
        """Test GET /bandwidth/stats?mac=X"""
        mock_monitor = Mock()
        mock_monitor.get_stats.return_value = sample_device_stats
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/bandwidth/stats?mac=aa:bb:cc:dd:ee:ff")
        
        assert response.status_code == 200
        data = response.json()
        assert "device" in data
        assert data["device"]["ip"] == "192.168.1.100"
        assert data["device"]["mac"] == "aa:bb:cc:dd:ee:ff"
        mock_monitor.get_stats.assert_called_once_with("aa:bb:cc:dd:ee:ff")
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_get_stats_device_not_found(self, mock_get_monitor, client):
        """Test GET /bandwidth/stats?mac=X device introuvable"""
        mock_monitor = Mock()
        mock_monitor.get_stats.return_value = None
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/bandwidth/stats?mac=unknown:mac")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_get_top_talkers(self, mock_get_monitor, client, sample_device_stats):
        """Test GET /bandwidth/top-talkers"""
        mock_monitor = Mock()
        mock_monitor.get_top_talkers.return_value = [sample_device_stats]
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/bandwidth/top-talkers")
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "top_talkers" in data
        assert data["count"] == 1
        mock_monitor.get_top_talkers.assert_called_once_with(limit=10, sort_by="total")
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_get_top_talkers_with_params(self, mock_get_monitor, client):
        """Test GET /bandwidth/top-talkers avec paramètres"""
        mock_monitor = Mock()
        mock_monitor.get_top_talkers.return_value = []
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/bandwidth/top-talkers?limit=5&sort_by=upload")
        
        assert response.status_code == 200
        mock_monitor.get_top_talkers.assert_called_once_with(limit=5, sort_by="upload")
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_register_device(self, mock_get_monitor, client, sample_device_stats):
        """Test POST /bandwidth/register"""
        mock_monitor = Mock()
        mock_monitor.register_device.return_value = sample_device_stats
        mock_get_monitor.return_value = mock_monitor
        
        # L'API utilise Query params, pas JSON body
        response = client.post(
            "/api/network/bandwidth/register?ip=192.168.1.100&mac=aa:bb:cc:dd:ee:ff&hostname=test-device"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "registered" in data["message"].lower()
        mock_monitor.register_device.assert_called_once_with(
            "192.168.1.100",
            "aa:bb:cc:dd:ee:ff",
            "test-device"
        )
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_register_device_error(self, mock_get_monitor, client):
        """Test POST /bandwidth/register avec erreur"""
        mock_monitor = Mock()
        mock_monitor.register_device.side_effect = Exception("Registration failed")
        mock_get_monitor.return_value = mock_monitor
        
        response = client.post(
            "/api/network/bandwidth/register?ip=192.168.1.100&mac=aa:bb:cc:dd:ee:ff"
        )
        
        assert response.status_code == 500
        assert "erreur" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_add_sample(self, mock_get_monitor, client):
        """Test POST /bandwidth/sample"""
        mock_monitor = Mock()
        mock_get_monitor.return_value = mock_monitor
        
        # L'API utilise Query params, pas JSON body
        response = client.post(
            "/api/network/bandwidth/sample?mac=aa:bb:cc:dd:ee:ff&bytes_sent=1024000&bytes_received=2048000"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added" in data["message"].lower()
        mock_monitor.add_sample.assert_called_once_with(
            "aa:bb:cc:dd:ee:ff",
            1024000,
            2048000
        )
    
    @patch("src.features.network.routers.bandwidth_router.get_bandwidth_monitor")
    def test_add_sample_error(self, mock_get_monitor, client):
        """Test POST /bandwidth/sample avec erreur"""
        mock_monitor = Mock()
        mock_monitor.add_sample.side_effect = Exception("Sample failed")
        mock_get_monitor.return_value = mock_monitor
        
        response = client.post(
            "/api/network/bandwidth/sample?mac=aa:bb:cc:dd:ee:ff&bytes_sent=1024&bytes_received=2048"
        )
        
        assert response.status_code == 500
        assert "erreur" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
