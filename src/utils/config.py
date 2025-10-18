"""
Utilitaires de configuration et fichiers
Gestion centralisée des configs et du stockage
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class ConfigManager:
    """Gestionnaire centralisé des configurations"""
    
    def __init__(self, base_path: str = "config"):
        self.base_path = base_path
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Crée le dossier config s'il n'existe pas"""
        os.makedirs(self.base_path, exist_ok=True)
    
    def load_json(self, filename: str, default: Any = None) -> Any:
        """Charge un fichier JSON avec fallback"""
        filepath = os.path.join(self.base_path, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur chargement {filename}: {e}")
        
        return default or {}
    
    def save_json(self, filename: str, data: Any) -> bool:
        """Sauvegarde des données en JSON"""
        filepath = os.path.join(self.base_path, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde {filename}: {e}")
            return False
    
    def backup_config(self, filename: str) -> bool:
        """Crée une sauvegarde de configuration"""
        source = os.path.join(self.base_path, filename)
        if not os.path.exists(source):
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filename}.backup_{timestamp}"
        backup_path = os.path.join(self.base_path, backup_name)
        
        try:
            import shutil
            shutil.copy2(source, backup_path)
            return True
        except Exception as e:
            print(f"Erreur backup {filename}: {e}")
            return False

# Instance globale
config = ConfigManager()

def load_devices() -> Dict:
    """Charge la configuration des appareils"""
    return config.load_json("devices.json", {
        "computers": [
            {
                "name": "PC Bureau",
                "hostname": "DESKTOP-PC",
                "mac": "00:11:22:33:44:55",
                "ip": "192.168.1.100"
            }
        ]
    })

def save_devices(devices_data: Dict) -> bool:
    """Sauvegarde la configuration des appareils"""
    return config.save_json("devices.json", devices_data)

def load_network_cache() -> Dict:
    """Charge le cache réseau"""
    return config.load_json("network_cache.json", {})

def save_network_cache(cache_data: Dict) -> bool:
    """Sauvegarde le cache réseau"""
    return config.save_json("network_cache.json", cache_data)