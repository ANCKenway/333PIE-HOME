"""
🌐 333HOME - Network Registry Router
Endpoints pour le registry réseau (source unique de vérité)

Le registry est le fichier persistant qui stocke TOUS les devices
jamais détectés avec leur historique complet (IP, hostname, présence).
"""

import logging
import subprocess
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..registry import get_network_registry
from ..schemas import DeviceRegistryResponse, RegistryStatistics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/registry", tags=["network-registry"])


def get_local_mac_address() -> Optional[str]:
    """
    Détecter automatiquement la MAC address de l'interface réseau principale
    
    Returns:
        MAC address en majuscules (ex: "88:A2:9E:3B:20:31") ou None si erreur
    """
    try:
        # Méthode 1: Via ip link (Linux)
        result = subprocess.run(
            ['ip', 'link', 'show'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                # Chercher ligne avec "link/ether" et état UP
                if 'link/ether' in line.lower() and 'state up' in result.stdout.lower():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        mac = parts[1].upper()
                        logger.info(f"🔍 MAC locale détectée: {mac}")
                        return mac
        
        # Méthode 2: Fallback via /sys/class/net
        import os
        for iface in os.listdir('/sys/class/net'):
            if iface.startswith(('eth', 'wlan', 'en')):
                try:
                    with open(f'/sys/class/net/{iface}/address', 'r') as f:
                        mac = f.read().strip().upper()
                        logger.info(f"🔍 MAC locale détectée ({iface}): {mac}")
                        return mac
                except:
                    continue
                    
    except Exception as e:
        logger.warning(f"⚠️  Impossible de détecter MAC locale: {e}")
    
    return None


@router.get(
    "/",
    response_model=DeviceRegistryResponse,
    summary="Get All Registry Devices",
    description="""
    Récupérer TOUS les devices du registry avec leur historique complet.
    
    Le registry est la SOURCE UNIQUE de vérité pour les devices réseau.
    Chaque scan ENRICHIT ce registry au lieu de créer une liste temporaire.
    
    Utiliser ce endpoint pour :
    - Dashboard temps réel (afficher tous les devices connus)
    - Timeline d'événements (IP/hostname changes)
    - Détection DHCP changes
    - Historique de présence/absence
    """
)
async def get_all_registry_devices(
    online_only: bool = Query(False, description="Filtrer uniquement les devices online"),
    vpn_only: bool = Query(False, description="Filtrer uniquement les devices VPN"),
    managed_only: bool = Query(False, description="Filtrer uniquement les devices gérés"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Nombre max de devices")
):
    """
    Récupérer tous les devices du registry avec filtres optionnels.
    """
    try:
        registry = get_network_registry()
        devices = registry.get_all_devices()
        
        # Filtres
        if online_only:
            devices = [d for d in devices if d.get('is_online')]
        
        if vpn_only:
            devices = [d for d in devices if d.get('is_vpn_connected')]
        
        if managed_only:
            devices = [d for d in devices if d.get('is_managed')]
        
        # Trier par last_seen (plus récents en premier)
        devices = sorted(
            devices,
            key=lambda d: d.get('last_seen', ''),
            reverse=True
        )
        
        # Limiter si demandé
        if limit:
            devices = devices[:limit]
        
        logger.info(f"📊 Registry query: {len(devices)} devices (online_only={online_only}, vpn_only={vpn_only})")
        
        return DeviceRegistryResponse(
            total=len(devices),
            devices=devices,
            filters_applied={
                'online_only': online_only,
                'vpn_only': vpn_only,
                'managed_only': managed_only,
                'limit': limit
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Error fetching registry devices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération registry: {str(e)}"
        )


@router.get(
    "/device/{mac}",
    summary="Get Device By MAC",
    description="Récupérer un device spécifique avec son historique complet"
)
async def get_device_by_mac(mac: str):
    """
    Récupérer un device spécifique du registry par son adresse MAC.
    Retourne son historique complet (IP changes, hostname changes, etc.)
    """
    try:
        registry = get_network_registry()
        device = registry.get_device(mac)
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail=f"Device {mac} non trouvé dans le registry"
            )
        
        return device
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching device {mac}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération device: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=RegistryStatistics,
    summary="Get Registry Statistics",
    description="Statistiques globales du registry (total, online, DHCP dynamic, etc.)"
)
async def get_registry_statistics():
    """
    Récupérer les statistiques globales du registry.
    """
    try:
        registry = get_network_registry()
        stats = registry.get_statistics()
        
        logger.info(f"📊 Registry stats: {stats['total_devices']} devices, {stats['online']} online")
        
        return RegistryStatistics(**stats)
    
    except Exception as e:
        logger.error(f"❌ Error fetching registry statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération statistics: {str(e)}"
        )


@router.get(
    "/recent-changes",
    summary="Get Recent Changes",
    description="Récupérer les devices triés par activité récente (pour timeline)"
)
async def get_recent_changes(
    limit: int = Query(50, ge=1, le=200, description="Nombre de devices à retourner")
):
    """
    Récupérer les devices récemment actifs (triés par last_seen).
    Utile pour timeline d'événements dans le dashboard.
    """
    try:
        registry = get_network_registry()
        recent = registry.get_recent_changes(limit=limit)
        
        logger.info(f"📊 Recent changes: {len(recent)} devices")
        
        return {
            'total': len(recent),
            'limit': limit,
            'devices': recent
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching recent changes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération recent changes: {str(e)}"
        )


@router.post(
    "/device/{mac}/manage",
    summary="Mark Device As Managed",
    description="Marquer un device comme géré (visible dans l'onglet Appareils)"
)
async def mark_device_as_managed(mac: str, managed: bool = True):
    """
    Marquer un device comme géré dans l'application.
    Les devices gérés apparaissent dans l'onglet "Appareils".
    """
    try:
        registry = get_network_registry()
        registry.mark_as_managed(mac, managed=managed)
        
        logger.info(f"✅ Device {mac} marked as {'managed' if managed else 'unmanaged'}")
        
        return {
            'success': True,
            'mac': mac,
            'managed': managed
        }
    
    except Exception as e:
        logger.error(f"❌ Error marking device {mac}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur marquage device: {str(e)}"
        )


@router.post(
    "/refresh",
    summary="🔄 Refresh Registry Status",
    description="""
    Refresh léger du registry : ARP + Tailscale status (pas de scan nmap).
    
    Ultra-rapide (<1s) : vérifie uniquement online/offline + VPN status.
    Parfait pour monitoring temps réel toutes les 30s.
    """
)
async def refresh_registry_status():
    """
    Refresh rapide du registry : ARP cache + Tailscale status.
    
    Met à jour :
    - is_online (via ARP cache)
    - is_vpn_connected (via Tailscale API)
    - last_seen (timestamp)
    
    Returns:
        Statistiques du refresh
    """
    try:
        from ..scanners.arp_scanner import ARPScanner
        from ..scanners.tailscale_scanner import TailscaleScanner
        
        registry = get_network_registry()
        
        logger.info("🔄 Registry refresh START (ARP + Tailscale)")
        
        # 1. ARP scan rapide (cache système)
        arp_scanner = ARPScanner("192.168.1.0/24")
        arp_devices = await arp_scanner.scan()
        
        # 2. Récupérer VPN data (Tailscale)
        ts_scanner = TailscaleScanner("192.168.1.0/24")
        vpn_map = await ts_scanner.scan()
        
        # 3. Compter devices
        online_count = 0
        vpn_count = 0
        agent_count = 0
        updated_count = 0
        
        # ✅ Détecter notre propre MAC dynamiquement (pas de hardcode)
        local_mac = get_local_mac_address()
        
        for mac, device in registry.devices.items():
            changed = False
            
            # ✅ Exception pour Self (nous-mêmes) : toujours online
            is_self = (local_mac and mac.upper() == local_mac.upper())
            
            if is_self:
                # Nous-mêmes : toujours online
                if not device.is_online:
                    device.is_online = True
                    changed = True
                online_count += 1
                
                # ✅ Mettre à jour last_seen pour le device local (temps réel)
                from datetime import datetime, timezone
                now_iso = datetime.now(timezone.utc).isoformat()
                device.last_seen = now_iso
                device.last_seen_online = now_iso
                changed = True
                # Note: IP/hostname seront enrichis par le VPN matching ci-dessous
            else:
                # Autres devices : check ARP
                arp_device = next((d for d in arp_devices if d.mac.upper() == mac), None)
                new_online = arp_device is not None
                
                if device.is_online != new_online:
                    device.is_online = new_online
                    changed = True
                
                if new_online:
                    online_count += 1
                    if arp_device:
                        # Update IP/hostname si changé
                        new_ip = arp_device.ip
                        new_hostname = arp_device.hostname
                        if new_ip and new_ip != device.current_ip:
                            device.current_ip = new_ip
                            changed = True
                        if new_hostname and new_hostname != device.current_hostname:
                            device.current_hostname = new_hostname
                            changed = True
                        
                        # ✅ Mettre à jour last_seen pour devices online (temps réel)
                        from datetime import datetime, timezone
                        now_iso = datetime.now(timezone.utc).isoformat()
                        device.last_seen = now_iso
                        device.last_seen_online = now_iso
                        changed = True
            
            # ✅ Enrichir hostname depuis devices managés si manquant
            if not device.current_hostname and device.is_managed:
                # Récupérer le nom depuis devices.json
                from ...devices.manager import DeviceManager
                device_manager = DeviceManager()
                managed_device = device_manager.get_device_by_mac(mac)
                if managed_device and managed_device.get('name'):
                    device.current_hostname = managed_device['name']
                    changed = True
                    logger.debug(f"✅ Hostname enrichi depuis device managé: {mac} → {device.current_hostname}")
            
            # Check VPN status
            hostname_upper = (device.current_hostname or '').upper()
            
            if hostname_upper in vpn_map:
                vpn_info = vpn_map[hostname_upper]
                device.vpn_ip = vpn_info.get('vpn_ip')
                device.is_vpn_connected = vpn_info.get('is_online', False)
                if device.is_vpn_connected:
                    vpn_count += 1
                changed = True
            else:
                if device.is_vpn_connected:
                    device.is_vpn_connected = False
                    changed = True
            
            # ✅ Check Agent status (croisement par IP ou hostname)
            from ...agents.routers.agents_router import agent_manager
            agent_found = False
            
            for agent in agent_manager.connections.values():
                agent_hostname = agent.metadata.get('hostname', '').upper()
                agent_ip = agent.metadata.get('ip')
                
                # Match par hostname OU IP
                if (device.current_hostname and agent_hostname == device.current_hostname.upper()) or \
                   (device.current_ip and agent_ip == device.current_ip):
                    device.is_agent_connected = True
                    device.agent_id = agent.agent_id
                    device.agent_version = agent.metadata.get('version')
                    agent_found = True
                    agent_count += 1
                    changed = True
                    break
            
            # Reset si agent non trouvé
            if not agent_found and device.is_agent_connected:
                device.is_agent_connected = False
                device.agent_id = None
                device.agent_version = None
                changed = True
            
            if changed:
                updated_count += 1
        
        # 5. Sauvegarder
        registry._save()
        
        logger.info(
            f"✅ Registry refresh DONE: {online_count} online, {vpn_count} VPN, "
            f"{agent_count} agents, {updated_count} updated"
        )
        
        return {
            'success': True,
            'total_devices': len(registry.devices),
            'online_count': online_count,
            'vpn_count': vpn_count,
            'agent_count': agent_count,
            'updated_count': updated_count,
            'duration_ms': 0  # Calculer si besoin
        }
    
    except Exception as e:
        logger.error(f"❌ Error refreshing registry: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur refresh registry: {str(e)}"
        )
