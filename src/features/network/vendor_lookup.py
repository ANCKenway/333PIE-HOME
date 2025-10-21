"""
🏠 333HOME - MAC Vendor Lookup Service

Service de lookup vendor via MAC address avec fallback sur API externe.
Utilise cache local pour éviter trop de requêtes API.

API: https://macvendors.com/api
"""

import logging
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import aiohttp


logger = logging.getLogger(__name__)


class VendorLookupService:
    """
    Service de lookup vendor par MAC address
    
    - Cache local persistant (évite requêtes API répétées)
    - Fallback sur API MacVendors.com
    - Rate limiting (respect de l'API)
    """
    
    def __init__(self, cache_file: str = "data/vendor_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(days=30)  # Cache vendor 30 jours
        self.api_url = "https://api.macvendors.com/"
        self.rate_limit_delay = 1.0  # 1s entre requêtes (rate limit API)
        self.last_api_call = None
        self._load_cache()
    
    def _load_cache(self):
        """Charger le cache depuis le fichier"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get('vendors', {})
                    logger.info(f"✅ Vendor cache chargé: {len(self.cache)} entries")
            else:
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                self._save_cache()
        except Exception as e:
            logger.error(f"❌ Erreur chargement vendor cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Sauvegarder le cache sur disque"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_entries': len(self.cache),
                'vendors': self.cache
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"💾 Vendor cache sauvegardé: {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde vendor cache: {e}")
    
    def _normalize_mac(self, mac: str) -> str:
        """
        Normaliser MAC address pour lookup
        
        Extrait OUI (3 premiers octets): AA:BB:CC:DD:EE:FF → AA:BB:CC
        """
        # Enlever séparateurs et mettre en majuscules
        mac_clean = mac.upper().replace(':', '').replace('-', '').replace('.', '')
        
        # Prendre les 6 premiers caractères (3 octets = OUI)
        oui = mac_clean[:6]
        
        # Formater avec :
        return f"{oui[:2]}:{oui[2:4]}:{oui[4:6]}"
    
    def _is_cache_valid(self, oui: str) -> bool:
        """Vérifier si l'entrée cache est valide (pas expirée)"""
        if oui not in self.cache:
            return False
        
        entry = self.cache[oui]
        cached_at = datetime.fromisoformat(entry['cached_at'])
        
        return (datetime.now() - cached_at) < self.cache_ttl
    
    async def lookup(self, mac: str) -> Optional[str]:
        """
        Lookup vendor par MAC address
        
        1. Vérifie cache local (évite requêtes API répétées)
        2. Essaie API MacVendors (source la plus à jour)
        3. Fallback sur OUI database locale si API fail
        4. Sauvegarde résultat dans cache
        
        Args:
            mac: Adresse MAC complète (AA:BB:CC:DD:EE:FF)
            
        Returns:
            Nom du vendor ou None si introuvable
        """
        if not mac:
            return None
        
        # Normaliser MAC → OUI
        try:
            oui = self._normalize_mac(mac)
        except Exception as e:
            logger.warning(f"MAC invalide: {mac} - {e}")
            return None
        
        # 1. Check cache local (évite requêtes API répétées)
        if self._is_cache_valid(oui):
            vendor = self.cache[oui].get('vendor')
            logger.debug(f"📦 Cache hit: {oui} → {vendor}")
            return vendor
        
        # 2. Essayer API MacVendors (source la plus à jour)
        vendor = await self._api_lookup(oui)
        
        # 3. Fallback sur OUI database locale si API fail
        if not vendor:
            logger.debug(f"⚠️ API fail, trying local OUI database for {oui}")
            try:
                from src.core.models.oui_database import ExtendedOUIDatabase
                oui_db = ExtendedOUIDatabase()
                oui_info = oui_db.lookup(mac)
                if oui_info and oui_info.get('vendor'):
                    vendor = oui_info['vendor']
                    logger.info(f"📍 Local OUI fallback: {oui} → {vendor}")
            except Exception as e:
                logger.debug(f"Local OUI lookup failed: {e}")
        
        # 4. Sauvegarder dans cache (même si None pour éviter requêtes répétées)
        self.cache[oui] = {
            'vendor': vendor,
            'cached_at': datetime.now().isoformat(),
            'source': 'api' if vendor else 'unknown'
        }
        self._save_cache()
        
        return vendor
    
    async def _api_lookup(self, oui: str) -> Optional[str]:
        """
        Lookup vendor via API MacVendors
        
        Rate limit: 1 req/s
        """
        # Rate limiting: attendre 1s depuis dernière requête
        if self.last_api_call:
            elapsed = (datetime.now() - self.last_api_call).total_seconds()
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        
        try:
            async with aiohttp.ClientSession() as session:
                # API endpoint: GET https://api.macvendors.com/AA:BB:CC
                url = f"{self.api_url}{oui}"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    self.last_api_call = datetime.now()
                    
                    if response.status == 200:
                        vendor = await response.text()
                        vendor = vendor.strip()
                        logger.info(f"🌐 API lookup: {oui} → {vendor}")
                        return vendor
                    elif response.status == 404:
                        logger.debug(f"❓ Vendor inconnu: {oui}")
                        return None
                    else:
                        logger.warning(f"⚠️ API error: {response.status} pour {oui}")
                        return None
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ API timeout pour {oui}")
            return None
        except Exception as e:
            logger.error(f"❌ API lookup error pour {oui}: {e}")
            return None
    
    async def bulk_lookup(self, macs: list) -> Dict[str, Optional[str]]:
        """
        Lookup vendor pour plusieurs MAC addresses
        
        Avec rate limiting automatique entre requêtes.
        
        Args:
            macs: Liste de MAC addresses
            
        Returns:
            Dict {mac: vendor}
        """
        results = {}
        
        for mac in macs:
            vendor = await self.lookup(mac)
            results[mac] = vendor
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Statistiques du cache"""
        valid_entries = sum(1 for oui in self.cache.keys() if self._is_cache_valid(oui))
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self.cache) - valid_entries,
            'cache_file': str(self.cache_file),
            'cache_ttl_days': self.cache_ttl.days
        }


# Singleton global
_vendor_service: Optional[VendorLookupService] = None


def get_vendor_lookup_service() -> VendorLookupService:
    """
    Récupérer l'instance singleton du VendorLookupService
    
    Garantit une seule instance avec cache partagé.
    """
    global _vendor_service
    if _vendor_service is None:
        _vendor_service = VendorLookupService()
    return _vendor_service
