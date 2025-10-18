"""
Scanner MAC vendor amélioré avec base de données complète
Focus sur la détection Android/iOS via MAC addresses
API macvendors.com en priorité, fallback base locale
"""

import json
import os
import requests
import time
from typing import Dict, Tuple

class MacVendorDetector:
    """Détecteur de vendor basé sur MAC - optimisé pour mobiles"""
    
    def __init__(self):
        self.vendors_db = self._load_vendors_database()
        self.api_cache = {}  # Cache pour éviter trop de requêtes API
        self.last_api_call = 0
        self.api_delay = 1.1  # macvendors.com limite à 1 req/sec
        
    def _load_vendors_database(self) -> Dict:
        """Charge la base de données MAC vendors"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mac_vendors.json')
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erreur chargement base MAC: {e}")
            return self._get_fallback_vendors()
    
    def _get_fallback_vendors(self) -> Dict:
        """Base vendor minimale en fallback"""
        return {
            "apple": {
                "7CC3A1": "Apple", "F0F61C": "Apple", "3C2EFF": "Apple", 
                "80E6A1": "Apple", "E4E4AB": "Apple", "AC87A3": "Apple"
            },
            "samsung": {
                "001A92": "Samsung", "7C11CB": "Samsung", "E8039A": "Samsung",
                "78F882": "Samsung", "C85B76": "Samsung"
            },
            "xiaomi": {
                "8CFABA": "Xiaomi", "50EC50": "Xiaomi", "781D8A": "Xiaomi"
            }
        }
    
    def detect_vendor_and_type(self, mac: str) -> Tuple[str, str]:
        """
        Détecte vendor et type d'appareil depuis MAC
        1. API macvendors.com (si internet)
        2. Fallback base locale
        Returns: (vendor, device_type)
        """
        if not mac or mac.lower() in ["unknown", "", "00:00:00:00:00:00"]:
            return "Unknown", "Unknown Device"
        
        # Nettoyer la MAC
        mac_clean = mac.replace(':', '').replace('-', '').upper()
        if len(mac_clean) < 6:
            return "Unknown", "Unknown Device"
            
        mac_prefix = mac_clean[:6]
        
        # 1. Essayer l'API macvendors.com d'abord
        vendor_api = self._get_vendor_from_api(mac)
        if vendor_api and vendor_api != "Unknown":
            device_type = self._determine_device_type_from_vendor(vendor_api)
            print(f"    🌐 API Vendor: {vendor_api}")
            return vendor_api, device_type
        
        # 2. Recherche dans la base locale
        vendor, device_type = self._search_in_database(mac_prefix)
        if vendor != "Unknown":
            return vendor, device_type
        
        # 3. Détection des MAC locales/randomisées (mobiles)
        if self._is_locally_administered(mac_clean):
            return "Unknown (Private MAC)", "Mobile Device (Privacy Mode)"
        
        # 4. Patterns spéciaux pour mobiles
        mobile_type = self._detect_mobile_patterns(mac_prefix)
        if mobile_type:
            return "Unknown", mobile_type
            
        return "Unknown", "Unknown Device"
    
    def _get_vendor_from_api(self, mac: str) -> str:
        """Récupère le vendor depuis l'API macvendors.com"""
        
        # Vérifier le cache d'abord
        mac_prefix = mac.replace(':', '').replace('-', '').upper()[:6]
        if mac_prefix in self.api_cache:
            return self.api_cache[mac_prefix]
        
        # Respecter la limite de 1 req/sec
        current_time = time.time()
        if current_time - self.last_api_call < self.api_delay:
            time.sleep(self.api_delay - (current_time - self.last_api_call))
        
        try:
            # API macvendors.com - gratuite avec limite
            url = f"https://api.macvendors.com/{mac[:8]}"  # Premiers 8 chars suffisent
            
            response = requests.get(url, timeout=3)
            self.last_api_call = time.time()
            
            if response.status_code == 200:
                vendor = response.text.strip()
                
                # Nettoyer et normaliser la réponse
                if vendor and vendor != "Not found" and len(vendor) < 100:
                    # Garder seulement le nom principal
                    vendor_clean = vendor.split(',')[0].split('\n')[0].strip()
                    
                    # Cache le résultat
                    self.api_cache[mac_prefix] = vendor_clean
                    return vendor_clean
                    
            elif response.status_code == 429:
                print(f"    ⚠️ API rate limit atteinte")
                
        except requests.exceptions.RequestException:
            # Pas d'internet ou erreur réseau - continuer avec la base locale
            pass
        except Exception as e:
            print(f"    ❌ Erreur API: {e}")
        
        return "Unknown"
    
    def _determine_device_type_from_vendor(self, vendor: str) -> str:
        """Détermine le type d'appareil depuis le vendor API"""
        vendor_lower = vendor.lower()
        
        # Mapping vendor -> type d'appareil
        if any(term in vendor_lower for term in ['apple', 'cupertino']):
            return "Apple Device"
        elif any(term in vendor_lower for term in ['samsung']):
            return "Android Phone"
        elif any(term in vendor_lower for term in ['xiaomi', 'beijing xiaomi']):
            return "Android Phone"
        elif any(term in vendor_lower for term in ['huawei']):
            return "Android Phone"
        elif any(term in vendor_lower for term in ['oppo', 'vivo', 'oneplus']):
            return "Android Phone"
        elif any(term in vendor_lower for term in ['google']):
            return "Android Device"
        elif any(term in vendor_lower for term in ['intel']):
            return "PC/Laptop"
        elif any(term in vendor_lower for term in ['dell', 'hp', 'lenovo', 'asus']):
            return "PC/Laptop"
        elif any(term in vendor_lower for term in ['tp-link', 'netgear', 'cisco', 'ubiquiti']):
            return "Network Equipment"
        elif any(term in vendor_lower for term in ['raspberry']):
            return "Single Board Computer"
        else:
            return "Unknown Device"
    
    def _search_in_database(self, mac_prefix: str) -> Tuple[str, str]:
        """Recherche dans toutes les catégories de la base"""
        
        # Apple - priorité car beaucoup d'appareils
        if 'apple' in self.vendors_db:
            if mac_prefix in self.vendors_db['apple']:
                return "Apple", self._get_apple_device_type(mac_prefix)
        
        # Samsung
        if 'samsung' in self.vendors_db:
            if mac_prefix in self.vendors_db['samsung']:
                return "Samsung", "Android Phone"
        
        # Xiaomi
        if 'xiaomi' in self.vendors_db:
            if mac_prefix in self.vendors_db['xiaomi']:
                return "Xiaomi", "Android Phone"
        
        # Huawei 
        if 'huawei' in self.vendors_db:
            if mac_prefix in self.vendors_db['huawei']:
                return "Huawei", "Android Phone"
        
        # Google
        if 'google' in self.vendors_db:
            if mac_prefix in self.vendors_db['google']:
                return "Google", "Android Device"
        
        # OPPO
        if 'oppo' in self.vendors_db:
            if mac_prefix in self.vendors_db['oppo']:
                return "OPPO", "Android Phone"
        
        # VIVO
        if 'vivo' in self.vendors_db:
            if mac_prefix in self.vendors_db['vivo']:
                return "VIVO", "Android Phone"
        
        # OnePlus
        if 'oneplus' in self.vendors_db:
            if mac_prefix in self.vendors_db['oneplus']:
                return "OnePlus", "Android Phone"
        
        # Intel (souvent PC/laptops)
        if 'intel' in self.vendors_db:
            if mac_prefix in self.vendors_db['intel']:
                return "Intel", "PC/Laptop"
        
        # Dell
        if 'dell' in self.vendors_db:
            if mac_prefix in self.vendors_db['dell']:
                return "Dell", "PC/Laptop"
        
        # ASUS
        if 'asus' in self.vendors_db:
            if mac_prefix in self.vendors_db['asus']:
                return "ASUS", "PC/Router"
        
        # TP-Link
        if 'tp_link' in self.vendors_db:
            if mac_prefix in self.vendors_db['tp_link']:
                return "TP-Link", "Network Equipment"
        
        # Netgear
        if 'netgear' in self.vendors_db:
            if mac_prefix in self.vendors_db['netgear']:
                return "Netgear", "Network Equipment"
        
        return "Unknown", "Unknown Device"
    
    def _get_apple_device_type(self, mac_prefix: str) -> str:
        """Détermine le type d'appareil Apple (si possible)"""
        # Certains préfixes sont plus spécifiques à certains appareils
        # Mais en général difficile de distinguer iPhone/iPad/Mac juste par MAC
        return "Apple Device"  # iPhone/iPad/Mac/AppleTV
    
    def _is_locally_administered(self, mac_clean: str) -> bool:
        """
        Détecte si la MAC est locale (bit U/L = 1)
        iOS et Android utilisent des MAC locales pour la privacy
        """
        if len(mac_clean) < 2:
            return False
            
        # Premier octet en hex
        first_byte = int(mac_clean[:2], 16)
        
        # Bit 1 (locally administered) = 1 ?
        return (first_byte & 0x02) != 0
    
    def _detect_mobile_patterns(self, mac_prefix: str) -> str:
        """Détecte des patterns typiques des mobiles"""
        
        # Certains préfixes sont souvent utilisés par les mobiles
        # (à affiner selon observation)
        mobile_patterns = [
            "02", "06", "0A", "0E",  # Locales communes
            "12", "16", "1A", "1E",
            "32", "36", "3A", "3E",
            "52", "56", "5A", "5E",
            "72", "76", "7A", "7E",
            "92", "96", "9A", "9E",
            "B2", "B6", "BA", "BE",
            "D2", "D6", "DA", "DE",
            "F2", "F6", "FA", "FE"
        ]
        
        if mac_prefix[:2] in mobile_patterns:
            return "Mobile Device (Random MAC)"
            
        return None
    
    def get_device_description(self, vendor: str, device_type: str, hostname: str = None) -> str:
        """Génère une description complète de l'appareil"""
        parts = []
        
        # Base description
        if device_type != "Unknown Device":
            parts.append(device_type)
        elif vendor != "Unknown":
            parts.append(f"{vendor} Device")
        else:
            parts.append("Unknown Device")
        
        # Hostname si significatif
        if hostname and hostname != "unknown" and not hostname.startswith("device-"):
            parts.append(f"({hostname})")
        
        # Vendor si pas déjà dans le type
        if vendor != "Unknown" and vendor not in parts[0]:
            parts.append(f"- {vendor}")
        
        return " ".join(parts)
    
    def analyze_network_macs(self, mac_list: list) -> Dict:
        """Analyse une liste de MACs pour stats réseau"""
        stats = {
            "total": len(mac_list),
            "vendors": {},
            "device_types": {},
            "mobile_devices": 0,
            "apple_devices": 0,
            "android_devices": 0,
            "unknown": 0
        }
        
        for mac in mac_list:
            if not mac or mac == "unknown":
                stats["unknown"] += 1
                continue
                
            vendor, device_type = self.detect_vendor_and_type(mac)
            
            # Stats vendors
            stats["vendors"][vendor] = stats["vendors"].get(vendor, 0) + 1
            
            # Stats types
            stats["device_types"][device_type] = stats["device_types"].get(device_type, 0) + 1
            
            # Stats spéciales
            if "Mobile" in device_type or "Phone" in device_type:
                stats["mobile_devices"] += 1
            
            if vendor == "Apple":
                stats["apple_devices"] += 1
            
            if "Android" in device_type:
                stats["android_devices"] += 1
        
        return stats