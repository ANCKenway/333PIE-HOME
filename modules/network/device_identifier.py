"""
Identificateur d'appareils avancé
Analyse les informations réseau pour déterminer le type d'appareil
"""

import re
import logging
from typing import Dict, Any, Optional, List
from .mac_vendor import MacVendorAPI

logger = logging.getLogger(__name__)

class DeviceIdentifier:
    def __init__(self):
        self.mac_vendor_api = MacVendorAPI()
        
        # Patterns pour identifier les types d'appareils
        self.device_patterns = {
            'smartphone': {
                'hostnames': [
                    r'.*iphone.*', r'.*android.*', r'.*samsung.*', r'.*huawei.*',
                    r'.*xiaomi.*', r'.*oneplus.*', r'.*pixel.*', r'.*galaxy.*'
                ],
                'vendors': [
                    'Apple', 'Samsung', 'Huawei', 'Xiaomi', 'OnePlus', 'Google',
                    'LG Electronics', 'Sony', 'HTC', 'Motorola'
                ],
                'services': ['5353']  # Bonjour/mDNS commun sur mobiles
            },
            'computer': {
                'hostnames': [
                    r'.*desktop.*', r'.*laptop.*', r'.*pc.*', r'.*workstation.*',
                    r'.*-pc$', r'.*win.*', r'.*ubuntu.*', r'.*fedora.*'
                ],
                'vendors': [
                    'Dell Inc.', 'Hewlett Packard', 'Lenovo', 'ASUSTek',
                    'MSI', 'Gigabyte', 'Intel Corporate'
                ],
                'services': ['135', '139', '445', '3389']  # Services Windows/SMB
            },
            'tablet': {
                'hostnames': [r'.*ipad.*', r'.*tablet.*'],
                'vendors': ['Apple', 'Samsung'],
                'services': ['5353']
            },
            'router': {
                'hostnames': [
                    r'.*router.*', r'.*gateway.*', r'.*livebox.*', r'.*freebox.*',
                    r'.*bbox.*', r'.*neufbox.*'
                ],
                'vendors': [
                    'Netgear', 'TP-Link', 'D-Link', 'Linksys', 'ASUS',
                    'Sagemcom', 'Technicolor', 'Orange'
                ],
                'services': ['80', '443', '8080', '23', '22']
            },
            'smart_tv': {
                'hostnames': [r'.*tv.*', r'.*samsung.*tv.*', r'.*lg.*tv.*'],
                'vendors': ['Samsung', 'LG Electronics', 'Sony', 'Philips'],
                'services': ['8080', '9080']
            },
            'iot': {
                'hostnames': [
                    r'.*esp.*', r'.*arduino.*', r'.*sensor.*', r'.*smart.*',
                    r'.*home.*', r'.*bulb.*', r'.*camera.*'
                ],
                'vendors': [
                    'Espressif', 'Raspberry Pi Foundation', 'Amazon Technologies',
                    'Nest Labs', 'Philips Lighting'
                ],
                'services': ['80', '443', '1883', '8883']  # HTTP + MQTT
            },
            'raspberry_pi': {
                'hostnames': [r'.*raspberry.*', r'.*rpi.*', r'.*pi.*'],
                'vendors': ['Raspberry Pi Foundation'],
                'services': ['22', '80', '443']
            },
            'printer': {
                'hostnames': [r'.*printer.*', r'.*print.*', r'.*hp.*', r'.*canon.*'],
                'vendors': ['Hewlett Packard', 'Canon', 'Epson', 'Brother'],
                'services': ['631', '9100', '515']  # IPP, JetDirect, LPD
            }
        }
    
    def _match_hostname_patterns(self, hostname: str, patterns: List[str]) -> bool:
        """Vérifier si le hostname correspond aux patterns"""
        if not hostname:
            return False
        
        hostname_lower = hostname.lower()
        for pattern in patterns:
            if re.match(pattern, hostname_lower):
                return True
        return False
    
    def _match_vendor_patterns(self, vendor: str, vendors: List[str]) -> bool:
        """Vérifier si le vendor correspond aux patterns"""
        if not vendor:
            return False
        
        for vendor_pattern in vendors:
            if vendor_pattern.lower() in vendor.lower():
                return True
        return False
    
    def _match_service_patterns(self, services: List[str], service_patterns: List[str]) -> bool:
        """Vérifier si les services correspondent aux patterns"""
        if not services:
            return False
        
        for service in services:
            if str(service) in service_patterns:
                return True
        return False
    
    def _calculate_device_score(self, device_info: Dict[str, Any], device_type: str) -> float:
        """Calculer un score de confiance pour un type d'appareil"""
        patterns = self.device_patterns.get(device_type, {})
        score = 0.0
        max_score = 0.0
        
        # Score hostname (poids: 40%)
        hostname_weight = 0.4
        max_score += hostname_weight
        if self._match_hostname_patterns(device_info.get('hostname', ''), patterns.get('hostnames', [])):
            score += hostname_weight
        
        # Score vendor (poids: 35%)
        vendor_weight = 0.35
        max_score += vendor_weight
        vendor_info = device_info.get('vendor_info', {})
        if self._match_vendor_patterns(vendor_info.get('vendor', ''), patterns.get('vendors', [])):
            score += vendor_weight
        
        # Score services (poids: 25%)
        service_weight = 0.25
        max_score += service_weight
        if self._match_service_patterns(device_info.get('services', []), patterns.get('services', [])):
            score += service_weight
        
        return score / max_score if max_score > 0 else 0.0
    
    def identify_device_type(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identifier le type d'appareil basé sur les informations disponibles
        """
        try:
            # Enrichir avec les infos vendor
            mac_address = device_info.get('mac_address')
            if mac_address and 'vendor_info' not in device_info:
                device_info['vendor_info'] = self.mac_vendor_api.get_vendor_info(mac_address)
            
            # Calculer les scores pour chaque type d'appareil
            type_scores = {}
            for device_type in self.device_patterns.keys():
                score = self._calculate_device_score(device_info, device_type)
                if score > 0:
                    type_scores[device_type] = score
            
            # Déterminer le type le plus probable
            if type_scores:
                best_type = max(type_scores, key=type_scores.get)
                best_score = type_scores[best_type]
                
                # Seuil de confiance minimum
                confidence_threshold = 0.3
                if best_score >= confidence_threshold:
                    confidence = 'high' if best_score >= 0.7 else 'medium'
                    return {
                        'device_type': best_type,
                        'confidence': confidence,
                        'score': best_score,
                        'all_scores': type_scores,
                        'vendor_info': device_info.get('vendor_info', {})
                    }
            
            # Valeur par défaut si aucune identification fiable
            return {
                'device_type': 'unknown',
                'confidence': 'low',
                'score': 0.0,
                'all_scores': type_scores,
                'vendor_info': device_info.get('vendor_info', {})
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'identification de l'appareil: {e}")
            return {
                'device_type': 'error',
                'confidence': 'none',
                'score': 0.0,
                'error': str(e),
                'vendor_info': {}
            }
    
    def get_device_details(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtenir des détails enrichis sur l'appareil
        """
        identification = self.identify_device_type(device_info)
        
        # Ajouter des détails spécifiques au type
        device_type = identification['device_type']
        vendor_info = identification.get('vendor_info', {})
        
        details = {
            'basic_info': {
                'ip': device_info.get('ip'),
                'hostname': device_info.get('hostname'),
                'mac_address': device_info.get('mac_address'),
                'status': device_info.get('status', 'unknown')
            },
            'identification': identification,
            'network_info': {
                'services': device_info.get('services', []),
                'response_time': device_info.get('response_time'),
                'last_seen': device_info.get('last_seen')
            }
        }
        
        # Ajouter des suggestions d'actions basées sur le type
        if device_type == 'computer':
            details['suggested_actions'] = ['ping', 'ssh', 'wake_on_lan']
        elif device_type == 'smartphone':
            details['suggested_actions'] = ['ping', 'notification']
        elif device_type == 'router':
            details['suggested_actions'] = ['ping', 'web_interface', 'snmp']
        elif device_type == 'smart_tv':
            details['suggested_actions'] = ['ping', 'web_interface', 'cast']
        elif device_type == 'iot':
            details['suggested_actions'] = ['ping', 'web_interface', 'mqtt']
        elif device_type == 'raspberry_pi':
            details['suggested_actions'] = ['ping', 'ssh', 'web_interface']
        else:
            details['suggested_actions'] = ['ping']
        
        return details
    
    def analyze_multiple_devices(self, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyser plusieurs appareils et fournir des statistiques
        """
        results = []
        type_counts = {}
        vendor_counts = {}
        
        for device in devices:
            details = self.get_device_details(device)
            results.append(details)
            
            # Compter les types
            device_type = details['identification']['device_type']
            type_counts[device_type] = type_counts.get(device_type, 0) + 1
            
            # Compter les vendors
            vendor = details['identification']['vendor_info'].get('vendor', 'Unknown')
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        
        return {
            'devices': results,
            'statistics': {
                'total_devices': len(results),
                'device_types': type_counts,
                'vendors': vendor_counts,
                'identification_success_rate': len([d for d in results if d['identification']['device_type'] != 'unknown']) / len(results) if results else 0
            }
        }