"""
🧪 Tests - Latency Router

Tests pour les endpoints de mesure de latence réseau
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Import app
from app import app


@pytest.fixture
def client():
    """FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def sample_latency_stats():
    """Stats latence pour tests"""
    stats = Mock()
    stats.ip = "192.168.1.100"
    stats.hostname = "test-device"
    stats.measurements_count = 100
    stats.avg_latency_ms = 16.2
    stats.min_latency_ms = 12.0
    stats.max_latency_ms = 25.0
    stats.jitter_ms = 3.5
    stats.packet_loss_percent = 0.0
    stats.quality_score = 95.0
    stats.quality_label = "Excellent"
    stats.last_measurement = datetime.now()
    return stats


class TestLatencyRouter:
    """Tests pour latency_router.py"""
    
    @patch("src.features.network.routers.latency_router.get_latency_monitor")
    def test_get_latency_success(self, mock_get_monitor, client, sample_latency_stats):
        """Test GET /latency/{ip} avec succès"""
        mock_monitor = Mock()
        mock_monitor.calculate_stats.return_value = sample_latency_stats
        mock_monitor.get_quality_icon.return_value = "🟢"
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/latency/192.168.1.100")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ip"] == "192.168.1.100"
        assert data["avg_latency_ms"] == 16.2
        assert data["quality_score"] == 95.0
        assert data["quality_label"] == "Excellent"
        mock_monitor.calculate_stats.assert_called_once_with("192.168.1.100")
    
    @patch("src.features.network.routers.latency_router.get_latency_monitor")
    def test_get_latency_not_found(self, mock_get_monitor, client):
        """Test GET /latency/{ip} device sans mesure"""
        mock_monitor = Mock()
        mock_monitor.calculate_stats.return_value = None
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/latency/192.168.1.200")
        
        assert response.status_code == 404
        assert "pas de données" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.latency_router.get_latency_monitor")
    def test_get_latency_error(self, mock_get_monitor, client):
        """Test GET /latency/{ip} avec erreur"""
        mock_monitor = Mock()
        mock_monitor.calculate_stats.side_effect = Exception("Database error")
        mock_get_monitor.return_value = mock_monitor
        
        response = client.get("/api/network/latency/192.168.1.100")
        
        assert response.status_code == 500
        assert "erreur" in response.json()["detail"].lower()
    
    @patch("src.features.network.routers.latency_router.get_latency_monitor")
    def test_measure_latency_success(self, mock_get_monitor, client, sample_latency_stats):
        """Test POST /latency/measure avec succès"""
        mock_monitor = Mock()
        mock_monitor.monitor_hosts = AsyncMock(return_value={
            "192.168.1.100": sample_latency_stats
        })
        mock_monitor.get_quality_icon.return_value = "🟢"
        mock_get_monitor.return_value = mock_monitor
        
        # L'API utilise Query params, pas JSON body
        response = client.post("/api/network/latency/measure?ips=192.168.1.100")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_measured"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["ip"] == "192.168.1.100"
        assert data["results"][0]["quality_score"] == 95.0
    
    @patch("src.features.network.routers.latency_router.get_latency_monitor")
    def test_measure_latency_multiple_ips(self, mock_get_monitor, client):
        """Test POST /latency/measure avec plusieurs IPs"""
        mock_monitor = Mock()
        
        # Créer 2 stats différents
        stats1 = Mock(ip="192.168.1.100", avg_latency_ms=15.0, quality_score=95.0, 
                     quality_label="Excellent", packet_loss_percent=0.0)
        stats2 = Mock(ip="192.168.1.200", avg_latency_ms=45.0, quality_score=70.0,
                     quality_label="Good", packet_loss_percent=5.0)
        
        mock_monitor.monitor_hosts = AsyncMock(return_value={
            "192.168.1.100": stats1,
            "192.168.1.200": stats2
        })
        mock_monitor.get_quality_icon.return_value = "🟢"
        mock_get_monitor.return_value = mock_monitor
        
        response = client.post("/api/network/latency/measure?ips=192.168.1.100&ips=192.168.1.200")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_measured"] == 2
        assert len(data["results"]) == 2
    
    @patch("src.features.network.routers.latency_router.get_latency_monitor")
    def test_measure_latency_error(self, mock_get_monitor, client):
        """Test POST /latency/measure avec erreur"""
        mock_monitor = Mock()
        mock_monitor.monitor_hosts.side_effect = Exception("Ping failed")
        mock_get_monitor.return_value = mock_monitor
        
        response = client.post("/api/network/latency/measure?ips=192.168.1.100")
        
        assert response.status_code == 500
        assert "erreur" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
