"""
API endpoints pour la découverte réseau
Version unifiée avec scanner exhaustif
"""

from fastapi import APIRouter, HTTPException
from ..services.network_unified import UnifiedNetworkScanner

router = APIRouter()

# Instance du scanner unifié
scanner = UnifiedNetworkScanner()

@router.get("/scan") 
async def scan_network():
    """Scan COMPLET et EXHAUSTIF du réseau - détecte tout"""
    try:
        devices = scanner.scan_complete_network()
        return {
            "success": True,
            "count": len(devices),
            "devices": devices,
            "scan_type": "exhaustive"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur scan: {str(e)}")

@router.get("/discover")
async def discover_network():
    """Alias pour scan complet - même fonctionnalité"""
    try:
        devices = scanner.scan_complete_network()
        
        return {
            "success": True,
            "count": len(devices),
            "devices": devices,
            "scan_type": "unified_exhaustive"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur découverte: {str(e)}")

@router.get("/device/{ip}")
async def get_device_info(ip: str):
    """Informations EXHAUSTIVES d'un appareil spécifique"""
    try:
        device = scanner._scan_device_exhaustive(ip)
        if not device:
            raise HTTPException(status_code=404, detail="Appareil non trouvé ou hors ligne")
        
        return {
            "success": True,
            "device": device
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")