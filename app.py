"""
🏠 333HOME - Application FastAPI principale
Serveur moderne pour la gestion de parc informatique avec scanner réseau avancé
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import asyncio
import time
import json
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Modules selon architecture RULES.md
from modules.devices import DeviceManager, DeviceMonitor
from modules.network.scan_storage import get_scan_storage
from modules.network.network_history import get_network_history

# Instance globale du gestionnaire de devices
device_manager = DeviceManager(DATA_DIR)
device_monitor = DeviceMonitor()
scan_storage = get_scan_storage(DATA_DIR)
network_history = get_network_history(DATA_DIR)

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de l'app
app = FastAPI(
    title="333HOME",
    description="Système de domotique et gestion de parc informatique",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemins
BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"

# Scanner réseau selon architecture modulaire
from modules.network import NetworkScanner
network_scanner = NetworkScanner()

# ===== API ENDPOINTS DE BASE =====

@app.get("/api/status")
async def get_status():
    """Status de l'application avec format attendu par le JS"""
    import psutil
    
    return {
        "success": True,
        "data": {
            "app_name": "333HOME v2.0.0",
            "version": "2.0.0",
            "status": "running",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "scanner_available": True
        },
        "message": "Serveur opérationnel avec scanner réseau avancé"
    }

@app.get("/api/info")
async def get_info():
    """Informations détaillées du système"""
    import psutil
    import platform
    from datetime import datetime
    
    return {
        "success": True,
        "data": {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            },
            "resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "timestamp": datetime.now().isoformat(),
            "app_name": "333HOME v2.0.0",
            "app_version": "2.0.0"
        }
    }

@app.get("/api/devices")
async def get_devices():
    """Obtenir la liste des appareils configurés avec monitoring intelligent"""
    try:
        # Charger les appareils via le gestionnaire
        devices = device_manager.load_devices()
        
        # Monitoring intelligent: ping rapide + lookup MAC pour DHCP
        enriched_devices = await device_monitor.get_devices_with_status(devices)
        
        # Ajouter informations de monitoring
        for device in enriched_devices:
            if device.get('last_checked'):
                last_check_ago = int(time.time() - device['last_checked'])
                if last_check_ago < 60:
                    device["last_seen"] = f"Il y a {last_check_ago}s"
                elif last_check_ago < 3600:
                    device["last_seen"] = f"Il y a {last_check_ago//60}min"
                else:
                    device["last_seen"] = f"Il y a {last_check_ago//3600}h"
            else:
                device["last_seen"] = "Jamais vérifié"
        
        return {"success": True, "devices": enriched_devices}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des appareils: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.post("/api/devices")
async def add_device(device_data: dict):
    """Ajouter un nouvel appareil"""
    try:
        success = device_manager.add_device(device_data)
        if success:
            return {"success": True, "message": "Appareil ajouté"}
        else:
            return {"success": False, "message": "Appareil déjà existant"}
    except Exception as e:
        logger.error(f"Erreur ajout appareil: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.put("/api/devices/{device_id}")
async def update_device(device_id: str, updates: dict):
    """Mettre à jour un appareil"""
    try:
        success = device_manager.update_device(device_id, updates)
        if success:
            return {"success": True, "message": "Appareil mis à jour"}
        else:
            raise HTTPException(status_code=404, detail="Appareil non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour appareil: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str):
    """Supprimer un appareil"""
    try:
        success = device_manager.remove_device(device_id)
        if success:
            return {"success": True, "message": "Appareil supprimé"}
        else:
            raise HTTPException(status_code=404, detail="Appareil non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression appareil: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/monitoring/stats")
async def get_monitoring_stats():
    """Statistiques du monitoring en temps réel"""
    try:
        stats = device_monitor.get_monitoring_stats()
        device_stats = device_manager.get_stats()
        
        return {
            "success": True, 
            "monitoring": stats,
            "devices": device_stats
        }
    except Exception as e:
        logging.error(f"Erreur monitoring stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.post("/api/monitoring/clear-cache")
async def clear_monitoring_cache():
    """Vider le cache de monitoring"""
    try:
        device_monitor.clear_cache()
        return {"success": True, "message": "Cache vidé"}
    except Exception as e:
        logging.error(f"Erreur clear cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== ENDPOINTS SCANNER RÉSEAU =====

@app.get("/api/network/scan")
async def professional_network_scan():
    """🔥 SCANNER RÉSEAU PROFESSIONNEL COMPLET"""
    try:
        logger.info("🚀 Lancement scan professionnel")
        start_time = time.time()
        
        result = network_scanner.professional_network_scan()
        
        # Calculer la durée du scan
        scan_duration = time.time() - start_time
        
        # Sauvegarder le scan (ancien système)
        if result and 'devices' in result:
            success = scan_storage.save_scan_result(result['devices'], scan_duration)
            logger.info(f"Scan sauvegardé (legacy): {success}")
            
            # Nouveau système d'historique unifié
            try:
                changes = network_history.update_scan_results(result['devices'], scan_duration)
                logger.info(f"Historique unifié mis à jour: {changes}")
            except Exception as history_error:
                logger.error(f"Erreur historique spécifique: {history_error}")
                import traceback
                logger.error(f"Traceback historique: {traceback.format_exc()}")
        
        return {"success": True, "scan_results": result}
    except Exception as e:
        logger.error(f"Erreur scan professionnel: {e}")
        import traceback
        logger.error(f"Traceback complet: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/quick-scan")
async def quick_network_scan():
    """Scanner rapide du réseau local"""
    try:
        # Scan rapide de la plage réseau
        result = network_scanner.scan_network_range()
        return {"success": True, "devices": result}
    except Exception as e:
        logger.error(f"Erreur scan rapide: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/detailed-scan")
async def detailed_network_scan(target: str = None):
    """Scanner détaillé avec ports et services"""
    try:
        if target:
            result = network_scanner.scan_host_detailed(target)
        else:
            result = network_scanner.scan_network_detailed()
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Erreur scan détaillé: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/discovery")
async def network_discovery():
    """Découverte réseau avec identification"""
    try:
        from modules.network.device_identifier import DeviceIdentifier
        identifier = DeviceIdentifier()
        
        # Scan de base
        devices = network_scanner.scan_network_range()
        
        # Enrichissement avec identification
        enriched_devices = []
        for device in devices:
            if device.get('mac'):
                device_info = await identifier.identify_device(device['mac'])
                device.update(device_info)
            enriched_devices.append(device)
        
        return {"success": True, "devices": enriched_devices}
    except Exception as e:
        logger.error(f"Erreur discovery: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== ENDPOINTS HISTORIQUE SCANS =====

@app.get("/api/network/last-scan")
async def get_last_scan():
    """Récupérer le dernier scan effectué"""
    try:
        last_scan = scan_storage.get_last_scan()
        return {"success": True, "last_scan": last_scan}
    except Exception as e:
        logger.error(f"Erreur last scan: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/scan-history")
async def get_scan_history(limit: int = 10):
    """Récupérer l'historique des scans"""
    try:
        history = scan_storage.get_scan_history(limit)
        return {"success": True, "history": history}
    except Exception as e:
        logger.error(f"Erreur history: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/disconnected-devices")
async def get_disconnected_devices(limit: int = 20):
    """Récupérer les appareils récemment déconnectés"""
    try:
        disconnected = scan_storage.get_disconnected_devices(limit)
        return {"success": True, "disconnected_devices": disconnected}
    except Exception as e:
        logger.error(f"Erreur disconnected: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/scan-stats")
async def get_scan_stats():
    """Récupérer les statistiques des scans (NOUVEAU: historique unifié)"""
    try:
        # Nouvelles stats depuis l'historique unifié
        stats = network_history.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur scan stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== NOUVEAUX ENDPOINTS HISTORIQUE UNIFIÉ =====

@app.get("/api/network/devices-history")
async def get_devices_with_history():
    """Récupérer tous les appareils avec leur historique enrichi"""
    try:
        history_data = network_history.get_history()
        return {"success": True, "history": history_data}
    except Exception as e:
        logger.error(f"Erreur devices history: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/device-history/{mac}")
async def get_device_history(mac: str):
    """Récupérer l'historique détaillé d'un appareil spécifique via MAC"""
    try:
        device_data = network_history.get_device_by_mac(mac)
        if device_data:
            return {"success": True, "device": device_data}
        else:
            raise HTTPException(status_code=404, detail="Appareil non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur device history: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/recent-events")
async def get_recent_network_events(limit: int = 20):
    """Récupérer les événements réseau récents (connexions, déconnexions, changements)"""
    try:
        events = network_history.get_recent_events(limit)
        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"Erreur recent events: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/scan-stats-legacy")
async def get_scan_stats_legacy():
    """Récupérer les statistiques des scans (ancien système)"""
    try:
        stats = scan_storage.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur scan stats legacy: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    """Récupérer les statistiques des scans"""
    try:
        stats = scan_storage.get_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur scan stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@app.get("/api/network/stats")
async def network_stats():
    """Statistiques du scanner réseau"""
    try:
        stats = {
            "last_scan": network_scanner.last_scan_time,
            "total_scanned": len(network_scanner.scan_results),
            "scan_timeout": network_scanner.scan_timeout,
            "active_threads": network_scanner.max_threads
        }
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Erreur stats réseau: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

# ===== SERVEUR DE FICHIERS STATIQUES =====

# Vérifier et créer les répertoires si nécessaire
if not WEB_DIR.exists():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Monter les fichiers statiques
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def read_root():
    """Page d'accueil"""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        raise HTTPException(status_code=404, detail="Page d'accueil non trouvée")

@app.get("/{filename}")
async def serve_web_files(filename: str):
    """Servir les fichiers web (templates, etc.)"""
    file_path = WEB_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    else:
        raise HTTPException(status_code=404, detail="Fichier non trouvé")

# ===== GESTION DES ERREURS =====

from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Endpoint non trouvé",
            "detail": f"L'endpoint {request.url.path} n'existe pas"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Erreur interne: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Erreur interne du serveur",
            "detail": str(exc)
        }
    )

# ===== ÉVÉNEMENTS DE L'APPLICATION =====

@app.on_event("startup")
async def startup_event():
    """Actions au démarrage"""
    logger.info("🚀 Démarrage de 333HOME v2.0.0")
    logger.info(f"📁 Répertoire: {BASE_DIR}")
    logger.info(f"🌐 Interface web: {WEB_DIR}")
    logger.info("✅ Scanner réseau avancé disponible")

@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt"""
    logger.info("🛑 Arrêt de 333HOME")

# ===== FONCTION DE DÉMARRAGE =====

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Démarrer le serveur FastAPI"""
    logger.info(f"🌐 Serveur: http://{host}:{port}")
    logger.info("📖 Documentation API: http://localhost:8000/api/docs")
    logger.info("🔗 Interface: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    start_server(reload=True)