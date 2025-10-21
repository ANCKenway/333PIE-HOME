"""
🌐 333HOME - Device Detector
Détection avancée d'appareils réseau

Combine:
- MAC Vendor API (macvendors.com)
- Base OUI locale étendue (IoT, chauffage, électroménager)
- Device Identifier (patterns hostname, services)
"""

import re
import time
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


# === MAC VENDOR API (async version) ===

class MacVendorAPI:
    """API pour récupérer les vendors via MAC"""
    
    def __init__(self):
        self.vendor_cache: Dict[str, Dict[str, Any]] = {}
        self.last_request_time = 0.0
        self.min_request_interval = 1.0  # 1s entre requêtes
    
    def _normalize_mac(self, mac_address: str) -> str:
        """Normalise MAC au format XX:XX:XX:XX:XX:XX"""
        mac_clean = ''.join(c for c in mac_address.upper() if c in '0123456789ABCDEF')
        if len(mac_clean) == 12:
            return ':'.join([mac_clean[i:i+2] for i in range(0, 12, 2)])
        return mac_address
    
    async def _rate_limit(self):
        """Respecte le rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def get_vendor_from_api(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """Récupère vendor via macvendors.com"""
        try:
            await self._rate_limit()
            mac_normalized = self._normalize_mac(mac_address)
            oui = ':'.join(mac_normalized.split(':')[:3])
            
            url = f"https://api.macvendors.com/{oui}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        vendor_name = (await response.text()).strip()
                        return {
                            'vendor': vendor_name,
                            'source': 'macvendors.com',
                            'confidence': 'high',
                            'oui': oui
                        }
                    elif response.status == 404:
                        return {
                            'vendor': 'Unknown',
                            'source': 'macvendors.com',
                            'confidence': 'unknown',
                            'oui': oui
                        }
        
        except asyncio.TimeoutError:
            logger.debug(f"⚠️  Timeout macvendors.com pour {mac_address}")
        except Exception as e:
            logger.debug(f"⚠️  Erreur macvendors.com pour {mac_address}: {e}")
        
        return None
    
    async def get_vendor_info(self, mac_address: str) -> Dict[str, Any]:
        """Récupère vendor (avec cache)"""
        if not mac_address:
            return {'vendor': 'Unknown', 'source': 'invalid_mac', 'confidence': 'none'}
        
        mac_normalized = self._normalize_mac(mac_address)
        
        # Cache check
        if mac_normalized in self.vendor_cache:
            cached = self.vendor_cache[mac_normalized].copy()
            cached['cached'] = True
            return cached
        
        # API call
        vendor_info = await self.get_vendor_from_api(mac_normalized)
        
        if not vendor_info:
            vendor_info = {
                'vendor': 'Unknown',
                'source': 'no_source',
                'confidence': 'none',
                'oui': ':'.join(mac_normalized.split(':')[:3])
            }
        
        vendor_info['cached'] = False
        self.vendor_cache[mac_normalized] = vendor_info.copy()
        
        return vendor_info


# === BASE OUI LOCALE ÉTENDUE ===

class ExtendedOUIDatabase:
    """Base OUI locale avec IoT, chauffage, électroménager"""
    
    def __init__(self):
        self.oui_database = {
            # APPLE (including randomized MACs patterns)
            "00:1F:F3": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad ancien"},
            "04:0C:CE": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone moderne"},
            "10:DD:B1": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone/iPad"},
            "14:7D:DA": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone"},
            "3C:A6:F6": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone"},
            "AC:BC:32": {"vendor": "Apple Inc.", "type": "computer", "note": "MacBook"},
            "A8:96:8A": {"vendor": "Apple Inc.", "type": "tv", "note": "Apple TV"},
            "CA:08:C5": {"vendor": "Apple Inc.", "type": "mobile", "note": "iPhone (MAC aléatoire)"},
            
            # SAMSUNG / ANDROID
            "F4:FE:FB": {"vendor": "Samsung", "type": "mobile", "note": "Galaxy/Android"},
            "2C:BA:BA": {"vendor": "Samsung", "type": "mobile", "note": "Galaxy"},
            "DC:71:96": {"vendor": "Samsung", "type": "mobile", "note": "Galaxy"},
            "9E:67:44": {"vendor": "Android Device", "type": "mobile", "note": "Android (MAC aléatoire)"},
            
            # CHAUFFAGE
            "00:17:88": {"vendor": "Bosch Thermotechnik", "type": "heating", "note": "Chaudière Bosch"},
            "00:1E:C2": {"vendor": "Vaillant", "type": "heating", "note": "Chaudière Vaillant"},
            "00:50:C2": {"vendor": "Viessmann", "type": "heating", "note": "Chaudière Viessmann"},
            "00:1A:79": {"vendor": "Daikin", "type": "heating", "note": "Climatisation Daikin"},
            
            # ÉLECTROMÉNAGER
            "28:6C:07": {"vendor": "Whirlpool", "type": "appliance", "note": "Lave-linge"},
            "00:A0:59": {"vendor": "LG Electronics", "type": "appliance", "note": "Électroménager LG"},
            "B4:7C:9C": {"vendor": "Miele", "type": "appliance", "note": "Électroménager Miele"},
            
            # IoT DOMESTIQUE
            "EC:FA:BC": {"vendor": "Nest Labs", "type": "iot", "note": "Thermostat Nest"},
            "68:FF:7B": {"vendor": "Philips Hue", "type": "iot", "note": "Ampoule Hue"},
            "B0:C5:54": {"vendor": "TP-Link", "type": "iot", "note": "Prise connectée"},
            
            # SÉCURITÉ
            "CC:50:E3": {"vendor": "Ring", "type": "security", "note": "Sonnette Ring"},
            "00:17:61": {"vendor": "Arlo", "type": "security", "note": "Caméra Arlo"},
            
            # MICROCONTRÔLEURS
            "A4:E5:7C": {"vendor": "Espressif", "type": "microcontroller", "note": "ESP32/ESP8266"},
            "24:0A:C4": {"vendor": "Espressif", "type": "microcontroller", "note": "ESP32"},
            "DC:A6:32": {"vendor": "Raspberry Pi", "type": "microcontroller", "note": "Raspberry Pi"},
            
            # ROUTEURS
            "8C:97:EA": {"vendor": "Freebox", "type": "router", "note": "Freebox"},
            "F4:CA:E5": {"vendor": "Orange Livebox", "type": "router", "note": "Livebox Orange"},
            
            # AUDIO/VIDEO
            "F4:FE:FB": {"vendor": "Samsung", "type": "tv", "note": "Smart TV Samsung"},
            "00:26:37": {"vendor": "LG", "type": "tv", "note": "Smart TV LG"},
            "B8:27:EB": {"vendor": "Sonos", "type": "audio", "note": "Enceinte Sonos"},
        }
    
    def lookup(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """Lookup dans la base locale"""
        if not mac_address:
            return None
        
        mac_clean = mac_address.upper().replace(':', '').replace('-', '').replace('.', '')
        if len(mac_clean) < 6:
            return None
        
        oui = ':'.join([mac_clean[i:i+2] for i in range(0, 6, 2)])
        
        if oui in self.oui_database:
            info = self.oui_database[oui].copy()
            info['source'] = 'local_oui'
            info['oui'] = oui
            info['confidence'] = 'high'
            return info
        
        return None
    
    def get_icon(self, device_type: str) -> str:
        """Icône selon type"""
        icons = {
            'mobile': '📱',
            'computer': '💻',
            'tv': '📺',
            'audio': '🔊',
            'heating': '🔥',
            'appliance': '🏠',
            'iot': '🌐',
            'security': '🛡️',
            'microcontroller': '🔧',
            'router': '🌐',
            'wearable': '⌚',
            'gaming': '🎮',
        }
        return icons.get(device_type, '❓')


# === DEVICE IDENTIFIER ===

class DeviceIdentifier:
    """Identifie le type d'appareil via patterns"""
    
    def __init__(self):
        self.patterns = {
            'smartphone': {
                'hostnames': [
                    r'.*iphone.*', r'.*android.*', r'.*samsung.*',
                    r'.*galaxy.*', r'.*pixel.*', r'.*xiaomi.*'
                ],
                'vendors': ['Apple', 'Samsung', 'Huawei', 'Xiaomi', 'OnePlus', 'Google'],
                'services': ['5353'],
            },
            'computer': {
                'hostnames': [
                    r'.*desktop.*', r'.*laptop.*', r'.*pc.*',
                    r'.*-pc$', r'.*win.*', r'.*ubuntu.*'
                ],
                'vendors': ['Dell', 'HP', 'Lenovo', 'ASUS', 'MSI'],
                'services': ['135', '139', '445', '3389'],
            },
            'router': {
                'hostnames': [
                    r'.*router.*', r'.*gateway.*', r'.*livebox.*',
                    r'.*freebox.*', r'.*bbox.*'
                ],
                'vendors': ['Netgear', 'TP-Link', 'D-Link', 'Freebox', 'Orange'],
                'services': ['80', '443', '8080'],
            },
            'smart_tv': {
                'hostnames': [r'.*tv.*', r'.*samsung.*tv.*', r'.*lg.*tv.*'],
                'vendors': ['Samsung', 'LG', 'Sony'],
                'services': ['8080', '9080'],
            },
            'iot': {
                'hostnames': [
                    r'.*esp.*', r'.*sensor.*', r'.*smart.*',
                    r'.*bulb.*', r'.*camera.*'
                ],
                'vendors': ['Espressif', 'Raspberry Pi', 'Nest', 'Philips'],
                'services': ['80', '443', '1883'],
            },
            'raspberry_pi': {
                'hostnames': [r'.*raspberry.*', r'.*rpi.*', r'.*pi.*'],
                'vendors': ['Raspberry Pi'],
                'services': ['22', '80'],
            },
        }
    
    def _match_patterns(self, value: str, patterns: List[str]) -> bool:
        """Check si value matche un pattern"""
        if not value:
            return False
        value_lower = value.lower()
        return any(re.match(p, value_lower) for p in patterns)
    
    def identify(
        self,
        hostname: Optional[str],
        vendor: Optional[str],
        services: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Identifie le type d'appareil"""
        scores = {}
        
        for device_type, patterns in self.patterns.items():
            score = 0.0
            
            # Hostname (40%)
            if hostname and self._match_patterns(hostname, patterns.get('hostnames', [])):
                score += 0.4
            
            # Vendor (40%)
            if vendor:
                vendor_patterns = patterns.get('vendors', [])
                if any(vp.lower() in vendor.lower() for vp in vendor_patterns):
                    score += 0.4
            
            # Services (20%)
            if services:
                service_patterns = patterns.get('services', [])
                if any(str(s) in service_patterns for s in services):
                    score += 0.2
            
            if score > 0:
                scores[device_type] = score
        
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            if best_score >= 0.3:
                confidence = 'high' if best_score >= 0.7 else 'medium'
                return {
                    'device_type': best_type,
                    'confidence': confidence,
                    'score': best_score,
                }
        
        return {
            'device_type': 'unknown',
            'confidence': 'low',
            'score': 0.0,
        }


# === DETECTOR PRINCIPAL ===

class DeviceDetector:
    """Détecteur d'appareils complet"""
    
    def __init__(self):
        self.mac_api = MacVendorAPI()
        self.oui_db = ExtendedOUIDatabase()
        self.identifier = DeviceIdentifier()
    
    async def detect_device(
        self,
        mac: str,
        ip: str,
        hostname: Optional[str] = None,
        services: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Détection complète d'un appareil
        
        Args:
            mac: Adresse MAC
            ip: Adresse IP
            hostname: Hostname (optionnel)
            services: Ports ouverts (optionnel)
            
        Returns:
            Dict avec vendor, device_type, confidence, etc.
        """
        logger.debug(f"🔍 Detecting device: {mac} ({ip})")
        
        # 1. Base OUI locale (prioritaire)
        local_info = self.oui_db.lookup(mac)
        
        if local_info:
            vendor = local_info['vendor']
            device_type = local_info.get('type', 'unknown')
            note = local_info.get('note', '')
            icon = self.oui_db.get_icon(device_type)
            
            return {
                'vendor': vendor,
                'device_type': device_type,
                'device_type_display': f"{icon} {note}" if note else f"{icon} {vendor}",
                'confidence': 'high',
                'source': 'local_oui',
                'note': note,
            }
        
        # 2. API externe (macvendors.com)
        api_info = await self.mac_api.get_vendor_info(mac)
        vendor = api_info.get('vendor', 'Unknown')
        
        # 3. Identification via patterns
        identification = self.identifier.identify(hostname, vendor, services)
        device_type = identification['device_type']
        confidence = identification['confidence']
        
        # Icône
        icon = self.oui_db.get_icon(device_type)
        
        return {
            'vendor': vendor,
            'device_type': device_type,
            'device_type_display': f"{icon} {vendor}",
            'confidence': confidence,
            'source': api_info.get('source', 'unknown'),
            'identification_score': identification['score'],
        }
    
    async def enrich_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données d'un appareil
        
        Args:
            device_data: Dict avec mac, ip, hostname
            
        Returns:
            Dict enrichi avec vendor, device_type, etc.
        """
        detection = await self.detect_device(
            mac=device_data.get('mac', ''),
            ip=device_data.get('current_ip', ''),
            hostname=device_data.get('current_hostname'),
            services=device_data.get('services', []),
        )
        
        # Merge avec les données existantes
        enriched = device_data.copy()
        enriched['vendor'] = detection['vendor']
        enriched['device_type'] = detection['device_type_display']
        enriched['os_detected'] = enriched.get('os_detected') or detection['device_type']
        
        return enriched
