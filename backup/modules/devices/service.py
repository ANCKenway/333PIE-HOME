"""
🔧 Service de gestion des appareils
"""
from typing import List, Optional
import asyncio
from pathlib import Path
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.models import Computer, DeviceStatus, APIResponse
from shared.utils import setup_logging, ping_host, validate_ip, validate_mac, format_mac, load_json_file, save_json_file
from core.config import get_settings

class DeviceService:
    """Service de gestion des appareils"""
    
    def __init__(self):
        self.logger = setup_logging(self.__class__.__name__)
        self.settings = get_settings()
        self.config_file = Path(self.settings.config_dir) / "devices.json"
        self._devices = []
        self._load_devices()
    
    def _load_devices(self) -> None:
        """Charge la configuration des appareils"""
        try:
            data = load_json_file(self.config_file)
            computers = data.get('computers', [])
            
            self._devices = [
                Computer(**device) for device in computers
            ]
            
            self.logger.info(f"Chargé {len(self._devices)} appareils")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des appareils: {e}")
            self._devices = []
    
    def _save_devices(self) -> bool:
        """Sauvegarde la configuration des appareils"""
        try:
            data = {
                'computers': [device.dict() for device in self._devices]
            }
            
            success = save_json_file(data, self.config_file)
            if success:
                self.logger.info("Configuration sauvegardée")
            return success
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    async def list_devices(self) -> List[Computer]:
        """Liste tous les appareils configurés"""
        # Mettre à jour le statut en temps réel
        tasks = []
        for device in self._devices:
            tasks.append(self._update_device_status(device))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return self._devices.copy()
    
    async def _update_device_status(self, device: Computer) -> None:
        """Met à jour le statut d'un appareil"""
        try:
            is_online = await ping_host(device.ip, self.settings.ping_timeout)
            device.status = DeviceStatus.ONLINE if is_online else DeviceStatus.OFFLINE
        except Exception as e:
            self.logger.warning(f"Erreur lors du ping de {device.ip}: {e}")
            device.status = DeviceStatus.UNKNOWN
    
    async def get_device(self, device_id: str) -> Optional[Computer]:
        """Récupère un appareil par son ID (nom ou IP)"""
        for device in self._devices:
            if device.name == device_id or device.ip == device_id:
                await self._update_device_status(device)
                return device
        return None
    
    async def add_device(self, device_data: dict) -> APIResponse:
        """Ajoute un nouvel appareil"""
        try:
            # Validation
            name = device_data.get('name', '').strip()
            ip = device_data.get('ip', '').strip()
            mac = device_data.get('mac', '').strip()
            
            if not name:
                return APIResponse(success=False, error="Le nom est obligatoire")
            
            if not validate_ip(ip):
                return APIResponse(success=False, error="Adresse IP invalide")
            
            if mac and not validate_mac(mac):
                return APIResponse(success=False, error="Adresse MAC invalide")
            
            # Vérifier les doublons
            for device in self._devices:
                if device.name == name:
                    return APIResponse(success=False, error="Un appareil avec ce nom existe déjà")
                if device.ip == ip:
                    return APIResponse(success=False, error="Un appareil avec cette IP existe déjà")
            
            # Créer l'appareil
            device = Computer(
                name=name,
                ip=ip,
                mac=format_mac(mac) if mac else None,
                description=device_data.get('description', ''),
                wake_on_lan=device_data.get('wake_on_lan', True)
            )
            
            # Tester la connectivité
            await self._update_device_status(device)
            
            # Ajouter et sauvegarder
            self._devices.append(device)
            
            if self._save_devices():
                self.logger.info(f"Appareil ajouté: {name} ({ip})")
                return APIResponse(
                    success=True,
                    message=f"Appareil '{name}' ajouté avec succès",
                    data=device.dict()
                )
            else:
                self._devices.remove(device)  # Rollback
                return APIResponse(success=False, error="Erreur lors de la sauvegarde")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout d'appareil: {e}")
            return APIResponse(success=False, error=str(e))
    
    async def remove_device(self, device_id: str) -> APIResponse:
        """Supprime un appareil"""
        try:
            device_to_remove = None
            
            for device in self._devices:
                if device.name == device_id or device.ip == device_id:
                    device_to_remove = device
                    break
            
            if not device_to_remove:
                return APIResponse(success=False, error="Appareil non trouvé")
            
            self._devices.remove(device_to_remove)
            
            if self._save_devices():
                self.logger.info(f"Appareil supprimé: {device_to_remove.name}")
                return APIResponse(
                    success=True,
                    message=f"Appareil '{device_to_remove.name}' supprimé"
                )
            else:
                self._devices.append(device_to_remove)  # Rollback
                return APIResponse(success=False, error="Erreur lors de la sauvegarde")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression: {e}")
            return APIResponse(success=False, error=str(e))
    
    async def wake_device(self, mac_address: str) -> APIResponse:
        """Envoie un paquet Wake-on-LAN"""
        try:
            if not validate_mac(mac_address):
                return APIResponse(success=False, error="Adresse MAC invalide")
            
            mac_formatted = format_mac(mac_address)
            
            # Trouver l'appareil correspondant
            device = None
            for d in self._devices:
                if d.mac and format_mac(d.mac) == mac_formatted:
                    device = d
                    break
            
            if not device:
                return APIResponse(success=False, error="Appareil non trouvé")
            
            if not device.wake_on_lan:
                return APIResponse(success=False, error="Wake-on-LAN désactivé pour cet appareil")
            
            # Envoyer le paquet magique
            success = await self._send_wake_on_lan_packet(mac_formatted)
            
            if success:
                self.logger.info(f"Wake-on-LAN envoyé vers {device.name} ({mac_formatted})")
                return APIResponse(
                    success=True,
                    message=f"Commande de réveil envoyée à '{device.name}'"
                )
            else:
                return APIResponse(success=False, error="Échec de l'envoi du paquet Wake-on-LAN")
                
        except Exception as e:
            self.logger.error(f"Erreur Wake-on-LAN: {e}")
            return APIResponse(success=False, error=str(e))
    
    async def _send_wake_on_lan_packet(self, mac_address: str) -> bool:
        """Envoie le paquet magique Wake-on-LAN"""
        try:
            import socket
            
            # Supprimer les séparateurs et convertir en bytes
            mac_clean = mac_address.replace(':', '')
            mac_bytes = bytes.fromhex(mac_clean)
            
            # Construire le paquet magique (6 x 0xFF + 16 x MAC)
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            
            # Envoyer en broadcast UDP sur port 9
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('255.255.255.255', 9))
            sock.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du paquet WOL: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Statistiques des appareils"""
        total = len(self._devices)
        online = sum(1 for d in self._devices if d.status == DeviceStatus.ONLINE)
        offline = sum(1 for d in self._devices if d.status == DeviceStatus.OFFLINE)
        
        return {
            'total': total,
            'online': online,
            'offline': offline,
            'unknown': total - online - offline
        }