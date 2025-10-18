"""
🏠 Device Manager - Gestion des appareils
Séparation des responsabilités selon RULES.md
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DeviceManager:
    """Gestionnaire des appareils configurés"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.devices_file = data_dir / "devices.json"
        self._ensure_data_structure()
    
    def _ensure_data_structure(self):
        """Assurer que la structure de données existe"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.devices_file.exists():
            self._create_empty_devices_file()
    
    def _create_empty_devices_file(self):
        """Créer un fichier devices.json vide mais valide"""
        empty_structure = {
            "devices": [],
            "last_updated": None,
            "version": "1.0"
        }
        self.save_devices(empty_structure)
        logger.info("Fichier devices.json créé")
    
    def load_devices(self) -> List[Dict]:
        """Charger la liste des appareils depuis le fichier JSON"""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                devices = data.get("devices", [])
                logger.debug(f"Chargé {len(devices)} appareils")
                return devices
        except FileNotFoundError:
            logger.warning("Fichier devices.json non trouvé")
            self._create_empty_devices_file()
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing devices.json: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur lecture devices.json: {e}")
            return []
    
    def save_devices(self, data: Dict):
        """Sauvegarder les données des appareils"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("Appareils sauvegardés")
        except Exception as e:
            logger.error(f"Erreur sauvegarde devices.json: {e}")
            raise
    
    def add_device(self, device: Dict) -> bool:
        """Ajouter un nouvel appareil"""
        try:
            data = self._load_full_data()
            
            # Vérifier les doublons par IP ou MAC
            existing_ips = [d.get('ip') for d in data['devices']]
            existing_macs = [d.get('mac') for d in data['devices'] if d.get('mac')]
            
            if device.get('ip') in existing_ips:
                logger.warning(f"Appareil avec IP {device['ip']} déjà existant")
                return False
            
            if device.get('mac') and device['mac'] in existing_macs:
                logger.warning(f"Appareil avec MAC {device['mac']} déjà existant")
                return False
            
            # Ajouter l'appareil
            data['devices'].append(device)
            self.save_devices(data)
            logger.info(f"Appareil ajouté: {device.get('name', 'Sans nom')}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout appareil: {e}")
            return False
    
    def update_device(self, device_id: str, updates: Dict) -> bool:
        """Mettre à jour un appareil (par IP ou MAC)"""
        try:
            data = self._load_full_data()
            
            for i, device in enumerate(data['devices']):
                if device.get('ip') == device_id or device.get('mac') == device_id:
                    data['devices'][i].update(updates)
                    self.save_devices(data)
                    logger.info(f"Appareil {device_id} mis à jour")
                    return True
            
            logger.warning(f"Appareil {device_id} non trouvé")
            return False
            
        except Exception as e:
            logger.error(f"Erreur mise à jour appareil: {e}")
            return False
    
    def remove_device(self, device_id: str) -> bool:
        """Supprimer un appareil (par IP ou MAC)"""
        try:
            data = self._load_full_data()
            original_count = len(data['devices'])
            
            data['devices'] = [
                d for d in data['devices'] 
                if d.get('ip') != device_id and d.get('mac') != device_id
            ]
            
            if len(data['devices']) < original_count:
                self.save_devices(data)
                logger.info(f"Appareil {device_id} supprimé")
                return True
            else:
                logger.warning(f"Appareil {device_id} non trouvé")
                return False
                
        except Exception as e:
            logger.error(f"Erreur suppression appareil: {e}")
            return False
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """Obtenir un appareil par son IP ou MAC"""
        devices = self.load_devices()
        for device in devices:
            if device.get('ip') == device_id or device.get('mac') == device_id:
                return device
        return None
    
    def _load_full_data(self) -> Dict:
        """Charger toute la structure JSON"""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"devices": [], "last_updated": None, "version": "1.0"}
        except Exception as e:
            logger.error(f"Erreur chargement complet: {e}")
            return {"devices": [], "last_updated": None, "version": "1.0"}
    
    def get_stats(self) -> Dict:
        """Statistiques des appareils"""
        devices = self.load_devices()
        stats = {
            'total_devices': len(devices),
            'by_type': {},
            'with_wake_on_lan': 0,
            'with_mac': 0,
            'with_hostname': 0
        }
        
        for device in devices:
            # Par type
            device_type = device.get('type', 'Unknown')
            stats['by_type'][device_type] = stats['by_type'].get(device_type, 0) + 1
            
            # Fonctionnalités
            if device.get('wake_on_lan'):
                stats['with_wake_on_lan'] += 1
            if device.get('mac'):
                stats['with_mac'] += 1
            if device.get('hostname'):
                stats['with_hostname'] += 1
        
        return stats