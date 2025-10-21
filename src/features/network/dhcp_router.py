"""
🏠 333HOME - DHCP Router

API pour le suivi DHCP et l'historique des IPs
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from src.features.network.monitoring.dhcp_tracker import get_dhcp_tracker  # ✅ Déplacé dans monitoring/
from src.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dhcp", tags=["dhcp"])


@router.get("/summary")
async def get_dhcp_summary() -> List[Dict[str, Any]]:
    """
    Résumé de tous les devices suivis par le DHCP tracker
    
    Returns:
        Liste des devices avec leur statut DHCP actuel
    """
    try:
        tracker = get_dhcp_tracker()
        summary = tracker.get_all_devices_summary()
        return summary
    except Exception as e:
        logger.error(f"❌ Failed to get DHCP summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/device/{mac}/history")
async def get_device_ip_history(mac: str) -> List[Dict[str, Any]]:
    """
    Historique des IPs d'un device spécifique
    
    Args:
        mac: Adresse MAC du device
        
    Returns:
        Liste chronologique des IPs avec dates d'attribution/libération
    """
    try:
        tracker = get_dhcp_tracker()
        history = tracker.get_device_ip_history(mac)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No DHCP history found for MAC {mac}"
            )
        
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get IP history for {mac}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conflicts")
async def get_ip_conflicts() -> List[Dict[str, Any]]:
    """
    Détecter les conflits d'IP (même IP attribuée à plusieurs MACs)
    
    Returns:
        Liste des conflits détectés avec détails
    """
    try:
        tracker = get_dhcp_tracker()
        conflicts = tracker.get_ip_conflicts()
        return conflicts
    except Exception as e:
        logger.error(f"❌ Failed to detect IP conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pool-usage")
async def get_dhcp_pool_usage(subnet: str = "192.168.1") -> Dict[str, Any]:
    """
    Analyser l'utilisation du pool DHCP
    
    Args:
        subnet: Sous-réseau à analyser (ex: "192.168.1")
        
    Returns:
        Statistiques d'utilisation du pool DHCP
    """
    try:
        tracker = get_dhcp_tracker()
        usage = tracker.get_dhcp_pool_usage(subnet)
        return usage
    except Exception as e:
        logger.error(f"❌ Failed to get DHCP pool usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_entries(days: int = 30) -> Dict[str, Any]:
    """
    Nettoyer les entrées DHCP anciennes
    
    Args:
        days: Supprimer les devices non vus depuis N jours (default: 30)
        
    Returns:
        Nombre d'entrées supprimées
    """
    try:
        tracker = get_dhcp_tracker()
        removed = tracker.cleanup_old_entries(days)
        
        return {
            "success": True,
            "removed_entries": removed,
            "message": f"Cleaned up {removed} entries older than {days} days"
        }
    except Exception as e:
        logger.error(f"❌ Failed to cleanup DHCP entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))
