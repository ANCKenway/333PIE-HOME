"""
🏠 333HOME - Gestionnaire de Base de Données JSON
Persistance des données avec gestion d'erreurs
"""

import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import DEVICES_FILE, SCAN_HISTORY_FILE, SYSTEM_LOGS_FILE
from core.models import Device, ScanResult, SystemInfo, DeviceAction

class JSONDatabase:
    """Gestionnaire de données JSON thread-safe"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._ensure_files_exist()
        print("✅ Base de données JSON initialisée")
    
    def _ensure_files_exist(self):
        """Créer les fichiers JSON s'ils n'existent pas"""
        default_data = {
            DEVICES_FILE: {"devices": [], "last_updated": None},
            SCAN_HISTORY_FILE: {"scans": [], "last_scan": None},
            SYSTEM_LOGS_FILE: {"logs": [], "last_log": None}
        }
        
        for file_path, default in default_data.items():
            if not file_path.exists():
                self._write_json(file_path, default)
    
    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        """Lecture sécurisée d'un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Erreur lecture {file_path.name}: {e}")
            return {}
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Écriture sécurisée d'un fichier JSON"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarde atomique
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            temp_file.replace(file_path)
            return True
            
        except Exception as e:
            print(f"❌ Erreur écriture {file_path.name}: {e}")
            return False
    
    # ===== GESTION DES APPAREILS =====
    
    def get_devices(self) -> List[Device]:
        """Récupérer tous les appareils"""
        with self._lock:
            data = self._read_json(DEVICES_FILE)
            devices = []
            
            for device_data in data.get('devices', []):
                try:
                    device = Device.from_dict(device_data)
                    devices.append(device)
                except Exception as e:
                    print(f"⚠️ Erreur chargement appareil: {e}")
            
            return devices
    
    def save_devices(self, devices: List[Device]) -> bool:
        """Sauvegarder la liste des appareils"""
        with self._lock:
            data = {
                "devices": [device.to_dict() for device in devices],
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total_count": len(devices)
            }
            return self._write_json(DEVICES_FILE, data)
    
    def add_device(self, device: Device) -> bool:
        """Ajouter un nouvel appareil"""
        devices = self.get_devices()
        
        # Vérifier si l'appareil existe déjà (par IP)
        for existing in devices:
            if existing.ip == device.ip:
                # Mettre à jour l'appareil existant
                existing.mac = device.mac or existing.mac
                existing.hostname = device.hostname or existing.hostname
                existing.vendor = device.vendor or existing.vendor
                existing.device_type = device.device_type
                existing.status = device.status
                existing.update_seen()
                return self.save_devices(devices)
        
        # Nouvel appareil
        devices.append(device)
        return self.save_devices(devices)
    
    def get_device_by_ip(self, ip: str) -> Optional[Device]:
        """Récupérer un appareil par IP"""
        devices = self.get_devices()
        for device in devices:
            if device.ip == ip:
                return device
        return None
    
    def get_favorite_devices(self) -> List[Device]:
        """Récupérer les appareils favoris"""
        devices = self.get_devices()
        return [device for device in devices if device.is_favorite]
    
    def mark_device_favorite(self, ip: str, nickname: str = "", description: str = "") -> bool:
        """Marquer un appareil comme favori"""
        devices = self.get_devices()
        
        for device in devices:
            if device.ip == ip:
                device.mark_as_favorite(nickname, description)
                return self.save_devices(devices)
        
        return False
    
    def remove_device(self, ip: str) -> bool:
        """Supprimer un appareil"""
        devices = self.get_devices()
        devices = [device for device in devices if device.ip != ip]
        return self.save_devices(devices)
    
    # ===== HISTORIQUE DES SCANS =====
    
    def save_scan_result(self, scan_result: ScanResult) -> bool:
        """Sauvegarder un résultat de scan"""
        with self._lock:
            data = self._read_json(SCAN_HISTORY_FILE)
            
            scans = data.get('scans', [])
            scans.append(scan_result.to_dict())
            
            # Garder seulement les 50 derniers scans
            if len(scans) > 50:
                scans = scans[-50:]
            
            data = {
                "scans": scans,
                "last_scan": scan_result.timestamp,
                "total_scans": len(scans)
            }
            
            return self._write_json(SCAN_HISTORY_FILE, data)
    
    def get_scan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupérer l'historique des scans"""
        with self._lock:
            data = self._read_json(SCAN_HISTORY_FILE)
            scans = data.get('scans', [])
            return scans[-limit:] if limit else scans
    
    def get_last_scan(self) -> Optional[Dict[str, Any]]:
        """Récupérer le dernier scan"""
        history = self.get_scan_history(1)
        return history[0] if history else None
    
    # ===== LOGS SYSTÈME =====
    
    def log_system_info(self, system_info: SystemInfo) -> bool:
        """Enregistrer des informations système"""
        with self._lock:
            data = self._read_json(SYSTEM_LOGS_FILE)
            
            logs = data.get('logs', [])
            logs.append(system_info.to_dict())
            
            # Garder seulement les 1000 derniers logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            data = {
                "logs": logs,
                "last_log": system_info.timestamp,
                "total_logs": len(logs)
            }
            
            return self._write_json(SYSTEM_LOGS_FILE, data)
    
    def get_system_logs(self, limit: int = 24) -> List[Dict[str, Any]]:
        """Récupérer les logs système récents"""
        with self._lock:
            data = self._read_json(SYSTEM_LOGS_FILE)
            logs = data.get('logs', [])
            return logs[-limit:] if limit else logs
    
    def log_device_action(self, action: DeviceAction) -> bool:
        """Enregistrer une action sur un appareil"""
        # Pour l'instant, on peut étendre les logs système
        # ou créer un fichier séparé si nécessaire
        return True

# Instance globale
db = JSONDatabase()

print("✅ Gestionnaire de données JSON chargé")