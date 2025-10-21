"""
🌐 333HOME - Network Scan Router
Endpoints pour les scans réseau

⚠️ SCANS ON-DEMAND uniquement (pas de background)
🎯 Utilise MultiSourceScanner (nmap+ARP+mDNS+NetBIOS) pour hostname detection avancée
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..schemas import ScanRequest, ScanResult, NetworkDeviceCreate
from ..scanners.multi_source import MultiSourceScanner  # ✅ Déplacé dans scanners/
from ..storage import save_scan_result, get_all_devices, get_device_by_mac
from ..history import NetworkHistory
from ..registry import NetworkRegistry
from src.core.models.unified_device import DeviceStatus


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scan", tags=["network-scan"])

# Scan en cours (éviter doublons)
_current_scan: Optional[ScanResult] = None
_scan_in_progress = False


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
        logger.info(f"🌐 Starting MULTI-SOURCE network scan: {scan_request.scan_type}")
        
        # Créer le MultiSourceScanner (avec NetBIOS pour Windows!)
        scanner = MultiSourceScanner(subnet=scan_request.subnet)
        
        # Activer/désactiver sources selon scan_type
        if scan_request.scan_type.value == "quick":
            scanner.enabled_sources['nmap'] = False  # Skip nmap pour quick
            logger.info("⚡ Quick scan: ARP + mDNS + NetBIOS only")
        elif scan_request.scan_type.value == "arp_only":
            scanner.enabled_sources.update({'nmap': False, 'mdns': False, 'netbios': False})
            logger.info("⚡ ARP-only scan")
        elif scan_request.scan_type.value == "mdns_only":
            scanner.enabled_sources.update({'nmap': False, 'arp': False, 'netbios': False})
            logger.info("⚡ mDNS-only scan")
        else:
            logger.info("🔥 Full scan: nmap + ARP + mDNS + NetBIOS")
        
        # Lancer le scan multi-sources
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
                vpn_hostname=ud.vpn_hostname
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
        registry = NetworkRegistry()
        
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


@router.get("/registry")
async def get_network_registry() -> dict:
    """
    Récupérer le Network Registry complet
    
    Le registry contient TOUS les devices jamais vus avec leur historique.
    C'est le fichier central de suivi persistant du réseau.
    """
    try:
        registry = NetworkRegistry()
        devices = registry.get_all_devices()
        stats = registry.get_statistics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'devices': devices
        }
    except Exception as e:
        logger.error(f"Registry read failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/{mac}")
async def get_device_history(mac: str) -> dict:
    """
    Récupérer l'historique complet d'un device
    
    Args:
        mac: Adresse MAC du device
        
    Returns:
        Historique complet (IPs, hostnames, détections)
    """
    try:
        registry = NetworkRegistry()
        device = registry.get_device(mac)
        
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {mac} not found in registry")
        
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Device history read failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/stats")
async def get_registry_statistics() -> dict:
    """
    Statistiques globales du registry
    
    Returns:
        Stats: total, online, offline, VPN, managed, DHCP dynamics
    """
    try:
        registry = NetworkRegistry()
        return registry.get_statistics()
    except Exception as e:
        logger.error(f"Registry stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
