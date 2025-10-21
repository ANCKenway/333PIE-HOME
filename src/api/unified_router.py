"""
🏠 333HOME - Network API Unified Router

API REST pour le système de monitoring réseau professionnel.
Single source of truth via NetworkServiceUnified.

Endpoints:
- GET /api/network/devices - Liste tous les devices
- GET /api/network/devices/{mac} - Détails device
- GET /api/network/devices/{mac}/history - Historique device
- GET /api/network/stats - Statistiques réseau
- POST /api/network/scan - Force un scan
- GET /api/network/conflicts - Conflits détectés

Références:
- docs/NETWORK_PRO_ARCHITECTURE.md
- TODO_NETWORK_PRO.md Phase 4
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.features.network.service_unified import get_network_service


router = APIRouter(prefix="/api/network/v2", tags=["network-v2"])


# === ENDPOINTS ===

@router.get("/devices")
async def get_devices(
    online_only: bool = False,
    sources: Optional[str] = None
) -> Dict[str, Any]:
    """
    Liste tous les devices
    
    Query params:
    - online_only: Si true, retourne seulement les devices online
    - sources: Filtre par sources (ex: "nmap,arp")
    """
    service = get_network_service()
    
    if online_only:
        devices = service.get_online_devices()
    else:
        devices = service.get_all_devices()
    
    # Filtre par sources
    if sources:
        source_list = [s.strip() for s in sources.split(',')]
        devices = [
            d for d in devices
            if any(src in d.sources for src in source_list)
        ]
    
    return {
        'success': True,
        'count': len(devices),
        'devices': [d.to_dict() for d in devices]
    }


@router.get("/devices/{mac}")
async def get_device(mac: str) -> Dict[str, Any]:
    """Détails complets d'un device"""
    service = get_network_service()
    device = service.get_device(mac)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        'success': True,
        'device': device.to_dict()
    }


@router.get("/devices/{mac}/history")
async def get_device_history(mac: str) -> Dict[str, Any]:
    """Historique complet d'un device"""
    service = get_network_service()
    history = service.get_device_history(mac)
    
    if not history:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        'success': True,
        'history': history
    }


@router.get("/stats")
async def get_statistics() -> Dict[str, Any]:
    """Statistiques réseau globales"""
    service = get_network_service()
    stats = service.get_statistics()
    
    return {
        'success': True,
        'statistics': stats
    }


@router.post("/scan")
async def trigger_scan(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Force un scan réseau
    
    Le scan est lancé en background pour ne pas bloquer la requête.
    """
    service = get_network_service()
    
    # Lance le scan en background
    async def do_scan():
        await service.scan_network()
    
    background_tasks.add_task(do_scan)
    
    return {
        'success': True,
        'message': 'Scan started in background',
        'timestamp': datetime.now().isoformat()
    }


@router.get("/conflicts")
async def get_conflicts() -> Dict[str, Any]:
    """
    Liste des conflits réseau détectés
    
    Types:
    - IP duplicate: Même IP sur plusieurs MACs
    - MAC spoofing: Incohérences vendor/type
    """
    service = get_network_service()
    
    # Get conflicts from intelligence engine
    devices = service.get_all_devices()
    conflicts = service.scanner.engine.detect_conflicts(
        [d.to_dict() for d in devices]
    )
    
    return {
        'success': True,
        'count': len(conflicts),
        'conflicts': [
            {
                'type': c.conflict_type.value,
                'severity': c.severity,
                'description': c.description,
                'affected_devices': c.affected_devices,
                'detected_at': c.detected_at.isoformat(),
                'details': c.details
            }
            for c in conflicts
        ]
    }


# === MONITORING ===

@router.get("/monitoring/stats")
async def get_monitoring_stats() -> Dict[str, Any]:
    """
    Statistiques du service de monitoring
    
    Returns:
        État du monitoring + métriques
    """
    from src.features.network.monitoring_service import get_monitoring_service
    
    monitoring = get_monitoring_service()
    return {
        'success': True,
        **monitoring.get_stats()
    }


# === HEALTH CHECK ===

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check du service réseau"""
    service = get_network_service()
    stats = service.get_statistics()
    
    return {
        'success': True,
        'status': 'healthy',
        'service': 'NetworkServiceUnified',
        'total_devices': stats['total_devices'],
        'online_devices': stats['online_devices'],
        'last_scan': stats.get('last_scan')
    }
