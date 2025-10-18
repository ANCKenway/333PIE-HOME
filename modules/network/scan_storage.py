"""
🏠 Scan Storage - Stockage persistant des scans réseau
Gestion de l'historique et des appareils déconnectés
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ScanStorage:
    """Gestionnaire de stockage des scans réseau"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.scan_file = data_dir / "last_scan.json"
        self._ensure_structure()
    
    def _ensure_structure(self):
        """Assurer que la structure de données existe"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.scan_file.exists():
            self._create_empty_scan_file()
    
    def _create_empty_scan_file(self):
        """Créer un fichier de scan vide"""
        empty_scan = {
            "last_scan": {
                "timestamp": None,
                "devices": [],
                "stats": {
                    "total_devices": 0,
                    "online_devices": 0,
                    "scan_duration": 0
                }
            },
            "scan_history": [],
            "disconnected_devices": [],
            "version": "1.0"
        }
        self._save_scan_data(empty_scan)
        logger.info("Fichier last_scan.json créé")
    
    def _save_scan_data(self, data: Dict):
        """Sauvegarder les données de scan"""
        try:
            with open(self.scan_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde scan: {e}")
    
    def _load_scan_data(self) -> Dict:
        """Charger les données de scan"""
        try:
            with open(self.scan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur chargement scan: {e}")
            self._create_empty_scan_file()
            return self._load_scan_data()
    
    def save_scan_result(self, devices: List[Dict], scan_duration: float) -> bool:
        """Sauvegarder un nouveau résultat de scan"""
        try:
            data = self._load_scan_data()
            current_time = time.time()
            
            # Préparer le nouveau scan
            new_scan = {
                "timestamp": current_time,
                "datetime": datetime.now().isoformat(),
                "devices": devices,
                "stats": {
                    "total_devices": len(devices),
                    "online_devices": len([d for d in devices if d.get('ping_success', False)]),
                    "scan_duration": round(scan_duration, 2)
                }
            }
            
            # Détecter les appareils déconnectés
            if data["last_scan"]["devices"]:
                self._detect_disconnected_devices(data, devices)
            
            # Ajouter à l'historique (garder 50 derniers scans)
            data["scan_history"].insert(0, {
                "timestamp": current_time,
                "datetime": new_scan["datetime"],
                "device_count": len(devices),
                "duration": scan_duration
            })
            data["scan_history"] = data["scan_history"][:50]
            
            # Mettre à jour le dernier scan
            data["last_scan"] = new_scan
            
            # Sauvegarder
            self._save_scan_data(data)
            logger.info(f"Scan sauvegardé: {len(devices)} appareils")
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde scan: {e}")
            return False
    
    def _detect_disconnected_devices(self, data: Dict, current_devices: List[Dict]):
        """Détecter les appareils qui se sont déconnectés"""
        try:
            # IPs du scan précédent et actuel
            previous_ips = {d['ip'] for d in data["last_scan"]["devices"] if d.get('ping_success', False)}
            current_ips = {d['ip'] for d in current_devices if d.get('ping_success', False)}
            
            # Appareils déconnectés
            disconnected_ips = previous_ips - current_ips
            
            if disconnected_ips:
                current_time = time.time()
                
                # Trouver les infos des appareils déconnectés
                for device in data["last_scan"]["devices"]:
                    if device['ip'] in disconnected_ips:
                        disconnected_device = {
                            "ip": device['ip'],
                            "hostname": device.get('hostname', 'N/A'),
                            "vendor": device.get('vendor', 'Inconnu'),
                            "os_detected": device.get('os_detected', 'Inconnu'),
                            "last_seen": current_time,
                            "last_seen_datetime": datetime.now().isoformat(),
                            "device_type": device.get('device_type', 'Inconnu')
                        }
                        
                        # Ajouter aux déconnectés (éviter doublons)
                        existing = next((d for d in data["disconnected_devices"] if d['ip'] == device['ip']), None)
                        if existing:
                            data["disconnected_devices"].remove(existing)
                        
                        data["disconnected_devices"].insert(0, disconnected_device)
                
                # Garder 100 derniers déconnectés max
                data["disconnected_devices"] = data["disconnected_devices"][:100]
                
                # Nettoyer les vieux (> 7 jours)
                week_ago = current_time - (7 * 24 * 3600)
                data["disconnected_devices"] = [
                    d for d in data["disconnected_devices"] 
                    if d['last_seen'] > week_ago
                ]
                
                logger.info(f"Détecté {len(disconnected_ips)} appareils déconnectés")
        
        except Exception as e:
            logger.error(f"Erreur détection déconnectés: {e}")
    
    def get_last_scan(self) -> Dict:
        """Récupérer le dernier scan"""
        data = self._load_scan_data()
        return data["last_scan"]
    
    def get_scan_history(self, limit: int = 10) -> List[Dict]:
        """Récupérer l'historique des scans"""
        data = self._load_scan_data()
        return data["scan_history"][:limit]
    
    def get_disconnected_devices(self, limit: int = 20) -> List[Dict]:
        """Récupérer les appareils récemment déconnectés"""
        data = self._load_scan_data()
        
        # Enrichir avec temps relatif
        current_time = time.time()
        for device in data["disconnected_devices"][:limit]:
            elapsed = int(current_time - device['last_seen'])
            if elapsed < 3600:
                device['time_ago'] = f"Il y a {elapsed//60}min"
            elif elapsed < 86400:
                device['time_ago'] = f"Il y a {elapsed//3600}h"
            else:
                device['time_ago'] = f"Il y a {elapsed//86400}j"
        
        return data["disconnected_devices"][:limit]
    
    def get_stats(self) -> Dict:
        """Récupérer les statistiques globales"""
        data = self._load_scan_data()
        
        last_scan = data["last_scan"]
        history_count = len(data["scan_history"])
        disconnected_count = len(data["disconnected_devices"])
        
        return {
            "last_scan_time": last_scan.get("datetime"),
            "last_scan_devices": last_scan.get("stats", {}).get("total_devices", 0),
            "scan_history_count": history_count,
            "disconnected_devices_count": disconnected_count,
            "has_scan_data": last_scan.get("timestamp") is not None
        }

# Instance globale
scan_storage = None

def get_scan_storage(data_dir: Path) -> ScanStorage:
    """Factory pour obtenir l'instance du storage"""
    global scan_storage
    if scan_storage is None:
        scan_storage = ScanStorage(data_dir)
    return scan_storage