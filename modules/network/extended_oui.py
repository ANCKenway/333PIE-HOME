"""
Base de données locale étendue des vendors MAC OUI
Inclut les constructeurs IoT, industriels, chaudières, électroménager
"""

import json
import logging
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)

class ExtendedOUIDatabase:
    def __init__(self):
        # Base OUI étendue avec vendors IoT/industriels
        self.oui_database = {
            # === APPAREILS APPLE (complet) ===
            "00:1F:F3": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad ancien"},
            "00:23:DF": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone 3G/3GS"},
            "00:26:4A": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone 4"},
            "04:0C:CE": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone moderne"},
            "28:CF:E9": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "3C:15:C2": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "70:56:81": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "B8:8D:12": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "DC:2B:61": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "F0:2F:74": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "A4:B1:C1": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "BC:52:B7": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "AC:BC:32": {"vendor": "Apple Inc.", "type": "computer", "note": "MacBook"},
            "A8:96:8A": {"vendor": "Apple Inc.", "type": "tv", "note": "Apple TV"},
            
            # === ÉLECTROMÉNAGER & CHAUFFAGE ===
            "00:17:88": {"vendor": "Bosch Thermotechnik GmbH", "type": "heating", "note": "Chaudière Bosch"},
            "00:1E:C2": {"vendor": "Vaillant GmbH", "type": "heating", "note": "Chaudière Vaillant"},
            "00:50:C2": {"vendor": "Viessmann Werke", "type": "heating", "note": "Chaudière Viessmann"},
            "08:00:28": {"vendor": "Saunier Duval", "type": "heating", "note": "Chaudière Saunier Duval"},
            "00:0C:CC": {"vendor": "De Dietrich Thermique", "type": "heating", "note": "Chaudière De Dietrich"},
            "00:15:6D": {"vendor": "Atlantic Climatisation", "type": "heating", "note": "Pompe à chaleur Atlantic"},
            "00:1A:79": {"vendor": "Daikin Industries", "type": "heating", "note": "Climatisation Daikin"},
            "00:04:A3": {"vendor": "Mitsubishi Electric", "type": "heating", "note": "Climatisation Mitsubishi"},
            
            # Électroménager
            "28:6C:07": {"vendor": "Whirlpool Corporation", "type": "appliance", "note": "Lave-linge/lave-vaisselle"},
            "00:A0:59": {"vendor": "LG Electronics", "type": "appliance", "note": "Électroménager LG"},
            "34:E6:D7": {"vendor": "Samsung Electronics", "type": "appliance", "note": "Électroménager Samsung"},
            "B4:7C:9C": {"vendor": "Miele & Cie", "type": "appliance", "note": "Électroménager Miele"},
            "00:50:43": {"vendor": "BSH Hausgeräte GmbH", "type": "appliance", "note": "Électroménager Bosch/Siemens"},
            "FC:75:16": {"vendor": "Candy Hoover Group", "type": "appliance", "note": "Lave-linge Candy"},
            
            # === IoT DOMESTIQUE ===
            "EC:FA:BC": {"vendor": "Nest Labs", "type": "iot", "note": "Thermostat Nest"},
            "18:B4:30": {"vendor": "Nest Labs", "type": "iot", "note": "Nest Protect"},
            "64:16:66": {"vendor": "Honeywell International", "type": "iot", "note": "Thermostat Honeywell"},
            "00:1A:92": {"vendor": "ASUSTeK Computer", "type": "iot", "note": "Routeur/IoT ASUS"},
            "C8:FF:77": {"vendor": "Dyson Limited", "type": "iot", "note": "Aspirateur/Ventilateur Dyson"},
            "24:4C:E3": {"vendor": "Dyson Limited", "type": "iot", "note": "Purificateur Dyson"},
            
            # === DOMOTIQUE & SÉCURITÉ ===
            "CC:50:E3": {"vendor": "Ring Inc", "type": "security", "note": "Sonnette Ring"},
            "AC:63:BE": {"vendor": "Ring Inc", "type": "security", "note": "Caméra Ring"},
            "00:17:61": {"vendor": "Arlo Technologies", "type": "security", "note": "Caméra Arlo"},
            "B0:C5:54": {"vendor": "TP-Link Technologies", "type": "iot", "note": "Prise connectée TP-Link"},
            "50:C7:BF": {"vendor": "TP-Link Technologies", "type": "iot", "note": "Ampoule Kasa"},
            "68:FF:7B": {"vendor": "Philips Lighting", "type": "iot", "note": "Ampoule Hue"},
            "EC:B5:FA": {"vendor": "Philips Lighting", "type": "iot", "note": "Bridge Hue"},
            
            # === MICROCONTRÔLEURS IoT ===
            "A4:E5:7C": {"vendor": "Espressif Inc.", "type": "microcontroller", "note": "ESP32/ESP8266"},
            "24:0A:C4": {"vendor": "Espressif Inc.", "type": "microcontroller", "note": "ESP32"},
            "84:0D:8E": {"vendor": "Espressif Inc.", "type": "microcontroller", "note": "ESP32"},
            "8C:AA:B5": {"vendor": "Espressif Inc.", "type": "microcontroller", "note": "ESP8266"},
            "CC:50:E3": {"vendor": "Raspberry Pi Foundation", "type": "microcontroller", "note": "Raspberry Pi"},
            "DC:A6:32": {"vendor": "Raspberry Pi Foundation", "type": "microcontroller", "note": "Raspberry Pi"},
            
            # === VÉHICULES CONNECTÉS ===
            "00:1F:3A": {"vendor": "Tesla Motors", "type": "vehicle", "note": "Tesla"},
            "00:23:AE": {"vendor": "BMW Group", "type": "vehicle", "note": "BMW ConnectedDrive"},
            "00:0F:3D": {"vendor": "Renault", "type": "vehicle", "note": "Renault EASY CONNECT"},
            "70:B3:D5": {"vendor": "Tesla Motors", "type": "vehicle", "note": "Tesla Model S/3/X/Y"},
            
            # === AUDIO/VIDEO ===
            "F4:FE:FB": {"vendor": "Samsung Electronics", "type": "tv", "note": "Smart TV Samsung"},
            "00:26:37": {"vendor": "LG Electronics", "type": "tv", "note": "Smart TV LG"},
            "04:5E:A4": {"vendor": "Sony Corporation", "type": "tv", "note": "Smart TV Sony"},
            "B8:27:EB": {"vendor": "Sonos Inc.", "type": "audio", "note": "Enceinte Sonos"},
            "00:0E:58": {"vendor": "Sonos Inc.", "type": "audio", "note": "Enceinte Sonos"},
            "5C:AA:FD": {"vendor": "Sonos Inc.", "type": "audio", "note": "Enceinte Sonos"},
            
            # === CONSTRUCTEURS PC ÉTENDUS ===
            "C8:7F:54": {"vendor": "ASUSTeK Computer Inc.", "type": "computer", "note": "PC/Laptop ASUS"},
            "34:5A:60": {"vendor": "Micro-Star International", "type": "computer", "note": "PC/Laptop MSI"},
            "70:85:C2": {"vendor": "Dell Inc.", "type": "computer", "note": "PC/Laptop Dell"},
            "A4:BB:6D": {"vendor": "Dell Inc.", "type": "computer", "note": "PC/Laptop Dell"},
            "3C:52:82": {"vendor": "HP Inc.", "type": "computer", "note": "PC/Laptop HP"},
            "E4:3A:6E": {"vendor": "Lenovo", "type": "computer", "note": "PC/Laptop Lenovo"},
            
            # === ROUTEURS/RÉSEAU ÉTENDUS ===
            "8C:97:EA": {"vendor": "FREEBOX SAS", "type": "router", "note": "Freebox"},
            "00:24:D4": {"vendor": "FREEBOX SAS", "type": "router", "note": "Freebox"},
            "F4:CA:E5": {"vendor": "Orange Livebox", "type": "router", "note": "Livebox Orange"},
            "E4:5F:01": {"vendor": "Netgear", "type": "router", "note": "Routeur Netgear"},
            "C0:4A:00": {"vendor": "TP-Link Technologies", "type": "router", "note": "Routeur TP-Link"},
            "14:CC:20": {"vendor": "TP-Link Technologies", "type": "router", "note": "Routeur TP-Link"},
            
            # === MONTRES CONNECTÉES ===
            "00:1A:7D": {"vendor": "Apple Inc.", "type": "wearable", "note": "Apple Watch"},
            "A0:E6:F8": {"vendor": "Apple Inc.", "type": "wearable", "note": "Apple Watch"},
            "C8:69:CD": {"vendor": "Samsung Electronics", "type": "wearable", "note": "Galaxy Watch"},
            "2C:44:01": {"vendor": "Fitbit Inc.", "type": "wearable", "note": "Fitbit"},
            
            # === CONSOLES DE JEU ===
            "7C:ED:8D": {"vendor": "Sony Computer Entertainment", "type": "gaming", "note": "PlayStation"},
            "A4:C0:E1": {"vendor": "Microsoft Corporation", "type": "gaming", "note": "Xbox"},
            "A4:5E:60": {"vendor": "Nintendo Co.", "type": "gaming", "note": "Nintendo Switch"},
            "00:09:BF": {"vendor": "Nintendo Co.", "type": "gaming", "note": "Nintendo Wii/Switch"},
        }
        
        # Patterns pour reconnaissance heuristique
        self.vendor_patterns = {
            # Pattern basé sur les 2 premiers octets pour certains constructeurs
            "A4:E5": "Espressif Inc. (ESP32)",
            "24:0A": "Espressif Inc. (ESP32)", 
            "84:0D": "Espressif Inc. (ESP32)",
            "C8:7F": "ASUSTeK Computer Inc.",
            "34:5A": "Micro-Star International (MSI)",
            "F4:FE": "Samsung Electronics Co.,Ltd",
            "C8:FF": "Dyson Limited",
            "8C:97": "FREEBOX SAS",
            "DC:A6": "Raspberry Pi Foundation",
        }
    
    def lookup_vendor(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """Lookup vendor dans la base locale étendue"""
        if not mac_address:
            return None
        
        # Normaliser MAC
        mac_clean = mac_address.upper().replace(':', '').replace('-', '').replace('.', '')
        if len(mac_clean) < 6:
            return None
        
        # OUI (3 premiers octets)
        oui = ':'.join([mac_clean[i:i+2] for i in range(0, 6, 2)])
        
        # Lookup exact OUI
        if oui in self.oui_database:
            vendor_info = self.oui_database[oui].copy()
            vendor_info['source'] = 'local_oui_database'
            vendor_info['oui'] = oui
            vendor_info['confidence'] = 'high'
            return vendor_info
        
        # Lookup pattern (2 premiers octets)
        oui_short = oui[:5]  # "A4:E5"
        if oui_short in self.vendor_patterns:
            return {
                'vendor': self.vendor_patterns[oui_short],
                'type': 'unknown',
                'source': 'local_pattern',
                'oui': oui,
                'confidence': 'medium',
                'note': 'Détection par pattern'
            }
        
        return None
    
    def get_device_type_icon(self, vendor_info: Dict[str, Any]) -> str:
        """Retourner l'icône appropriée basée sur le type d'appareil"""
        device_type = vendor_info.get('type', 'unknown')
        vendor = vendor_info.get('vendor', '').lower()
        
        icon_map = {
            'mobile': '📱',
            'computer': '💻', 
            'tv': '📺',
            'audio': '🔊',
            'heating': '🔥',
            'appliance': '🏠',
            'iot': '🌐',
            'security': '🛡️',
            'microcontroller': '🔧',
            'vehicle': '🚗',
            'router': '🌐',
            'wearable': '⌚',
            'gaming': '🎮'
        }
        
        icon = icon_map.get(device_type, '❓')
        
        # Cas spéciaux
        if 'apple' in vendor:
            if device_type == 'mobile':
                icon = '📱'
            elif device_type == 'computer':
                icon = '💻'
            elif device_type == 'tv':
                icon = '📺'
            elif device_type == 'wearable':
                icon = '⌚'
            else:
                icon = '🍎'
        elif 'dyson' in vendor:
            icon = '💨'
        elif 'tesla' in vendor:
            icon = '🚗'
        elif 'nest' in vendor:
            icon = '🏠'
        
        return icon
    
    def get_comprehensive_device_info(self, mac_address: str) -> Dict[str, Any]:
        """Informations complètes sur un appareil basé sur sa MAC"""
        vendor_info = self.lookup_vendor(mac_address)
        
        if not vendor_info:
            return {
                'vendor': 'Unknown',
                'device_type': '❓ Appareil inconnu',
                'category': 'Autres',
                'confidence': 'none',
                'source': 'unknown'
            }
        
        icon = self.get_device_type_icon(vendor_info)
        vendor_name = vendor_info['vendor']
        device_type = vendor_info.get('type', 'unknown')
        note = vendor_info.get('note', '')
        
        # Construction du device_type avec icône
        if note:
            device_type_display = f"{icon} {note}"
        else:
            device_type_display = f"{icon} {vendor_name}"
        
        # Catégorisation
        category_map = {
            'mobile': 'Mobiles',
            'computer': 'Ordinateurs', 
            'tv': 'Périphériques',
            'audio': 'Périphériques',
            'heating': 'Domotique',
            'appliance': 'Électroménager',
            'iot': 'IoT',
            'security': 'Sécurité',
            'microcontroller': 'Développement',
            'vehicle': 'Véhicules',
            'router': 'Réseau',
            'wearable': 'Mobiles',
            'gaming': 'Divertissement'
        }
        
        category = category_map.get(device_type, 'Autres')
        
        return {
            'vendor': vendor_name,
            'device_type': device_type_display,
            'category': category,
            'confidence': vendor_info.get('confidence', 'medium'),
            'source': vendor_info.get('source', 'local'),
            'device_category': device_type,
            'note': note,
            'oui': vendor_info.get('oui', ''),
            'raw_info': vendor_info
        }
    
    def search_by_vendor_name(self, vendor_name: str) -> List[str]:
        """Rechercher les OUIs d'un constructeur"""
        vendor_name = vendor_name.lower()
        matching_ouis = []
        
        for oui, info in self.oui_database.items():
            if vendor_name in info['vendor'].lower():
                matching_ouis.append(oui)
        
        return matching_ouis
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques de la base OUI"""
        stats = {
            'total_ouis': len(self.oui_database),
            'by_type': {},
            'vendors_count': len(set(info['vendor'] for info in self.oui_database.values()))
        }
        
        for info in self.oui_database.values():
            device_type = info.get('type', 'unknown')
            stats['by_type'][device_type] = stats['by_type'].get(device_type, 0) + 1
        
        return stats