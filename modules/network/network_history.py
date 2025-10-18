"""
🏠 Network History - Historique unifié des appareils réseau
Track les changements d'IP, MAC, connexions/déconnexions dans un seul fichier
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class NetworkHistory:
    """Gestionnaire d'historique unifié des appareils réseau"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.history_file = data_dir / "network_history.json"
        self._ensure_structure()
    
    def _ensure_structure(self):
        """Assurer que la structure de données existe"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.history_file.exists():
            self._create_empty_history()
    
    def _create_empty_history(self):
        """Créer un fichier d'historique vide"""
        empty_history = {
            "devices_by_mac": {},  # {mac -> device_history} - CLÉ PRIMAIRE
            "devices_by_ip": {},   # {ip -> mac} - INDEX RAPIDE
            "scan_events": [],  # Liste des scans avec timestamps
            "connection_events": [],  # Connexions/déconnexions
            "ip_changes": [],  # Changements d'IP DHCP
            "mac_changes": [],  # Changements MAC (privacy)
            "last_scan": {
                "timestamp": None,
                "device_count": 0,
                "duration": 0
            },
            "stats": {
                "total_scans": 0,
                "unique_devices": 0,
                "last_updated": None
            },
            "version": "2.1"  # Nouvelle version avec MAC comme clé
        }
        self._save_history(empty_history)
        logger.info("Fichier network_history.json créé")
    
    def _save_history(self, data: Dict):
        """Sauvegarder l'historique"""
        try:
            data["stats"]["last_updated"] = datetime.now().isoformat()
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde historique: {e}")
    
    def _load_history(self) -> Dict:
        """Charger l'historique"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur chargement historique: {e}")
            self._create_empty_history()
            return self._load_history()
    
    def update_scan_results(self, devices: List[Dict], scan_duration: float) -> Dict:
        """Mettre à jour l'historique avec un nouveau scan"""
        history = self._load_history()
        current_time = time.time()
        scan_datetime = datetime.now().isoformat()
        
        # 1. Événement de scan
        scan_event = {
            "timestamp": current_time,
            "datetime": scan_datetime,
            "device_count": len(devices),
            "duration": round(scan_duration, 2)
        }
        history["scan_events"].insert(0, scan_event)
        history["scan_events"] = history["scan_events"][:50]  # Garder 50 derniers
        
        # 2. Analyser chaque appareil avec MAC comme clé primaire
        connection_events = []
        ip_changes = []
        mac_changes = []
        
        # Nettoyer l'index IP -> MAC pour les nouvelles données
        new_ip_index = {}
        
        for device in devices:
            ip = device['ip']
            mac = device.get('mac_address', '')
            
            if not mac:
                # Pas de MAC = pas de tracking possible, créer entrée temporaire par IP
                device_key = f"no_mac_{ip}"
                mac = device_key
            
            # Mettre à jour l'index IP -> MAC
            new_ip_index[ip] = mac
            
            # Vérifier si l'appareil (par MAC) existe déjà
            if mac in history["devices_by_mac"]:
                # Appareil existant - analyser les changements
                device_history = history["devices_by_mac"][mac]
                previous_data = device_history["current_data"]
                previous_ip = previous_data.get('ip', '')
                
                # CHANGEMENT D'IP détecté !
                if ip != previous_ip and previous_ip:
                    ip_changes.append({
                        "mac": mac,
                        "hostname": device.get('hostname', '') or previous_data.get('hostname', ''),
                        "vendor": device.get('vendor', '') or previous_data.get('vendor', ''),
                        "old_ip": previous_ip,
                        "new_ip": ip,
                        "timestamp": current_time,
                        "datetime": scan_datetime
                    })
                    logger.info(f"📍 CHANGEMENT IP: {mac[:8]}... {previous_ip} → {ip}")
                    
                    # Ajouter la nouvelle IP à l'historique
                    if ip not in device_history["ip_history"]:
                        device_history["ip_history"].append(ip)
                
                # Mise à jour basique
                device_history["last_seen"] = current_time
                device_history["last_seen_datetime"] = scan_datetime
                device_history["scan_count"] += 1
                device_history["current_data"] = device
                
                # Détecter changements hostname/vendor
                self._detect_other_changes(device_history, device, previous_data)
                
                # Ajouter snapshot à l'historique
                device_history["history"].insert(0, self._create_device_snapshot(device, current_time, scan_datetime))
                device_history["history"] = device_history["history"][:20]  # Garder 20 derniers
                
                # Événement de reconnexion si longtemps absent
                time_since_last = current_time - device_history.get("last_seen", current_time)
                if time_since_last > 3600:  # Plus d'1h
                    connection_events.append({
                        "type": "reconnection",
                        "mac": mac,
                        "ip": ip,
                        "old_ip": previous_ip,
                        "hostname": device.get('hostname', ''),
                        "vendor": device.get('vendor', ''),
                        "time_offline": time_since_last,
                        "timestamp": current_time,
                        "datetime": scan_datetime
                    })
            
            else:
                # Nouvel appareil (première fois vu)
                history["devices_by_mac"][mac] = {
                    "first_seen": current_time,
                    "first_seen_datetime": scan_datetime,
                    "last_seen": current_time,
                    "last_seen_datetime": scan_datetime,
                    "scan_count": 1,
                    "current_data": device,
                    "history": [self._create_device_snapshot(device, current_time, scan_datetime)],
                    "ip_history": [ip],
                    "mac_history": [mac] if mac and not mac.startswith('no_mac_') else [],
                    "hostname_history": [device.get('hostname', '')] if device.get('hostname') else [],
                    "vendor_history": [device.get('vendor', '')] if device.get('vendor') else []
                }
                
                # Événement de connexion (nouvel appareil)
                connection_events.append({
                    "type": "new_device",
                    "mac": mac,
                    "ip": ip,
                    "hostname": device.get('hostname', ''),
                    "vendor": device.get('vendor', ''),
                    "timestamp": current_time,
                    "datetime": scan_datetime
                })
                logger.info(f"🆕 NOUVEL APPAREIL: {ip} ({mac[:8]}...)")
        
        # 3. Mettre à jour l'index IP -> MAC
        history["devices_by_ip"] = new_ip_index
        
        # 4. Détecter déconnexions (appareils qui étaient là mais plus maintenant)
        current_macs = set(new_ip_index.values())
        for mac, device_history in history["devices_by_mac"].items():
            if mac not in current_macs:
                last_seen = device_history.get("last_seen", 0)
                
                # Seulement si vu récemment (éviter spam vieux appareils)
                if current_time - last_seen < 86400:  # 24h
                    previous_data = device_history["current_data"]
                    connection_events.append({
                        "type": "disconnection",
                        "mac": mac,
                        "ip": previous_data.get('ip', ''),
                        "hostname": previous_data.get('hostname', ''),
                        "vendor": previous_data.get('vendor', ''),
                        "time_offline": current_time - last_seen,
                        "timestamp": current_time,
                        "datetime": scan_datetime
                    })
        
        # 5. Ajouter les événements
        history["connection_events"] = connection_events + history["connection_events"]
        history["connection_events"] = history["connection_events"][:100]  # Garder 100 derniers
        
        history["ip_changes"] = ip_changes + history["ip_changes"]
        history["ip_changes"] = history["ip_changes"][:50]
        
        history["mac_changes"] = mac_changes + history["mac_changes"]
        history["mac_changes"] = history["mac_changes"][:50]
        
        # 6. Mise à jour des stats
        history["last_scan"] = {
            "timestamp": current_time,
            "datetime": scan_datetime,
            "device_count": len(devices),
            "duration": round(scan_duration, 2)
        }
        
        history["stats"]["total_scans"] += 1
        history["stats"]["unique_devices"] = len(history["devices_by_mac"])
        
        # 7. Sauvegarder
        self._save_history(history)
        
        # 8. Retourner statistiques des changements
        changes_summary = {
            "new_devices": len([e for e in connection_events if e["type"] == "new_device"]),
            "reconnections": len([e for e in connection_events if e["type"] == "reconnection"]),
            "disconnections": len([e for e in connection_events if e["type"] == "disconnection"]),
            "mac_changes": len(mac_changes),
            "ip_changes": len(ip_changes)
        }
        
        logger.info(f"📊 Historique unifié mis à jour: {changes_summary}")
        return changes_summary
    
    def _detect_other_changes(self, device_history: Dict, device: Dict, previous_data: Dict):
        """Détecter les changements hostname/vendor"""
        # Détecter changements hostname
        prev_hostname = previous_data.get('hostname', '')
        curr_hostname = device.get('hostname', '')
        if curr_hostname and curr_hostname != prev_hostname:
            if curr_hostname not in device_history["hostname_history"]:
                device_history["hostname_history"].append(curr_hostname)
        
        # Détecter changements vendor
        prev_vendor = previous_data.get('vendor', '')
        curr_vendor = device.get('vendor', '')
        if curr_vendor and curr_vendor != prev_vendor:
            if curr_vendor not in device_history["vendor_history"]:
                device_history["vendor_history"].append(curr_vendor)
                prev_vendor = previous_data.get('vendor', '')
                curr_vendor = device.get('vendor', '')
                if curr_vendor and curr_vendor != prev_vendor:
                    if curr_vendor not in device_history["vendor_history"]:
                        device_history["vendor_history"].append(curr_vendor)
                
                # Ajouter snapshot à l'historique
                device_history["history"].insert(0, self._create_device_snapshot(device, current_time, scan_datetime))
                device_history["history"] = device_history["history"][:20]  # Garder 20 derniers
                
                # Mettre à jour current_data
                device_history["current_data"] = device
                
                # Événement de reconnexion si longtemps absent
                time_since_last = current_time - device_history.get("last_seen", current_time)
                if time_since_last > 3600:  # Plus d'1h
                    connection_events.append({
                        "type": "reconnection",
                        "ip": ip,
                        "mac": mac,
                        "hostname": device.get('hostname', ''),
                        "vendor": device.get('vendor', ''),
                        "time_offline": time_since_last,
                        "timestamp": current_time,
                        "datetime": scan_datetime
                    })
        
        # 4. Ajouter les événements
        history["connection_events"] = connection_events + history["connection_events"]
        history["connection_events"] = history["connection_events"][:100]  # Garder 100 derniers
        
        history["ip_changes"] = ip_changes + history["ip_changes"]
        history["ip_changes"] = history["ip_changes"][:50]
        
        history["mac_changes"] = mac_changes + history["mac_changes"]
        history["mac_changes"] = history["mac_changes"][:50]
        
        # 5. Mise à jour des stats
        history["last_scan"] = {
            "timestamp": current_time,
            "datetime": scan_datetime,
            "device_count": len(devices),
            "duration": round(scan_duration, 2)
        }
        
        history["stats"]["total_scans"] += 1
        history["stats"]["unique_devices"] = len(history["devices_by_mac"])
        
        # 6. Sauvegarder
        self._save_history(history)
        
        # 7. Retourner statistiques des changements
        changes_summary = {
            "new_devices": len([e for e in connection_events if e["type"] == "new_device"]),
            "reconnections": len([e for e in connection_events if e["type"] == "reconnection"]),
            "disconnections": len([e for e in connection_events if e["type"] == "disconnection"]),
            "mac_changes": len(mac_changes),
            "ip_changes": len(ip_changes)
        }
        
        logger.info(f"📊 Historique mis à jour: {changes_summary}")
        return changes_summary
    
    def _create_device_snapshot(self, device: Dict, timestamp: float, datetime_str: str) -> Dict:
        """Créer un snapshot d'appareil"""
        return {
            "timestamp": timestamp,
            "datetime": datetime_str,
            "ip": device['ip'],
            "mac": device.get('mac_address', ''),
            "hostname": device.get('hostname', ''),
            "vendor": device.get('vendor', ''),
            "os_detected": device.get('os_detected', ''),
            "device_type": device.get('device_type', ''),
            "ping_success": device.get('ping_success', False),
            "open_ports": device.get('open_ports', [])
        }
    
    def get_device_history(self, mac_or_ip: str) -> Optional[Dict]:
        """Récupérer l'historique d'un appareil spécifique par MAC ou IP"""
        history = self._load_history()
        
        # D'abord essayer par MAC
        if mac_or_ip in history["devices_by_mac"]:
            return history["devices_by_mac"][mac_or_ip]
        
        # Sinon essayer par IP (lookup dans l'index)
        mac = history["devices_by_ip"].get(mac_or_ip)
        if mac and mac in history["devices_by_mac"]:
            return history["devices_by_mac"][mac]
        
        return None
    
    def get_recent_events(self, limit: int = 20) -> Dict:
        """Récupérer les événements récents"""
        history = self._load_history()
        return {
            "connection_events": history["connection_events"][:limit],
            "ip_changes": history["ip_changes"][:limit],
            "mac_changes": history["mac_changes"][:limit]
        }
    
    def get_device_list(self) -> List[Dict]:
        """Récupérer la liste enrichie des appareils"""
        history = self._load_history()
        devices = []
        
        current_time = time.time()
        
        for mac, device_history in history["devices_by_mac"].items():
            device = device_history["current_data"].copy()
            
            # Enrichir avec données historiques
            device["mac_primary"] = mac
            device["first_seen_datetime"] = device_history["first_seen_datetime"]
            device["scan_count"] = device_history["scan_count"]
            device["ip_count"] = len(device_history["ip_history"])
            device["mac_count"] = len(device_history["mac_history"])
            device["hostname_count"] = len(device_history["hostname_history"])
            device["vendor_count"] = len(device_history["vendor_history"])
            
            # Historique des IPs pour debug
            device["all_ips"] = device_history["ip_history"]
            
            # Temps depuis dernière vue
            last_seen = device_history["last_seen"]
            elapsed = int(current_time - last_seen)
            if elapsed < 3600:
                device["last_seen_ago"] = f"Il y a {elapsed//60}min"
            elif elapsed < 86400:
                device["last_seen_ago"] = f"Il y a {elapsed//3600}h"
            else:
                device["last_seen_ago"] = f"Il y a {elapsed//86400}j"
            
            device["is_recent"] = elapsed < 300  # 5min = récent
            devices.append(device)
        
        # Trier par dernière vue
        devices.sort(key=lambda d: history["devices_by_mac"][d["mac_primary"]]["last_seen"], reverse=True)
        return devices
    
    def get_device_by_mac(self, mac: str) -> Dict:
        """Récupérer les données complètes d'un appareil par son MAC"""
        history = self._load_history()
        
        if mac in history["devices_by_mac"]:
            return history["devices_by_mac"][mac]
        else:
            return None
    
    def get_history(self) -> Dict:
        """Récupérer l'historique complet"""
        return self._load_history()
    
    def get_stats(self) -> Dict:
        """Récupérer les statistiques globales"""
        history = self._load_history()
        
        return {
            "total_scans": history["stats"]["total_scans"],
            "unique_devices": history["stats"]["unique_devices"],
            "last_scan": history["last_scan"],
            "recent_events_count": len(history["connection_events"]),
            "has_data": history["last_scan"]["timestamp"] is not None
        }

# Instance globale
network_history = None

def get_network_history(data_dir: Path) -> NetworkHistory:
    """Factory pour obtenir l'instance de l'historique"""
    global network_history
    if network_history is None:
        network_history = NetworkHistory(data_dir)
    return network_history