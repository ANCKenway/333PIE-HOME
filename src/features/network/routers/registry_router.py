"""
🌐 333HOME - Network Registry Router
Endpoints pour le registry réseau (source unique de vérité)

Le registry est le fichier persistant qui stocke TOUS les devices
jamais détectés avec leur historique complet (IP, hostname, présence).
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..registry import NetworkRegistry
from ..schemas import DeviceRegistryResponse, RegistryStatistics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/registry", tags=["network-registry"])


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
        registry = NetworkRegistry()
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
        registry = NetworkRegistry()
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
        registry = NetworkRegistry()
        stats = registry.get_statistics()
        
        logger.debug(f"📊 Registry stats: {stats['total_devices']} devices, {stats['online']} online")
        
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
        registry = NetworkRegistry()
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
        registry = NetworkRegistry()
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
