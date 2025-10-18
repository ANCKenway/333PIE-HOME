"""
API endpoints pour le scanner réseau avancé
Intégration avec le système de scan et d'identification
"""

import json
import logging
from typing import Dict, Any, Optional
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.network import NetworkScanner, DeviceIdentifier, MacVendorAPI

logger = logging.getLogger(__name__)

class NetworkAPI:
    def __init__(self):
        self.scanner = NetworkScanner()
        self.device_identifier = DeviceIdentifier()
        self.mac_vendor_api = MacVendorAPI()
    
    def scan_network(self, network: str = None, include_ports: bool = True) -> Dict[str, Any]:
        """
        Endpoint pour scanner le réseau
        """
        try:
            logger.info(f"Début du scan réseau: network={network}, include_ports={include_ports}")
            
            # Effectuer le scan
            scan_results = self.scanner.full_network_scan(network, include_ports)
            
            # Enrichir avec l'identification des appareils
            if 'devices' in scan_results:
                enriched_devices = []
                
                for device in scan_results['devices']:
                    # Identifier le type d'appareil
                    device_details = self.device_identifier.get_device_details(device)
                    enriched_devices.append(device_details)
                
                scan_results['devices'] = enriched_devices
                
                # Ajouter des statistiques enrichies
                analysis = self.device_identifier.analyze_multiple_devices(scan_results['devices'])
                scan_results['device_analysis'] = analysis['statistics']
            
            return {
                'success': True,
                'data': scan_results,
                'message': f"Scan terminé: {len(scan_results.get('devices', []))} appareils trouvés"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du scan réseau: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors du scan réseau"
            }
    
    def quick_scan(self, network: str = None) -> Dict[str, Any]:
        """
        Endpoint pour un scan rapide (sans ports)
        """
        return self.scan_network(network, include_ports=False)
    
    def get_device_info(self, identifier: str, identifier_type: str = 'ip') -> Dict[str, Any]:
        """
        Récupérer les informations détaillées d'un appareil
        identifier_type: 'ip' ou 'mac'
        """
        try:
            device = None
            
            if identifier_type == 'ip':
                device = self.scanner.get_device_by_ip(identifier)
            elif identifier_type == 'mac':
                device = self.scanner.get_device_by_mac(identifier)
            
            if not device:
                return {
                    'success': False,
                    'message': f"Appareil non trouvé: {identifier}",
                    'error': 'device_not_found'
                }
            
            # Enrichir avec l'identification
            device_details = self.device_identifier.get_device_details(device)
            
            return {
                'success': True,
                'data': device_details,
                'message': f"Informations récupérées pour {identifier}"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos appareil: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la récupération des informations"
            }
    
    def get_vendor_info(self, mac_address: str) -> Dict[str, Any]:
        """
        Récupérer les informations du fabricant pour une adresse MAC
        """
        try:
            vendor_info = self.mac_vendor_api.get_vendor_info(mac_address)
            
            return {
                'success': True,
                'data': vendor_info,
                'message': f"Informations fabricant récupérées pour {mac_address}"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos fabricant: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la récupération des informations fabricant"
            }
    
    def get_network_interfaces(self) -> Dict[str, Any]:
        """
        Récupérer les interfaces réseau disponibles
        """
        try:
            interfaces = self.scanner.get_network_interfaces()
            
            return {
                'success': True,
                'data': {
                    'interfaces': interfaces,
                    'default_network': self.scanner.get_default_network()
                },
                'message': f"{len(interfaces)} interfaces trouvées"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des interfaces: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la récupération des interfaces"
            }
    
    def get_scan_history(self) -> Dict[str, Any]:
        """
        Récupérer l'historique des scans
        """
        try:
            scan_data = self.scanner.scan_results
            
            if not scan_data:
                return {
                    'success': True,
                    'data': None,
                    'message': "Aucun scan récent disponible"
                }
            
            return {
                'success': True,
                'data': {
                    'last_scan': scan_data,
                    'scan_time': self.scanner.last_scan_time
                },
                'message': "Historique récupéré"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la récupération de l'historique"
            }
    
    def export_scan_results(self, format: str = 'json') -> Dict[str, Any]:
        """
        Exporter les résultats du scan
        """
        try:
            if not self.scanner.scan_results:
                return {
                    'success': False,
                    'message': "Aucun résultat de scan à exporter",
                    'error': 'no_scan_data'
                }
            
            exported_data = self.scanner.export_results(format)
            
            return {
                'success': True,
                'data': {
                    'format': format,
                    'content': exported_data,
                    'timestamp': self.scanner.last_scan_time
                },
                'message': f"Résultats exportés en format {format}"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de l'export"
            }
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Vider les caches (vendor cache, etc.)
        """
        try:
            self.mac_vendor_api.clear_cache()
            
            return {
                'success': True,
                'message': "Cache vidé avec succès"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage du cache: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors du vidage du cache"
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Récupérer les statistiques du cache
        """
        try:
            cache_stats = self.mac_vendor_api.get_cache_stats()
            
            return {
                'success': True,
                'data': cache_stats,
                'message': "Statistiques du cache récupérées"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': "Erreur lors de la récupération des statistiques"
            }

# Instance globale pour l'API
network_api = NetworkAPI()