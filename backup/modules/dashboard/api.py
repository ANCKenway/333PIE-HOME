"""
🔥 API Routes Dashboard Ultra - avec Scanner Blindé
"""
from fastapi import APIRouter, HTTPException
import logging

from .service import UltraDashboardService

logger = logging.getLogger(__name__)
router = APIRouter()

# Instance globale du service ultra
dashboard_service = UltraDashboardService()

@router.get("/")
async def get_dashboard_data():
    """
    🏠 Récupère les données du dashboard (version simplifiée)
    """
    try:
        logger.info("🏠 Récupération données dashboard")
        data = dashboard_service.get_ultra_dashboard_data()
        
        return {
            "success": True,
            "message": "🏠 Dashboard chargé",
            "data": data
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur API dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur dashboard: {str(e)}")

@router.get("/status")
async def get_application_status():
    """
    ⚡ Statut rapide de l'application
    """
    try:
        return {
            "status": "🟢 online",
            "version": "3.0.0",
            "edition": "🔥 Ultra Blindé",
            "modules": {
                "dashboard": "🔥 ultra_loaded", 
                "network": "🔥 scanner_blindé",
                "devices": "✅ loaded",
                "core": "✅ loaded"
            },
            "features": [
                "Scanner Réseau Ultra Blindé",
                "Identification Maximale",
                "Dashboard Temps Réel", 
                "Monitoring Avancé"
            ],
            "scanner": {
                "type": "ultra_blindé",
                "techniques": ["nmap", "scapy", "arp", "banner", "os_detection"],
                "status": "ready"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur statut: {e}")
        return {
            "status": "🟡 degraded",
            "error": str(e)
        }

@router.get("/system")
async def get_system_overview():
    """
    🖥️ Vue d'ensemble système rapide
    """
    try:
        system_data = await dashboard_service._get_system_status_ultra()
        
        return {
            "status": "success",
            "data": system_data,
            "message": "Données système récupérées"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur système: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network")  
async def get_network_overview():
    """
    🌐 Vue d'ensemble réseau avec scanner ultra
    """
    try:
        network_data = await dashboard_service._get_network_overview()
        
        return {
            "status": "success", 
            "data": network_data,
            "message": f"🔥 {network_data.get('total_devices', 0)} appareils analysés"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur réseau: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics():
    """
    📊 Métriques de performance système
    """
    try:
        perf_data = await dashboard_service._get_performance_metrics()
        
        return {
            "status": "success",
            "data": perf_data,
            "message": "Métriques performance récupérées"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))