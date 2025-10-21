"""
🏠 333HOME - Hub Router

API unifiée qui agrège toutes les sources de données
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from src.features.hub.unified_service import (
    get_unified_devices,
    get_unified_device_by_mac,
    get_unified_device_by_id,
    get_devices_stats,
)
from src.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/hub", tags=["hub"])


@router.get("/devices")
async def get_all_unified_devices() -> List[Dict[str, Any]]:
    """
    Liste tous les devices unifiés (devices.json + network + tailscale)
    
    Returns:
        Liste complète des devices avec toutes les infos
    """
    try:
        devices = get_unified_devices()
        result = [d.to_dict() for d in devices]
        logger.info(f"📊 Returning {len(result)} unified devices")
        return result
    except Exception as e:
        logger.error(f"❌ Error getting unified devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}")
async def get_unified_device(device_id: str) -> Dict[str, Any]:
    """
    Récupère un device unifié par ID
    
    Args:
        device_id: ID du device
        
    Returns:
        Device avec toutes les infos
    """
    try:
        device = get_unified_device_by_id(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return device.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/mac/{mac}")
async def get_unified_device_by_mac_address(mac: str) -> Dict[str, Any]:
    """
    Récupère un device unifié par MAC
    
    Args:
        mac: Adresse MAC
        
    Returns:
        Device avec toutes les infos
    """
    try:
        device = get_unified_device_by_mac(mac)
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return device.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting device by MAC {mac}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_hub_stats() -> Dict[str, Any]:
    """
    Stats globales du HUB
    
    Returns:
        Statistiques agrégées
    """
    try:
        stats = get_devices_stats()
        logger.debug(f"📊 Hub stats: {stats}")
        return {
            'devices': stats,
            'timestamp': datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"❌ Error getting hub stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

