"""
🌐 333HOME - Network Bandwidth Router
Endpoints pour monitoring bande passante
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..bandwidth_monitor import get_bandwidth_monitor


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bandwidth", tags=["network-bandwidth"])


@router.get("/stats", response_model=dict)
async def get_bandwidth_stats(
    mac: Optional[str] = Query(None, description="MAC address (None = all)")
) -> dict:
    """
    Récupère les statistiques de bande passante
    
    Args:
        mac: Adresse MAC (optionnel, None = tous)
        
    Returns:
        Statistiques bandwidth
    """
    try:
        monitor = get_bandwidth_monitor()
        
        if mac:
            # Stats pour un device spécifique
            stats = monitor.get_stats(mac)
            if not stats:
                raise HTTPException(
                    status_code=404,
                    detail=f"Device not found: {mac}"
                )
            
            return {
                "device": {
                    "ip": stats.ip,
                    "mac": stats.mac,
                    "hostname": stats.hostname,
                    "current": {
                        "upload_mbps": stats.current_upload_bps / (1024 * 1024),
                        "download_mbps": stats.current_download_bps / (1024 * 1024),
                        "total_mbps": stats.current_mbps,
                    },
                    "total": {
                        "bytes_sent": stats.total_bytes_sent,
                        "bytes_received": stats.total_bytes_received,
                        "total_mb": stats.total_mb,
                    },
                    "average": {
                        "upload_mbps": stats.avg_upload_bps / (1024 * 1024),
                        "download_mbps": stats.avg_download_bps / (1024 * 1024),
                        "total_mbps": stats.avg_mbps,
                    },
                    "peak": {
                        "mbps": stats.peak_mbps,
                        "timestamp": stats.peak_timestamp,
                    },
                    "uptime_seconds": stats.uptime_seconds,
                    "sample_count": stats.sample_count,
                }
            }
        else:
            # Stats globales
            all_stats = monitor.get_all_stats()
            network_total = monitor.get_total_bandwidth()
            
            return {
                "network": network_total,
                "devices_count": len(all_stats),
                "devices": [
                    {
                        "ip": s.ip,
                        "mac": s.mac,
                        "hostname": s.hostname,
                        "current_mbps": s.current_mbps,
                        "total_mb": s.total_mb,
                    }
                    for s in all_stats
                ]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting bandwidth stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération stats bandwidth: {str(e)}"
        )


@router.get("/top-talkers", response_model=dict)
async def get_top_talkers(
    limit: int = Query(10, ge=1, le=50),
    sort_by: str = Query("total", regex="^(total|upload|download|current)$")
) -> dict:
    """
    Récupère les top talkers (devices avec plus de traffic)
    
    Args:
        limit: Nombre max de devices
        sort_by: Critère (total/upload/download/current)
        
    Returns:
        Liste des top talkers
    """
    try:
        monitor = get_bandwidth_monitor()
        top_devices = monitor.get_top_talkers(limit=limit, sort_by=sort_by)
        
        return {
            "sort_by": sort_by,
            "count": len(top_devices),
            "top_talkers": [
                {
                    "rank": idx + 1,
                    "ip": stats.ip,
                    "mac": stats.mac,
                    "hostname": stats.hostname,
                    "current_mbps": stats.current_mbps,
                    "total_mb": stats.total_mb,
                    "total_bytes_sent": stats.total_bytes_sent,
                    "total_bytes_received": stats.total_bytes_received,
                    "peak_mbps": stats.peak_mbps,
                }
                for idx, stats in enumerate(top_devices)
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting top talkers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération top talkers: {str(e)}"
        )


@router.post("/register", response_model=dict)
async def register_device_bandwidth(
    ip: str,
    mac: str,
    hostname: Optional[str] = None
) -> dict:
    """
    Enregistre un device pour monitoring bandwidth
    
    Args:
        ip: Adresse IP
        mac: Adresse MAC
        hostname: Hostname optionnel
        
    Returns:
        Confirmation
    """
    try:
        monitor = get_bandwidth_monitor()
        stats = monitor.register_device(ip, mac, hostname)
        
        logger.info(f"📊 Device registered for bandwidth: {ip} ({mac})")
        
        return {
            "success": True,
            "message": "Device registered",
            "device": {
                "ip": stats.ip,
                "mac": stats.mac,
                "hostname": stats.hostname,
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Error registering device: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur enregistrement device: {str(e)}"
        )


@router.post("/sample", response_model=dict)
async def add_bandwidth_sample(
    mac: str,
    bytes_sent: int,
    bytes_received: int
) -> dict:
    """
    Ajoute un échantillon de bande passante
    
    Args:
        mac: Adresse MAC
        bytes_sent: Bytes envoyés
        bytes_received: Bytes reçus
        
    Returns:
        Confirmation
    """
    try:
        monitor = get_bandwidth_monitor()
        monitor.add_sample(mac, bytes_sent, bytes_received)
        
        return {
            "success": True,
            "message": "Sample added",
        }
    
    except Exception as e:
        logger.error(f"❌ Error adding sample: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur ajout sample: {str(e)}"
        )
