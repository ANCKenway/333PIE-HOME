"""
🌐 333HOME - Network Scan Router
Endpoints pour les scans réseau

⚠️ SCANS ON-DEMAND uniquement (pas de background)
🎯 Utilise MultiSourceScanner (nmap+ARP+mDNS+NetBIOS) pour hostname detection avancée
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..schemas import ScanRequest, ScanResult, NetworkDeviceCreate
from ..scanners.multi_source import MultiSourceScanner  # ✅ Déplacé dans scanners/
from ..storage import save_scan_result, get_all_devices, get_device_by_mac
from ..history import NetworkHistory
from ..registry import NetworkRegistry
from src.shared.constants import DeviceStatus  # ✅ Source unique RÈGLE #1


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scan", tags=["network-scan"])

# Scan en cours (éviter doublons)
_current_scan: Optional[ScanResult] = None
_scan_in_progress = False


async def enrich_vendors_from_api(devices: List[dict], registry):
    """
    Enrichir vendors manquants via API MacVendors (background task)
    
    Args:
        devices: Liste des devices du scan
        registry: Instance NetworkRegistry
    """
    try:
        from ..vendor_lookup import get_vendor_lookup_service
        vendor_service = get_vendor_lookup_service()
        
        # Trouver devices sans vendor
        devices_without_vendor = [
            d for d in devices 
            if not d.get('vendor') or d.get('vendor') == 'Unknown'
        ]
        
        if not devices_without_vendor:
            logger.debug("✅ Tous les devices ont déjà un vendor")
            return
        
        logger.info(f"🌐 Enrichissement vendor API: {len(devices_without_vendor)} devices")
        
        # Lookup vendors (avec rate limiting automatique)
        for device in devices_without_vendor:
            mac = device.get('mac')
            if not mac:
                continue
            
            vendor = await vendor_service.lookup(mac)
            
            if vendor:
                # Mettre à jour dans le registry
                registry_device = registry.devices.get(mac.upper())
                if registry_device and not registry_device.vendor:
                    registry_device.vendor = vendor
                    logger.info(f"✅ Vendor enrichi: {mac[:17]} → {vendor}")
        
        # Sauvegarder registry avec nouveaux vendors
        registry._save()
        logger.info(f"💾 Registry sauvegardé avec vendors enrichis")
        
    except Exception as e:
        logger.error(f"❌ Erreur enrichissement vendors: {e}")


async def enrich_vpn_status(registry):
    """
    Enrichir statut VPN Tailscale depuis API (background task)
    
    Args:
        registry: Instance NetworkRegistry
    """
    try:
        from ..scanners.tailscale_scanner import TailscaleScanner
        
        logger.info("🔒 Enrichissement VPN Tailscale...")
        
        ts_scanner = TailscaleScanner("192.168.1.0/24")
        ts_devices = ts_scanner.scan()
        
        # Créer map MAC -> VPN info
        vpn_map = {}
        for ts_device in ts_devices:
            # Trouver MAC correspondant dans registry via hostname ou IP
            hostname = ts_device.get('hostname', '').upper()
            vpn_ip = ts_device.get('ip')
            is_online = ts_device.get('is_online', False)
            
            if not hostname:
                continue
            
            # Chercher device par hostname dans registry
            for mac, reg_device in registry.devices.items():
                reg_hostname = (reg_device.current_hostname or '').upper()
                if reg_hostname == hostname:
                    vpn_map[mac] = {
                        'vpn_ip': vpn_ip,
                        'is_vpn_connected': is_online
                    }
                    break
        
        # Mettre à jour tous les devices du registry
        updated_count = 0
        for mac, reg_device in registry.devices.items():
            if mac in vpn_map:
                # Device a un VPN
                reg_device.vpn_ip = vpn_map[mac]['vpn_ip']
                reg_device.is_vpn_connected = vpn_map[mac]['is_vpn_connected']
                updated_count += 1
            else:
                # Device n'a pas de VPN ou VPN offline
                reg_device.is_vpn_connected = False
                # Garder vpn_ip si existant (peut être temporairement offline)
        
        # Sauvegarder
        registry._save()
        logger.info(f"✅ VPN enrichi: {updated_count} devices avec VPN, {len(registry.devices)-updated_count} sans VPN")
        
    except Exception as e:
        logger.error(f"❌ Erreur enrichissement VPN: {e}")


def _load_last_scan_from_history():
    """Charge le dernier scan depuis l'historique au démarrage"""
    global _current_scan
    try:
        import json
        from pathlib import Path
        
        history_file = Path("data/network_scan_history.json")
        if history_file.exists():
            with open(history_file, 'r') as f:
                data = json.load(f)
                scans = data.get('scans', [])
                if scans:
                    # Prendre le dernier scan (le plus récent)
                    last_scan_dict = scans[-1]
                    # Convertir en ScanResult
                    _current_scan = ScanResult(**last_scan_dict)
                    logger.info(f"✅ Dernier scan chargé depuis l'historique: {len(_current_scan.devices)} devices")
    except Exception as e:
        logger.warning(f"Impossible de charger le dernier scan: {e}")


# Charger dernier scan au démarrage du module
_load_last_scan_from_history()


@router.post("", response_model=ScanResult)
async def scan_network(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
) -> ScanResult:
    """
    Lance un scan réseau ON-DEMAND
    
    🔧 Optimisé : Scans throttled, timing polite (-T2)
    
    Args:
        scan_request: Configuration du scan
        background_tasks: Tasks FastAPI
        
    Returns:
        ScanResult avec les devices trouvés
    """
    global _scan_in_progress, _current_scan
    
    if _scan_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Un scan est déjà en cours"
        )
    
    try:
        _scan_in_progress = True
        logger.info(f"🌐 Starting MULTI-SOURCE network scan (FULL)")
        
        # Phase 6: 1 seul scan type = FULL (toutes sources activées)
        # RULES.MD: "Pas de versions multiples" → quick/arp/mdns supprimés
        scanner = MultiSourceScanner(subnet=scan_request.subnet)
        logger.info("🔥 Full scan: nmap + ARP + mDNS + NetBIOS + Tailscale")
        
        # Lancer le scan multi-sources (toutes sources)
        unified_devices = await scanner.scan_all()
        
        # Filtrer devices VPN-only (pas d'IP locale)
        # Les devices enrichis avec VPN mais ayant une IP locale sont gardés
        network_devices_only = [
            ud for ud in unified_devices
            if ud.current_ip and not ud.current_ip.startswith('100.')
        ]
        
        logger.info(f"📊 Filtered: {len(unified_devices)} total -> {len(network_devices_only)} network-only (excluded {len(unified_devices)-len(network_devices_only)} VPN-only)")
        
        # Convertir UnifiedDevice -> NetworkDevice pour ScanResult
        from ..schemas import NetworkDevice, ServiceInfo
        from datetime import datetime
        
        devices = []
        for ud in network_devices_only:
            # Convertir services (str -> ServiceInfo)
            services = []
            if ud.capabilities and ud.capabilities.services:
                for svc_name in ud.capabilities.services:
                    services.append(ServiceInfo(
                        port=0,  # Port inconnu pour l'instant
                        service=svc_name,
                        name=svc_name,
                        icon="🔌"
                    ))
            
            nd = NetworkDevice(
                id=ud.id,  # ✅ UnifiedDevice.id
                mac=ud.mac,
                current_ip=ud.current_ip or "0.0.0.0",  # ✅ Required field
                current_hostname=ud.hostname,  # ✅ UnifiedDevice.hostname
                vendor=ud.vendor,
                device_type=ud.device_type,
                os_detected=ud.capabilities.detected_os if ud.capabilities else None,
                device_role=None,
                first_seen=ud.first_seen or datetime.now(),  # ✅ Required
                last_seen=ud.last_seen or datetime.now(),  # ✅ Required
                total_appearances=ud.total_scans_detected,
                currently_online=(ud.status == DeviceStatus.ONLINE),
                in_devices=ud.is_managed,
                tags=ud.tags,
                services=services,
                # ✅ Status simple (basé sur scans)
                last_seen_relative=ud.last_seen_relative,
                scan_status=ud.scan_status,
                # ✅ VPN (Tailscale)
                is_vpn_connected=ud.is_vpn_connected,
                vpn_ip=ud.vpn_ip,
                vpn_hostname=ud.vpn_hostname,
                # ✅ Agent (depuis registry)
                is_agent_connected=False,  # Sera enrichi par registry
                agent_id=None,
                agent_version=None
            )
            devices.append(nd)
        
        # Créer ScanResult
        from uuid import uuid4
        scan_result = ScanResult(
            scan_id=f"scan_{uuid4().hex[:8]}",  # ✅ Required field
            duration_ms=int((datetime.now() - datetime.now()).total_seconds() * 1000),  # ✅ Required
            scan_type=scan_request.scan_type,
            subnet=scan_request.subnet,
            devices_found=len(devices),
            devices=devices,
            new_devices=0  # Sera calculé ci-dessous
        )
        
        # 🔥 ENRICHIR LE NETWORK REGISTRY (suivi persistant)
        from ..registry import get_network_registry
        registry = get_network_registry()
        
        # Convertir devices en format dict pour le registry
        devices_for_registry = []
        for device in devices:
            devices_for_registry.append({
                'mac': device.mac,
                'current_ip': device.current_ip,
                'current_hostname': device.current_hostname,
                'vendor': device.vendor,
                'os_detected': device.os_detected,
                'device_type': device.device_type,
                'is_online': device.currently_online,
                'is_vpn_connected': device.is_vpn_connected,
                'vpn_ip': device.vpn_ip
            })
        
        # Enrichir le registry et récupérer les stats
        registry_stats = registry.update_from_scan(devices_for_registry)
        scan_result.new_devices = registry_stats['new']
        
        # 🌐 ENRICHISSEMENT: Vendor lookup API pour devices sans vendor
        # (en background pour ne pas ralentir la réponse)
        background_tasks.add_task(enrich_vendors_from_api, devices_for_registry, registry)
        
        # 🔒 ENRICHISSEMENT: VPN Tailscale status (sync temps réel)
        # (en background pour ne pas ralentir la réponse)
        background_tasks.add_task(enrich_vpn_status, registry)
        
        logger.info(
            f"📊 Registry enrichi: {registry_stats['new']} nouveaux, "
            f"{registry_stats['updated']} mis à jour, "
            f"{len(registry_stats['changes'])} changements"
        )
        
        # Log des changements importants
        for change in registry_stats['changes'][:10]:  # Top 10
            if change['type'] == 'ip_changed':
                logger.info(f"🔄 DHCP change: {change['mac']} {change['old_ip']} → {change['new_ip']}")
            elif change['type'] == 'hostname_changed':
                logger.info(f"🔄 Hostname change: {change['mac']} {change['old_hostname']} → {change['new_hostname']}")
        
        # Détecter les changements et log events (legacy history)
        history = NetworkHistory()
        for device in scan_result.devices:
            previous = get_device_by_mac(device.mac)
            history.detect_and_log_changes(previous, device)
        
        # Sauvegarder en background
        background_tasks.add_task(save_scan_result, scan_result)
        
        _current_scan = scan_result
        
        logger.info(
            f"✅ Scan completed: {scan_result.devices_found} devices, "
            f"{scan_result.new_devices} new"
        )
        
        return scan_result
    
    except Exception as e:
        logger.error(f"❌ Scan failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Échec du scan: {str(e)}"
        )
    
    finally:
        _scan_in_progress = False


@router.get("/status")
async def get_scan_status() -> dict:
    """
    Statut du scan en cours
    
    Returns:
        Dict avec in_progress et last_scan
    """
    global _scan_in_progress, _current_scan
    
    return {
        "in_progress": _scan_in_progress,
        "last_scan": _current_scan.model_dump() if _current_scan else None,
    }


@router.get("/ping")
async def quick_ping_check() -> dict:
    """
    Ping rapide ARP + Tailscale status (pour refresh temps réel)
    
    Ultra-léger: ARP cache + Tailscale JSON (pas de scan actif)
    Retourne: {devices: [{mac, ip, is_online, is_vpn_connected, vpn_ip}]}
    """
    from ..scanners.arp_scanner import ARPScanner
    from ..scanners.tailscale_scanner import TailscaleScanner
    
    try:
        # 1. Check ARP cache (instantané)
        arp_scanner = ARPScanner("192.168.1.0/24")
        arp_devices = await arp_scanner.scan()
        
        # 2. Check Tailscale status (instantané)
        ts_scanner = TailscaleScanner("192.168.1.0/24")
        vpn_map = await ts_scanner.scan()
        
        # 3. Créer liste de devices avec status
        devices_status = []
        
        # D'abord les devices locaux (ARP)
        online_macs = {d.mac.upper() for d in arp_devices if d.is_online}
        
        for device in arp_devices:
            mac = device.mac.upper()
            hostname = (device.hostname or '').split('.')[0].upper()
            
            # Check VPN status (existe ET online)
            vpn_info = vpn_map.get(hostname) if hostname else None
            is_vpn_connected = vpn_info['is_online'] if vpn_info else False  # ✅ Vérifier Online flag
            
            devices_status.append({
                'mac': mac,
                'ip': device.ip,
                'is_online': device.is_online,
                'is_vpn_connected': is_vpn_connected,
                'vpn_ip': vpn_info['vpn_ip'] if vpn_info else None,
                'hostname': device.hostname
            })
        
        # Ajouter devices VPN qui ne sont pas dans ARP (pour afficher même si offline)
        for hostname_upper, vpn_info in vpn_map.items():
            # Vérifier si ce device n'est pas déjà dans la liste
            vpn_ip = vpn_info['vpn_ip']
            if not any(d['vpn_ip'] == vpn_ip for d in devices_status):
                devices_status.append({
                    'mac': None,  # Pas de MAC pour VPN-only
                    'ip': vpn_info.get('local_ip'),
                    'is_online': False,  # Pas détecté en local
                    'is_vpn_connected': vpn_info['is_online'],  # ✅ Status VPN réel
                    'vpn_ip': vpn_ip,
                    'hostname': vpn_info['full_hostname']
                })
        
        vpn_online_count = sum(1 for d in devices_status if d['is_vpn_connected'])
        logger.debug(f"📡 Quick ping: {len(devices_status)} devices ({len(online_macs)} online, {vpn_online_count} VPN connected)")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'devices': devices_status,
            'online_count': len(online_macs),
            'vpn_count': vpn_online_count  # ✅ Compter uniquement VPN connectés
        }
        
    except Exception as e:
        logger.error(f"Quick ping failed: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'devices': [],
            'error': str(e)
        }

