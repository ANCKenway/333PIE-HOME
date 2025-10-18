"""
API endpoints pour le scanner réseau avancé
FastAPI moderne pour l'interface web
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
import sys
import os

# Ajouter le répertoire racine au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.network import network_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/network", tags=["network-scanner"])

# ===== MODÈLES PYDANTIC =====

class ScanRequest(BaseModel):
    network: Optional[str] = None
    include_ports: bool = True
    background: bool = False

class AddDeviceRequest(BaseModel):
    ip: str
    name: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    device_type: Optional[str] = None
    description: Optional[str] = None

# Stockage des tâches de scan en cours
active_scans = {}

# ===== ENDPOINTS =====

@router.get("/interfaces", summary="Interfaces réseau")
async def get_network_interfaces():
    """Récupérer les interfaces réseau disponibles"""
    try:
        result = network_api.get_network_interfaces()
        return result
    except Exception as e:
        logger.error(f"Erreur récupération interfaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan", summary="Scanner réseau (GET)")
async def scan_network_get(
    network: Optional[str] = Query(None, description="Réseau à scanner (ex: 192.168.1.0/24)"),
    include_ports: bool = Query(True, description="Inclure le scan des ports"),
    quick: bool = Query(False, description="Scan rapide uniquement")
):
    """Scanner le réseau via GET avec paramètres"""
    try:
        if quick:
            result = network_api.quick_scan(network)
        else:
            result = network_api.scan_network(network, include_ports)
        return result
    except Exception as e:
        logger.error(f"Erreur scan GET: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan", summary="Scanner réseau (POST)")
async def scan_network_post(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks
):
    """Scanner le réseau avec configuration avancée"""
    try:
        if scan_request.background:
            # Scan en arrière-plan (pour les gros réseaux)
            scan_id = f"scan_{len(active_scans) + 1}"
            active_scans[scan_id] = {"status": "running", "progress": 0}
            
            def run_background_scan():
                try:
                    result = network_api.scan_network(scan_request.network, scan_request.include_ports)
                    active_scans[scan_id] = {
                        "status": "completed",
                        "result": result,
                        "progress": 100
                    }
                except Exception as e:
                    active_scans[scan_id] = {
                        "status": "error",
                        "error": str(e),
                        "progress": 0
                    }
            
            background_tasks.add_task(run_background_scan)
            
            return {
                "success": True,
                "scan_id": scan_id,
                "message": "Scan démarré en arrière-plan"
            }
        else:
            # Scan synchrone
            result = network_api.scan_network(scan_request.network, scan_request.include_ports)
            return result
            
    except Exception as e:
        logger.error(f"Erreur scan POST: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan/quick", summary="Scan rapide")
async def quick_network_scan(
    network: Optional[str] = Query(None, description="Réseau à scanner")
):
    """Scan rapide sans ports (ping + ARP uniquement)"""
    try:
        result = network_api.quick_scan(network)
        return result
    except Exception as e:
        logger.error(f"Erreur scan rapide: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scan/{scan_id}/status", summary="Statut scan")
async def get_scan_status(scan_id: str):
    """Récupérer le statut d'un scan en arrière-plan"""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    return {
        "success": True,
        "data": active_scans[scan_id]
    }

@router.get("/devices", summary="Appareils découverts")
async def get_discovered_devices():
    """Récupérer les appareils découverts lors du dernier scan"""
    try:
        result = network_api.get_scan_history()
        return result
    except Exception as e:
        logger.error(f"Erreur récupération appareils: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/{ip}", summary="Info appareil par IP")
async def get_device_info(ip: str):
    """Récupérer les informations détaillées d'un appareil par IP"""
    try:
        result = network_api.get_device_info(ip, 'ip')
        return result
    except Exception as e:
        logger.error(f"Erreur récupération info appareil: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/mac/{mac}", summary="Info appareil par MAC")
async def get_device_info_by_mac(mac: str):
    """Récupérer les informations détaillées d'un appareil par MAC"""
    try:
        result = network_api.get_device_info(mac, 'mac')
        return result
    except Exception as e:
        logger.error(f"Erreur récupération info appareil par MAC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vendor/{mac}", summary="Info fabricant MAC")
async def get_mac_vendor(mac: str):
    """Récupérer les informations du fabricant pour une adresse MAC"""
    try:
        result = network_api.get_vendor_info(mac)
        return result
    except Exception as e:
        logger.error(f"Erreur récupération vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export", summary="Exporter résultats")
async def export_scan_results(
    format: str = Query("json", description="Format d'export (json ou text)")
):
    """Exporter les résultats du dernier scan"""
    try:
        if format not in ["json", "text"]:
            raise HTTPException(status_code=400, detail="Format non supporté")
        
        result = network_api.export_scan_results(format)
        return result
    except Exception as e:
        logger.error(f"Erreur export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache", summary="Vider cache")
async def clear_cache():
    """Vider le cache des vendors MAC"""
    try:
        result = network_api.clear_cache()
        return result
    except Exception as e:
        logger.error(f"Erreur vidage cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats", summary="Stats cache")
async def get_cache_stats():
    """Récupérer les statistiques du cache"""
    try:
        result = network_api.get_cache_stats()
        return result
    except Exception as e:
        logger.error(f"Erreur stats cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/add", summary="Ajouter appareil")
async def add_device_to_managed(device_data: AddDeviceRequest):
    """Ajouter un appareil découvert à la liste des appareils gérés"""
    try:
        # TODO: Intégrer avec le système de gestion des appareils existant
        # Pour l'instant, on retourne une confirmation
        
        return {
            "success": True,
            "message": f"Appareil {device_data.name} ajouté à la gestion",
            "device": device_data.dict()
        }
        
    except Exception as e:
        logger.error(f"Erreur ajout appareil: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", summary="Statistiques réseau")
async def get_network_statistics():
    """Récupérer les statistiques du réseau et des scans"""
    try:
        scan_history = network_api.get_scan_history()
        cache_stats = network_api.get_cache_stats()
        
        statistics = {
            "scan_available": scan_history['success'] and scan_history['data'] is not None,
            "cache_stats": cache_stats['data'] if cache_stats['success'] else {},
            "active_scans": len(active_scans)
        }
        
        if scan_history['success'] and scan_history['data']:
            last_scan = scan_history['data']['last_scan']
            if 'device_analysis' in last_scan:
                statistics['device_analysis'] = last_scan['device_analysis']
            if 'statistics' in last_scan:
                statistics['scan_stats'] = last_scan['statistics']
        
        return {
            "success": True,
            "data": statistics
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {e}")
        raise HTTPException(status_code=500, detail=str(e))