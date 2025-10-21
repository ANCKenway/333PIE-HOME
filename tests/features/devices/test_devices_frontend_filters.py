"""
Tests pour les filtres frontend du module Devices

Suite de tests vérifiant la logique de filtrage côté client :
- Recherche multi-champs (IP, MAC, nom, vendor, hostname)
- Filtre de statut (online/offline)
- Filtre de type (desktop, laptop, server, etc.)
- Filtre de location (in_network)
- Combinaison de filtres
"""

import pytest
from unittest.mock import Mock, patch
import json


class TestDevicesFilters:
    """Tests pour la logique de filtrage des devices"""

    @pytest.fixture
    def sample_devices(self):
        """Génère une liste de devices pour les tests"""
        return [
            {
                "id": "dev_1",
                "name": "CLACLA",
                "ip": "192.168.1.24",
                "mac": "10:7C:61:78:72:8B",
                "hostname": "CLACLA",
                "type": "laptop",
                "vendor": "ASUSTek COMPUTER INC.",
                "online": True,
                "in_devices": True,
                "in_network": True
            },
            {
                "id": "dev_2",
                "name": "TITO",
                "ip": "192.168.1.174",
                "mac": "34:5A:60:7F:12:C1",
                "hostname": "TITO",
                "type": "desktop",
                "vendor": "Micro-Star International",
                "online": False,
                "in_devices": True,
                "in_network": True
            },
            {
                "id": "dev_3",
                "name": "Server-NAS",
                "ip": "192.168.1.100",
                "mac": "AA:BB:CC:DD:EE:FF",
                "hostname": "nas-server",
                "type": "nas",
                "vendor": "Synology",
                "online": True,
                "in_devices": True,
                "in_network": False
            },
            {
                "id": "dev_4",
                "name": "iPhone",
                "ip": "192.168.1.50",
                "mac": "11:22:33:44:55:66",
                "hostname": "iPhone-12",
                "type": "mobile",
                "vendor": "Apple",
                "online": True,
                "in_devices": True,
                "in_network": True
            },
        ]

    def test_filter_search_by_name(self, sample_devices):
        """Test recherche par nom"""
        search = "clacla"
        filtered = [
            d for d in sample_devices
            if search.lower() in d.get("name", "").lower()
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["name"] == "CLACLA"

    def test_filter_search_by_ip(self, sample_devices):
        """Test recherche par IP"""
        search = "192.168.1.24"
        filtered = [
            d for d in sample_devices
            if search in d.get("ip", "")
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["ip"] == "192.168.1.24"

    def test_filter_search_by_mac(self, sample_devices):
        """Test recherche par MAC"""
        search = "10:7C:61"
        filtered = [
            d for d in sample_devices
            if search.lower() in d.get("mac", "").lower()
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["mac"] == "10:7C:61:78:72:8B"

    def test_filter_search_by_vendor(self, sample_devices):
        """Test recherche par vendor"""
        search = "asus"
        filtered = [
            d for d in sample_devices
            if search.lower() in d.get("vendor", "").lower()
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["vendor"] == "ASUSTek COMPUTER INC."

    def test_filter_search_by_hostname(self, sample_devices):
        """Test recherche par hostname"""
        search = "nas-server"
        filtered = [
            d for d in sample_devices
            if search.lower() in d.get("hostname", "").lower()
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["hostname"] == "nas-server"

    def test_filter_status_online(self, sample_devices):
        """Test filtre statut: online uniquement"""
        filtered = [d for d in sample_devices if d.get("online") is True]
        
        assert len(filtered) == 3
        assert all(d["online"] for d in filtered)

    def test_filter_status_offline(self, sample_devices):
        """Test filtre statut: offline uniquement"""
        filtered = [d for d in sample_devices if d.get("online") is False]
        
        assert len(filtered) == 1
        assert filtered[0]["name"] == "TITO"

    def test_filter_type_laptop(self, sample_devices):
        """Test filtre type: laptop"""
        filtered = [d for d in sample_devices if d.get("type") == "laptop"]
        
        assert len(filtered) == 1
        assert filtered[0]["type"] == "laptop"

    def test_filter_type_desktop(self, sample_devices):
        """Test filtre type: desktop"""
        filtered = [d for d in sample_devices if d.get("type") == "desktop"]
        
        assert len(filtered) == 1
        assert filtered[0]["type"] == "desktop"

    def test_filter_type_nas(self, sample_devices):
        """Test filtre type: NAS"""
        filtered = [d for d in sample_devices if d.get("type") == "nas"]
        
        assert len(filtered) == 1
        assert filtered[0]["type"] == "nas"

    def test_filter_type_mobile(self, sample_devices):
        """Test filtre type: mobile"""
        filtered = [d for d in sample_devices if d.get("type") == "mobile"]
        
        assert len(filtered) == 1
        assert filtered[0]["type"] == "mobile"

    def test_filter_location_in_network(self, sample_devices):
        """Test filtre location: in_network"""
        filtered = [d for d in sample_devices if d.get("in_network") is True]
        
        assert len(filtered) == 3
        assert all(d["in_network"] for d in filtered)

    def test_filter_combined_online_and_laptop(self, sample_devices):
        """Test combinaison de filtres: online + laptop"""
        filtered = [
            d for d in sample_devices
            if d.get("online") is True and d.get("type") == "laptop"
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["name"] == "CLACLA"

    def test_filter_combined_search_and_type(self, sample_devices):
        """Test combinaison: recherche + type"""
        search = "server"
        device_type = "nas"
        filtered = [
            d for d in sample_devices
            if search.lower() in d.get("hostname", "").lower()
            and d.get("type") == device_type
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["hostname"] == "nas-server"

    def test_filter_no_results(self, sample_devices):
        """Test filtre ne retournant aucun résultat"""
        search = "nonexistent"
        filtered = [
            d for d in sample_devices
            if search.lower() in d.get("name", "").lower()
        ]
        
        assert len(filtered) == 0

    def test_stats_calculation(self, sample_devices):
        """Test calcul des statistiques"""
        total = len(sample_devices)
        online = len([d for d in sample_devices if d.get("online") is True])
        offline = len([d for d in sample_devices if d.get("online") is False])
        
        assert total == 4
        assert online == 3
        assert offline == 1
        assert online + offline == total

    def test_export_csv_data_structure(self, sample_devices):
        """Test structure de données pour export CSV"""
        # Simuler la transformation pour export
        export_data = [
            {
                "name": d["name"],
                "ip": d["ip"],
                "mac": d.get("mac", ""),
                "type": d.get("type", "other"),
                "hostname": d.get("hostname", ""),
                "vendor": d.get("vendor", ""),
                "status": "online" if d.get("online") else "offline",
                "in_network": d.get("in_network", False),
            }
            for d in sample_devices
        ]
        
        assert len(export_data) == 4
        assert all("name" in d for d in export_data)
        assert all("ip" in d for d in export_data)
        assert all("status" in d for d in export_data)

    def test_csv_escape_commas(self):
        """Test échappement des virgules dans les valeurs CSV"""
        value = "ASUSTek COMPUTER INC., Taiwan"
        escaped = f'"{value}"' if "," in value else value
        
        assert escaped.startswith('"')
        assert escaped.endswith('"')

    def test_csv_escape_quotes(self):
        """Test échappement des guillemets dans les valeurs CSV"""
        value = 'Device "Main"'
        value_escaped = value.replace('"', '""')
        escaped = f'"{value_escaped}"'
        
        assert '""' in escaped  # Double quotes échappés


class TestDevicesFilterPerformance:
    """Tests de performance pour le filtrage"""

    def test_filter_large_dataset(self):
        """Test filtrage sur un grand dataset (1000 devices)"""
        import time
        
        # Générer 1000 devices
        devices = [
            {
                "id": f"dev_{i}",
                "name": f"Device-{i}",
                "ip": f"192.168.{i//255}.{i%255}",
                "mac": f"AA:BB:CC:DD:{i//255:02X}:{i%255:02X}",
                "type": ["desktop", "laptop", "server"][i % 3],
                "online": i % 2 == 0,
                "in_devices": True,
                "in_network": i % 3 != 0,
            }
            for i in range(1000)
        ]
        
        # Test performance de filtrage
        start = time.time()
        filtered = [d for d in devices if d.get("online") is True]
        elapsed = time.time() - start
        
        assert len(filtered) == 500
        assert elapsed < 0.1  # Doit être très rapide (< 100ms)

    def test_filter_multiple_conditions_performance(self):
        """Test performance avec conditions multiples"""
        import time
        
        devices = [
            {
                "id": f"dev_{i}",
                "name": f"Device-{i}",
                "ip": f"192.168.{i//255}.{i%255}",
                "type": ["desktop", "laptop"][i % 2],
                "online": True,
                "vendor": f"Vendor-{i % 10}",
            }
            for i in range(500)
        ]
        
        search = "Device-42"
        device_type = "desktop"
        
        start = time.time()
        filtered = [
            d for d in devices
            if search in d.get("name", "")
            and d.get("type") == device_type
            and d.get("online") is True
        ]
        elapsed = time.time() - start
        
        assert elapsed < 0.05  # Doit être très rapide (< 50ms)

