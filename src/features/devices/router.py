"""
📱 333HOME - Devices API Router
Routes API pour la gestion des appareils
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends

from src.core import get_logger
from src.shared import DeviceError, NetworkError
from .schemas import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    WakeOnLanRequest,
    DeviceStatusSummary
)
from .manager import DeviceManager
from .monitor import DeviceMonitor
from .wol import WakeOnLanService


logger = get_logger(__name__)
router = APIRouter(prefix="/devices", tags=["devices"])

# Instances globales
device_manager = DeviceManager()
device_monitor = DeviceMonitor()
wol_service = WakeOnLanService()


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(check_status: bool = True):
    """
    Lister tous les appareils
    
    Args:
        check_status: Si True, vérifie le statut online/offline depuis NetworkRegistry (Phase 6)
    """
    try:
        devices = device_manager.get_all_devices()
        
        if check_status:
            devices = await device_monitor.check_multiple_devices(devices)
        
        logger.info(f"📱 {len(devices)} appareils listés")
        return devices
        
    except Exception as e:
        logger.error(f"❌ Erreur liste appareils: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/summary", response_model=DeviceStatusSummary)
async def get_devices_summary():
    """Obtenir un résumé du statut de tous les appareils"""
    try:
        devices = device_manager.get_all_devices()
        devices_with_status = await device_monitor.check_multiple_devices(devices)
        summary = device_monitor.get_status_summary(devices_with_status)
        
        return {
            **summary,
            "last_update": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur résumé appareils: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, check_status: bool = True):
    """
    Récupérer un appareil par son ID
    
    Args:
        device_id: ID de l'appareil
        check_status: Si True, vérifie le statut online/offline
    """
    try:
        device = device_manager.get_device(device_id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appareil non trouvé: {device_id}"
            )
        
        if check_status:
            device = await device_monitor.check_device_status(device)
        
        return device
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération appareil {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate):
    """Créer un nouvel appareil"""
    try:
        device_dict = device.model_dump()
        new_device = device_manager.create_device(device_dict)
        
        logger.info(f"✅ Appareil créé: {new_device['name']}")
        return new_device
        
    except DeviceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Erreur création appareil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: str, device_update: DeviceUpdate):
    """Mettre à jour un appareil"""
    try:
        update_data = device_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune donnée à mettre à jour"
            )
        
        updated_device = device_manager.update_device(device_id, update_data)
        
        logger.info(f"✅ Appareil mis à jour: {device_id}")
        return updated_device
        
    except DeviceError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour appareil {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: str):
    """Supprimer un appareil"""
    try:
        device_manager.delete_device(device_id)
        logger.info(f"🗑️ Appareil supprimé: {device_id}")
        
    except DeviceError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Erreur suppression appareil {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{device_id}/wake", status_code=status.HTTP_200_OK)
async def wake_device(device_id: str):
    """
    Réveiller un appareil via Wake-on-LAN
    
    L'appareil doit avoir une adresse MAC configurée
    """
    try:
        device = device_manager.get_device(device_id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appareil non trouvé: {device_id}"
            )
        
        mac = device.get('mac')
        if not mac:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appareil sans adresse MAC configurée"
            )
        
        await wol_service.wake(mac)
        
        logger.info(f"⚡ Wake-on-LAN envoyé à {device['name']} ({mac})")
        return {
            "message": "Magic packet envoyé avec succès",
            "device_id": device_id,
            "mac": mac
        }
        
    except NetworkError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur Wake-on-LAN pour {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/wake", status_code=status.HTTP_200_OK)
async def wake_custom(wol_request: WakeOnLanRequest):
    """
    Envoyer un magic packet Wake-on-LAN personnalisé
    
    Permet de réveiller un appareil sans l'avoir configuré dans l'application
    """
    try:
        await wol_service.wake(
            mac=wol_request.mac,
            broadcast=wol_request.broadcast,
            port=wol_request.port
        )
        
        logger.info(f"⚡ Magic packet envoyé à {wol_request.mac}")
        return {
            "message": "Magic packet envoyé avec succès",
            "mac": wol_request.mac,
            "broadcast": wol_request.broadcast,
            "port": wol_request.port
        }
        
    except NetworkError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Erreur Wake-on-LAN: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{device_id}/ping", status_code=status.HTTP_200_OK)
async def ping_device(device_id: str):
    """
    Pinger un appareil pour vérifier sa connectivité
    """
    try:
        device = device_manager.get_device(device_id)
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appareil non trouvé: {device_id}"
            )
        
        ip = device.get('ip')
        if not ip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appareil sans adresse IP"
            )
        
        online = await device_monitor.ping(ip)
        
        return {
            "device_id": device_id,
            "ip": ip,
            "online": online,
            "status": "online" if online else "offline"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur ping appareil {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
