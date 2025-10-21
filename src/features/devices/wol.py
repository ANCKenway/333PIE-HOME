"""
⚡ 333HOME - Wake-on-LAN Service
Service pour réveiller les appareils via Wake-on-LAN
"""

import socket
import struct
from typing import Optional

from src.core import get_logger
from src.shared import NetworkError, is_valid_mac


logger = get_logger(__name__)


class WakeOnLanService:
    """Service Wake-on-LAN"""
    
    @staticmethod
    def _create_magic_packet(mac_address: str) -> bytes:
        """
        Créer le magic packet WOL
        
        Format: 6 bytes FF + 16 répétitions de l'adresse MAC
        """
        # Nettoyer l'adresse MAC
        mac_clean = mac_address.replace(':', '').replace('-', '').upper()
        
        if len(mac_clean) != 12:
            raise NetworkError(f"Adresse MAC invalide: {mac_address}")
        
        # Convertir en bytes
        mac_bytes = bytes.fromhex(mac_clean)
        
        # Créer le magic packet
        magic_packet = b'\xFF' * 6 + mac_bytes * 16
        
        return magic_packet
    
    @staticmethod
    async def wake(
        mac: str,
        broadcast: str = "255.255.255.255",
        port: int = 9
    ) -> bool:
        """
        Envoyer un magic packet Wake-on-LAN
        
        Args:
            mac: Adresse MAC de l'appareil
            broadcast: Adresse broadcast
            port: Port WOL (généralement 7 ou 9)
            
        Returns:
            True si le packet a été envoyé avec succès
        """
        try:
            # Valider la MAC
            if not is_valid_mac(mac):
                raise NetworkError(f"Adresse MAC invalide: {mac}")
            
            # Créer le magic packet
            magic_packet = WakeOnLanService._create_magic_packet(mac)
            
            # Créer un socket UDP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(magic_packet, (broadcast, port))
            
            logger.info(f"⚡ Magic packet envoyé à {mac} ({broadcast}:{port})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur Wake-on-LAN pour {mac}: {e}")
            raise NetworkError(f"Échec Wake-on-LAN: {e}")
