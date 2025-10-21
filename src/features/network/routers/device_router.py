"""
🌐 333HOME - Network Device Router
Endpoints pour les devices réseau
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from ..schemas import (
    NetworkDevice,
    DeviceHistory,
    NetworkTimeline,
    NetworkStats,
    PromoteToDevicesRequest,
    PromoteToDevicesResponse,
    NetworkEventType,
    NetworkEvent,
)
from ..storage import (
    get_all_devices,
    get_device_by_mac,
    update_device_in_devices_flag,
)
from ..history import NetworkHistory


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["network-devices"])


@router.get("", response_model=List[NetworkDevice])
async def get_network_devices(
    online_only: bool = Query(False, description="Afficher uniquement les devices en ligne"),
) -> List[NetworkDevice]:
    """
    Liste tous les devices réseau
    
    Args:
        online_only: Filtrer uniquement les online
        
    Returns:
        Liste des NetworkDevice
    """
    try:
        devices = get_all_devices()
        
        if online_only:
            devices = [d for d in devices if d.currently_online]
        
        # Trier par last_seen (plus récent en premier)
        devices.sort(key=lambda d: d.last_seen, reverse=True)
        
        logger.debug(f"📱 Returning {len(devices)} network devices")
        return devices
    
    except Exception as e:
        logger.error(f"❌ Error getting devices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération devices: {str(e)}"
        )


@router.get("/history/{mac}", response_model=DeviceHistory)
async def get_device_history(mac: str) -> DeviceHistory:
    """
    Historique complet d'un device
    
    Args:
        mac: Adresse MAC
        
    Returns:
        DeviceHistory avec événements, IP history, etc.
    """
    try:
        history = NetworkHistory()
        device_history = history.get_device_history(mac)
        
        if not device_history:
            raise HTTPException(
                status_code=404,
                detail=f"Device {mac} non trouvé"
            )
        
        return device_history
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting device history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération historique: {str(e)}"
        )


@router.get("/timeline", response_model=NetworkTimeline)
async def get_network_timeline(
    hours: int = Query(24, ge=1, le=168, description="Nombre d'heures"),
    device_mac: Optional[str] = Query(None, description="Filtrer par MAC"),
) -> NetworkTimeline:
    """
    Timeline des événements réseau
    
    Args:
        hours: Nombre d'heures à récupérer (1-168)
        device_mac: Filtrer par MAC (optionnel)
        
    Returns:
        NetworkTimeline avec tous les événements
    """
    try:
        history = NetworkHistory()
        timeline = history.get_timeline(hours=hours, device_mac=device_mac)
        
        return timeline
    
    except Exception as e:
        logger.error(f"❌ Error getting timeline: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération timeline: {str(e)}"
        )


@router.post("/{mac}/promote", response_model=PromoteToDevicesResponse)
async def promote_to_devices(
    mac: str,
    request: PromoteToDevicesRequest,
) -> PromoteToDevicesResponse:
    """
    Promouvoir un device réseau vers Devices (favoris)
    
    Args:
        mac: Adresse MAC
        request: Configuration du device
        
    Returns:
        PromoteToDevicesResponse avec l'ID du device créé
    """
    try:
        # Vérifier que le device existe
        network_device = get_device_by_mac(mac)
        if not network_device:
            raise HTTPException(
                status_code=404,
                detail=f"Device {mac} non trouvé"
            )
        
        # Importer le manager Devices
        from src.features.devices.manager import DeviceManager
        from src.features.devices.schemas import DeviceCreate
        
        device_manager = DeviceManager()
        
        # Créer le device dans Devices
        device_name = request.name or network_device.current_hostname or f"Device {mac}"
        
        device_create = DeviceCreate(
            name=device_name,
            ip=network_device.current_ip,
            mac=mac,
            type=request.type or network_device.device_type or "other",
            description=request.description or f"Promoted from network ({network_device.vendor})",
            tags=request.tags,
        )
        
        new_device = device_manager.create_device(device_create)
        
        # Marquer comme in_devices
        update_device_in_devices_flag(mac, True)
        
        # Log l'événement
        history = NetworkHistory()
        event = NetworkEvent(
            event_id=f"event_{mac}_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            event_type=NetworkEventType.DEVICE_PROMOTED,
            device_mac=mac,
            device_name=device_name,
            details={
                "device_id": new_device.id,
                "promoted_to": "devices",
            },
        )
        history._save_event(event)
        
        logger.info(f"✅ Device {mac} promoted to Devices: {new_device.id}")
        
        return PromoteToDevicesResponse(
            success=True,
            message=f"Device {device_name} ajouté aux favoris",
            device_id=new_device.id,
            network_device_id=network_device.id,
            device_name=device_name,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error promoting device: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur promotion device: {str(e)}"
        )


@router.get("/stats", response_model=NetworkStats)
async def get_network_stats() -> NetworkStats:
    """
    Statistiques réseau globales
    
    Returns:
        NetworkStats avec toutes les métriques
    """
    try:
        history = NetworkHistory()
        stats = history.get_network_stats()
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération stats: {str(e)}"
        )
