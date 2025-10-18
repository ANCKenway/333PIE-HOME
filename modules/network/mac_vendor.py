"""
API pour récupérer les informations des fabricants via l'adresse MAC
Intégration avec macvendors.com et autres services
"""

import requests
import json
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MacVendorAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Home-Automation-Pi/1.0'
        })
        # Cache pour éviter les requêtes répétées
        self.vendor_cache = {}
        # Limite de taux pour les APIs
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 seconde entre les requêtes
    
    def _rate_limit(self):
        """Respecter la limite de taux des APIs"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _normalize_mac(self, mac_address: str) -> str:
        """Normaliser l'adresse MAC au format XX:XX:XX:XX:XX:XX"""
        # Enlever tous les séparateurs et convertir en majuscules
        mac_clean = ''.join(mac_address.upper().split(':'))
        mac_clean = ''.join(mac_clean.split('-'))
        mac_clean = ''.join(mac_clean.split('.'))
        
        # Reformater avec des :
        if len(mac_clean) == 12:
            return ':'.join([mac_clean[i:i+2] for i in range(0, 12, 2)])
        return mac_address
    
    def get_vendor_from_macvendors_com(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """Récupérer les infos via macvendors.com"""
        try:
            self._rate_limit()
            mac_normalized = self._normalize_mac(mac_address)
            
            # Utiliser seulement les 3 premiers octets (OUI)
            oui = ':'.join(mac_normalized.split(':')[:3])
            
            url = f"https://api.macvendors.com/{oui}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                vendor_name = response.text.strip()
                return {
                    'vendor': vendor_name,
                    'source': 'macvendors.com',
                    'confidence': 'high',
                    'oui': oui
                }
            elif response.status_code == 404:
                return {
                    'vendor': 'Unknown',
                    'source': 'macvendors.com',
                    'confidence': 'unknown',
                    'oui': oui
                }
                
        except requests.RequestException as e:
            logger.warning(f"Erreur lors de la requête macvendors.com pour {mac_address}: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue macvendors.com pour {mac_address}: {e}")
        
        return None
    
    def get_vendor_from_ieee(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """Fallback avec base de données IEEE locale si disponible"""
        try:
            mac_normalized = self._normalize_mac(mac_address)
            oui = mac_normalized.replace(':', '').upper()[:6]
            
            # Ici on pourrait intégrer une base de données IEEE locale
            # Pour l'instant, retourner None pour utiliser le cache local
            return None
            
        except Exception as e:
            logger.error(f"Erreur IEEE lookup pour {mac_address}: {e}")
            return None
    
    def get_vendor_info(self, mac_address: str) -> Dict[str, Any]:
        """
        Récupérer les informations du fabricant pour une adresse MAC
        Utilise le cache et plusieurs sources
        """
        if not mac_address:
            return {'vendor': 'Unknown', 'source': 'invalid_mac', 'confidence': 'none'}
        
        try:
            mac_normalized = self._normalize_mac(mac_address)
            
            # Vérifier le cache
            if mac_normalized in self.vendor_cache:
                cached_result = self.vendor_cache[mac_normalized].copy()
                cached_result['cached'] = True
                return cached_result
            
            # Essayer macvendors.com en premier
            vendor_info = self.get_vendor_from_macvendors_com(mac_normalized)
            
            # Fallback vers IEEE si nécessaire
            if not vendor_info or vendor_info.get('vendor') == 'Unknown':
                ieee_info = self.get_vendor_from_ieee(mac_normalized)
                if ieee_info:
                    vendor_info = ieee_info
            
            # Résultat par défaut si aucune source ne fonctionne
            if not vendor_info:
                vendor_info = {
                    'vendor': 'Unknown',
                    'source': 'no_source',
                    'confidence': 'none',
                    'oui': ':'.join(mac_normalized.split(':')[:3])
                }
            
            # Ajouter au cache
            vendor_info['cached'] = False
            self.vendor_cache[mac_normalized] = vendor_info.copy()
            
            return vendor_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos vendor pour {mac_address}: {e}")
            return {
                'vendor': 'Error',
                'source': 'error',
                'confidence': 'none',
                'error': str(e)
            }
    
    def get_multiple_vendors(self, mac_addresses: list) -> Dict[str, Dict[str, Any]]:
        """Récupérer les infos de plusieurs MACs en respectant les limites de taux"""
        results = {}
        total = len(mac_addresses)
        
        for i, mac in enumerate(mac_addresses, 1):
            logger.info(f"Récupération vendor {i}/{total}: {mac}")
            results[mac] = self.get_vendor_info(mac)
            
            # Petite pause pour éviter de surcharger les APIs
            if i < total:
                time.sleep(0.5)
        
        return results
    
    def clear_cache(self):
        """Vider le cache des vendors"""
        self.vendor_cache.clear()
        logger.info("Cache des vendors vidé")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Statistiques du cache"""
        return {
            'cache_size': len(self.vendor_cache),
            'cached_vendors': list(self.vendor_cache.keys())
        }