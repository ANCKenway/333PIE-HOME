"""
📱 333HOME - Device Manager
Gestion des appareils et de leur stockage

Version 3.0 - Format de données moderne et optimisé
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import shutil

from src.core import get_logger, settings
from src.shared import DeviceError, StorageError, generate_id
from .storage import migrate_old_device_format


logger = get_logger(__name__)


class DeviceManager:
    """
    Gestionnaire des appareils (v3.0)
    
    Fonctionnalités:
    - Stockage au format JSON moderne
    - Migration automatique de l'ancien format
    - Backup automatique avant migration
    - Opérations CRUD complètes
    """
    
    STORAGE_VERSION = "3.0"
    
    def __init__(self):
        self.devices_file = settings.data_dir / "devices.json"
        self._ensure_storage_ready()
        logger.info("📱 DeviceManager v3.0 initialisé")
    
    def _ensure_storage_ready(self):
        """S'assurer que le fichier de stockage est prêt"""
        if not self.devices_file.exists():
            self._create_empty_storage()
            logger.info(f"📝 Nouveau fichier créé: {self.devices_file}")
        else:
            # Vérifier si migration nécessaire
            self._check_and_migrate()
    
    def _create_empty_storage(self):
        """Créer un fichier de stockage vide au nouveau format"""
        empty_storage = {
            "version": self.STORAGE_VERSION,
            "updated_at": datetime.now().isoformat(),
            "devices": []
        }
        self._save_storage(empty_storage)
    
    def _check_and_migrate(self):
        """Vérifier et migrer si nécessaire l'ancien format"""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Détecter le format
            if isinstance(data, list):
                # Ancien format: liste directe
                logger.warning("⚠️ Ancien format détecté (liste directe), migration...")
                self._migrate_from_list(data)
            elif isinstance(data, dict):
                if 'version' not in data or data.get('version') != self.STORAGE_VERSION:
                    # Ancien format: dict sans version ou vieille version
                    logger.warning(f"⚠️ Ancien format détecté (v{data.get('version', '?')}), migration...")
                    
                    # Backup avant migration
                    backup_file = self.devices_file.with_suffix('.json.backup')
                    shutil.copy2(self.devices_file, backup_file)
                    logger.info(f"💾 Backup créé: {backup_file}")
                    
                    # Migrer
                    old_devices = data.get('devices', [])
                    self._migrate_from_list(old_devices)
                else:
                    logger.debug(f"✅ Format v{self.STORAGE_VERSION} détecté, OK")
        except Exception as e:
            logger.error(f"❌ Erreur vérification format: {e}")
            # En cas d'erreur, créer un nouveau fichier
            self._create_empty_storage()
    
    def _migrate_from_list(self, old_devices: List[Dict]):
        """Migrer une liste d'appareils de l'ancien format vers le nouveau"""
        migrated_devices = []
        
        for old_device in old_devices:
            try:
                new_device = migrate_old_device_format(old_device)
                migrated_devices.append(new_device)
            except Exception as e:
                logger.error(f"❌ Erreur migration appareil {old_device.get('name', '?')}: {e}")
        
        # Sauvegarder au nouveau format
        new_storage = {
            "version": self.STORAGE_VERSION,
            "updated_at": datetime.now().isoformat(),
            "devices": migrated_devices
        }
        self._save_storage(new_storage)
        
        logger.info(f"✅ Migration terminée: {len(migrated_devices)} appareils migrés")
    
    def _load_storage(self) -> Dict:
        """Charger le fichier de stockage complet"""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erreur chargement storage: {e}")
            raise StorageError(f"Impossible de charger le storage: {e}")
    
    def _save_storage(self, storage: Dict):
        """Sauvegarder le fichier de storage complet"""
        try:
            storage['updated_at'] = datetime.now().isoformat()
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(storage, f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Storage sauvegardé")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde storage: {e}")
            raise StorageError(f"Impossible de sauvegarder le storage: {e}")
    
    def _load_devices(self) -> List[Dict]:
        """Charger uniquement la liste des appareils"""
        storage = self._load_storage()
        devices = storage.get('devices', [])
        logger.debug(f"📖 {len(devices)} appareils chargés")
        return devices
    
    def _save_devices(self, devices: List[Dict]):
        """Sauvegarder la liste des appareils"""
        storage = self._load_storage()
        storage['devices'] = devices
        self._save_storage(storage)
    
    def _generate_device_id(self, ip: str, mac: Optional[str] = None) -> str:
        """Générer un ID unique pour un appareil"""
        key = f"{ip}_{mac}" if mac else ip
        return generate_id(key)
    
    def get_all_devices(self) -> List[Dict]:
        """Récupérer tous les appareils"""
        return self._load_devices()
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Récupérer un appareil par son ID"""
        devices = self._load_devices()
        for device in devices:
            if device.get('id') == device_id:
                return device
        return None
    
    def create_device(self, device_data: Dict) -> Dict:
        """Créer un nouvel appareil"""
        devices = self._load_devices()
        
        # Générer un ID
        device_id = self._generate_device_id(
            device_data.get('ip'),
            device_data.get('mac')
        )
        
        # Vérifier si existe déjà
        if any(d.get('id') == device_id for d in devices):
            raise DeviceError(f"Appareil avec cet ID existe déjà: {device_id}")
        
        # Créer l'appareil
        device = {
            'id': device_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            **device_data
        }
        
        devices.append(device)
        self._save_devices(devices)
        
        logger.info(f"✅ Appareil créé: {device.get('name')} ({device_id})")
        return device
    
    def update_device(self, device_id: str, update_data: Dict) -> Dict:
        """Mettre à jour un appareil"""
        devices = self._load_devices()
        
        for i, device in enumerate(devices):
            if device.get('id') == device_id:
                # ✅ Fusionner metadata au lieu de l'écraser
                if 'metadata' in update_data:
                    existing_metadata = device.get('metadata', {})
                    new_metadata = update_data.pop('metadata')
                    # Merge: nouvelles clés ajoutées, anciennes préservées
                    existing_metadata.update(new_metadata)
                    device['metadata'] = existing_metadata
                
                # Mettre à jour les autres champs fournis
                device.update(update_data)
                device['updated_at'] = datetime.now().isoformat()
                devices[i] = device
                self._save_devices(devices)
                
                logger.info(f"✅ Appareil mis à jour: {device_id}")
                return device
        
        raise DeviceError(f"Appareil non trouvé: {device_id}")
    
    def delete_device(self, device_id: str) -> bool:
        """Supprimer un appareil"""
        devices = self._load_devices()
        initial_count = len(devices)
        
        devices = [d for d in devices if d.get('id') != device_id]
        
        if len(devices) == initial_count:
            raise DeviceError(f"Appareil non trouvé: {device_id}")
        
        self._save_devices(devices)
        logger.info(f"🗑️ Appareil supprimé: {device_id}")
        return True
    
    def get_device_by_mac(self, mac: str) -> Optional[Dict]:
        """Récupérer un appareil par son adresse MAC"""
        devices = self._load_devices()
        for device in devices:
            if device.get('mac') == mac:
                return device
        return None
    
    def get_device_by_ip(self, ip: str) -> Optional[Dict]:
        """Récupérer un appareil par son IP"""
        devices = self._load_devices()
        for device in devices:
            if device.get('ip') == ip:
                return device
        return None
